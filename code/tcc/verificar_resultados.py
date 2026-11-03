"""Confere os artefatos experimentais sem treinar modelos ou acessar a rede."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def hash_arquivo(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def conferir_grupos(previsoes, metricas, chaves, real, estimada, nomes):
    referencia_temporal = None
    total = 0
    for chave, grupo in previsoes.groupby(chaves, sort=True):
        valores = chave if isinstance(chave, tuple) else (chave,)
        filtro = pd.Series(True, index=metricas.index)
        for coluna, valor in zip(chaves, valores):
            filtro &= metricas[coluna].eq(valor)
        linha = metricas.loc[filtro]
        assert len(linha) == 1, (chave, 'métrica ausente ou duplicada')
        linha = linha.iloc[0]
        tempos = tuple(grupo.timestamp)
        assert len(tempos) == int(linha.n_teste)
        assert len(set(tempos)) == len(tempos)
        if referencia_temporal is None:
            referencia_temporal = tempos
        assert tempos == referencia_temporal, 'Amostras de teste diferentes entre grupos'
        assert np.isfinite(grupo[[real, estimada]].to_numpy()).all()
        medidas = [mean_absolute_error(grupo[real], grupo[estimada]),
                   np.sqrt(mean_squared_error(grupo[real], grupo[estimada])),
                   r2_score(grupo[real], grupo[estimada])]
        np.testing.assert_allclose(medidas, linha[nomes].astype(float).to_numpy(),
                                   rtol=1e-9, atol=1e-10)
        total += 1
    assert total == len(metricas)
    return referencia_temporal


config = json.loads((BASE / 'results/experimentos/configuracao_execucao.json').read_text())
dados_file = ROOT / config['arquivo_dados']
assert hash_arquivo(dados_file) == config['sha256_dados']
dados = pd.read_csv(dados_file, index_col='timestamp')
assert len(dados) == config['n_treino'] + config['n_teste']
assert np.isfinite(dados.to_numpy()).all()
prev = pd.read_csv(BASE / 'results/experimentos/previsoes_teste.csv')
met = pd.read_csv(BASE / 'results/experimentos/tabelas/metricas_por_sensor.csv')
tempos = conferir_grupos(prev, met, ['sensor_alvo', 'metodo'],
                        'temperatura_real', 'temperatura_estimada', ['MAE', 'RMSE', 'R2'])
esperados = pd.to_datetime(dados.index[config['n_treino']:], utc=True)
assert pd.DatetimeIndex(pd.to_datetime(tempos, utc=True)).equals(esperados)
for alvo, grupo in prev.groupby('sensor_alvo'):
    valores = dados.loc[list(tempos), str(alvo)].to_numpy()
    for _, sub in grupo.groupby('metodo'):
        np.testing.assert_allclose(sub.temperatura_real, valores, atol=1e-10)
resumo = pd.read_csv(BASE / 'results/experimentos/tabelas/resumo_modelos.csv').set_index('metodo')
for metodo, grupo in met.groupby('metodo'):
    for coluna, nome in [('MAE', 'MAE_medio'), ('RMSE', 'RMSE_medio'), ('R2', 'R2_medio')]:
        assert np.isclose(grupo[coluna].mean(), resumo.loc[metodo, nome], atol=1e-10)

esp = BASE / 'results/espacial'
cfg = json.loads((esp / 'configuracao_espacial.json').read_text())
assert cfg['sha256_dados'] == config['sha256_dados']
assert cfg['sha256_coordenadas'] == hash_arquivo(ROOT / 'code/sensorsWithCoordinates')
prev_e = pd.read_csv(esp / 'previsoes_espaciais.csv.gz')
met_e = pd.read_csv(esp / 'tabelas/metricas_espaciais_por_alvo.csv')
tempos_e = conferir_grupos(prev_e, met_e, ['sensor_alvo', 'estrategia', 'k'],
                          'real', 'estimada', ['MAE', 'RMSE', 'R2'])
assert tempos == tempos_e
for _, linha in met_e.iterrows():
    entradas = json.loads(linha.sensores_entrada)
    assert linha.sensor_alvo not in entradas
    assert len(entradas) == linha.k
    assert set(entradas).issubset(cfg['ids'])
for nome in ['MAE', 'RMSE', 'R2']:
    completos = met_e[met_e.k == 5].pivot(index='sensor_alvo', columns='estrategia', values=nome)
    np.testing.assert_allclose(completos.Correlacao, completos.Proximidade, atol=1e-9)
mapa = np.load(esp / 'grade_idw_media.npz')
cluster = ((mapa['x'] <= cfg['mapa']['parede_vertical_x_aprox']) &
           (mapa['y'] > cfg['mapa']['divisoria_y_aprox']))
assert not np.isfinite(mapa['temperatura'][cluster]).any()
print('OK: hashes, referência física, amostras comuns, 27 avaliações principais,')
print('60 avaliações espaciais, exclusão do alvo, métricas e máscara do mapa.')

# As extensões foram executadas em 31/10/2026; as amostras são pareadas por alvo.
umidade_dir = BASE / 'results/umidade'
if (umidade_dir / 'configuracao_umidade.json').exists():
    cfg_h = json.loads((umidade_dir / 'configuracao_umidade.json').read_text())
    assert cfg_h['sha256_temperatura'] == config['sha256_dados']
    h_file = BASE / 'data/raw/questdb/complementares/umidade_1006_5min.csv'
    assert hash_arquivo(h_file) == cfg_h['sha256_extracao_umidade']
    ph = pd.read_csv(umidade_dir / 'previsoes_enriquecimento.csv.gz')
    mh = pd.read_csv(umidade_dir / 'tabelas/metricas_enriquecimento.csv')
    assert len(mh) == 18
    for alvo, grupo in ph.groupby('sensor_alvo'):
        subset_m = mh[mh.sensor_alvo == alvo]
        t = conferir_grupos(grupo, subset_m, ['sensor_alvo', 'variante'],
                            'real', 'estimada', ['MAE', 'RMSE', 'R2'])
        assert set(t).issubset(tempos)
        for _, sub in grupo.groupby('variante'):
            np.testing.assert_allclose(sub.real, dados.loc[list(t), str(alvo)], atol=1e-10)
    h_matrix = pd.read_csv(BASE / 'data/processed/umidade_1006_5min.csv', index_col='timestamp')
    h_matrix.index = pd.to_datetime(h_matrix.index, utc=True)
    temp_index = pd.to_datetime(dados.index, utc=True)
    corte_h = pd.Timestamp(cfg_h['inicio_teste_utc'])
    for _, row in mh.iterrows():
        entradas = json.loads(row.sensores_entrada)
        assert row.sensor_alvo not in entradas and len(entradas) == 8
        h_entradas = h_matrix.reindex(temp_index)[[str(s) for s in entradas]]
        validos = h_entradas.notna().all(axis=1)
        assert ((temp_index < corte_h) & validos).sum() == row.n_treino
        assert ((temp_index >= corte_h) & validos).sum() == row.n_teste
        esperadas_h = temp_index[(temp_index >= corte_h) & validos]
        g = ph[(ph.sensor_alvo == row.sensor_alvo) & (ph.variante == row.variante)]
        assert pd.DatetimeIndex(pd.to_datetime(g.timestamp, utc=True)).equals(esperadas_h)
    resumo_h = pd.read_csv(umidade_dir / 'tabelas/resumo_enriquecimento.csv').set_index('variante')
    for variante, g in mh.groupby('variante'):
        for m, nome in [('MAE', 'MAE_medio'), ('RMSE', 'RMSE_medio'), ('R2', 'R2_medio')]:
            assert np.isclose(g[m].mean(), resumo_h.loc[variante, nome], atol=1e-10)
    print('OK: 18 avaliações com umidade, máscaras por alvo, exclusão do alvo e comparação pareada.')

energia_dir = BASE / 'results/energia'
if (energia_dir / 'configuracao_energia.json').exists():
    cfg_e = json.loads((energia_dir / 'configuracao_energia.json').read_text())
    assert hash_arquivo(BASE / 'data/raw/questdb/complementares/energia_1006_5min.csv') == cfg_e['sha256_extracao']
    e = pd.read_csv(BASE / 'data/processed/energia_1006_5min.csv', index_col='timestamp')
    resumo_e = pd.read_csv(energia_dir / 'tabelas/resumo_energia.csv')
    assert len(e) == 13248 and e.notna().sum().sum() == 539
    assert np.isclose(resumo_e.cobertura_pct.iloc[0], 100 * 539 / 13248)
    assert not cfg_e['conversao_para_consumo']
    print('OK: hash, 539 janelas e escala não convertida do campo energy.')
