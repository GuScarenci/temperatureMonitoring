"""Exporta os CSVs experimentais para tabelas LaTeX e copia figuras existentes.

Execute: python3 thesis/paper/scripts/exportar_resultados.py
Não consulta o banco nem ajusta modelos. Requer apenas a biblioteca padrão.
"""
import csv
import shutil
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
RESULTS = ROOT / 'code/tcc/results/experimentos'
TABLES = PAPER / 'tables'
FIGURES = PAPER / 'figures'
TABLES.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


def ler(path):
    with path.open(encoding='utf-8', newline='') as arquivo:
        return list(csv.DictReader(arquivo))


def numero(valor, casas=3):
    return f'{float(valor):.{casas}f}'.replace('.', ',')


def tabela(nome, cabecalho, linhas, alinhamento):
    texto = [r'\begin{tabular}{' + alinhamento + '}', r'\toprule',
             ' & '.join(cabecalho) + r' \\', r'\midrule']
    texto.extend(' & '.join(linha) + r' \\' for linha in linhas)
    texto.extend([r'\bottomrule', r'\end{tabular}', ''])
    (TABLES / nome).write_text('\n'.join(texto), encoding='utf-8')


resumo = ler(RESULTS / 'tabelas/resumo_modelos.csv')
nomes = {'Media': 'Média aritmética', 'Regressao Linear': 'Regressão linear',
         'Random Forest': 'Random Forest'}
tabela('modelos.tex', ['Método', 'MAE (°C)', 'RMSE (°C)', r'$R^2$'],
       [[nomes[r['metodo']], numero(r['MAE_medio']), numero(r['RMSE_medio']),
         numero(r['R2_medio'])] for r in resumo], 'lrrr')
metricas = ler(RESULTS / 'tabelas/metricas_por_sensor.csv')
ids = [1, 48, 887, 891, 86782, 86789, 86790, 86791, 86793]
linhas = []
for sensor in ids:
    grupo = {r['metodo']: r for r in metricas if int(r['sensor_alvo']) == sensor}
    linhas.append([str(sensor)] + [numero(grupo[m]['MAE']) for m in nomes])
tabela('mae_alvos.tex', ['Sensor-alvo', 'Média aritmética', 'Regressão linear',
                         'Random Forest'], linhas, 'rrrr')
quantidade = ler(RESULTS / 'tabelas/resumo_quantidade_sensores.csv')
tabela('quantidade.tex', [r'$k$', 'MAE (°C)', 'RMSE (°C)', r'$R^2$'],
       [[r['k'], numero(r['MAE_medio']), numero(r['RMSE_medio']),
         numero(r['R2_medio'])] for r in quantidade], 'rrrr')
cobertura = ler(ROOT / 'code/tcc/data/metadata/resumo_questdb_1006.csv')
tabela('sensores.tex', ['Sensor', 'Janelas válidas', 'Ausentes',
                         r'Cobertura (\%)', 'Média (°C)', 'Desvio (°C)'],
       [[r['sensor_id'], r['janelas_validas'], r['janelas_ausentes'],
         numero(r['cobertura_pct'], 2), numero(r['media_c']), numero(r['desvio_c'])]
        for r in cobertura], 'rrrrrr')
for nome in ['mae_por_sensor', 'erro_quantidade_sensores',
             'reconstrucao_sensor_891']:
    shutil.copy2(RESULTS / 'figuras' / f'{nome}.pdf', FIGURES / f'{nome}.pdf')
print('Quatro tabelas e três figuras exportadas para', PAPER)

# Análise complementar do notebook 04, quando executada.
ESPACIAL = ROOT / 'code/tcc/results/espacial'
if (ESPACIAL / 'configuracao_espacial.json').exists():
    resumo_espacial = ler(ESPACIAL / 'tabelas/resumo_selecao_espacial.csv')
    linhas = []
    for k in range(1, 6):
        grupo = {r['estrategia']: r for r in resumo_espacial if int(r['k']) == k}
        linhas.append([str(k)] + [numero(grupo[m][v]) for m in ['Correlacao', 'Proximidade']
                                  for v in ['MAE_medio', 'RMSE_medio']])
    tabela('selecao_espacial.tex', [r'$k$', 'MAE corr.', 'RMSE corr.', 'MAE prox.', 'RMSE prox.'],
           linhas, 'rrrrr')
    coord = ler(ESPACIAL / 'tabelas/temperaturas_mapa.csv')
    tabela('coordenadas.tex', ['Sensor', 'X relativo', 'Y relativo', 'Média (°C)'],
           [[r['sensor_id'], numero(r['x_aprox'], 1), numero(r['y_aprox'], 1),
             numero(r['media_c'])] for r in coord], 'rrrr')
    for nome in ['comparacao_selecao_espacial', 'mapa_termico_1006_painel']:
        shutil.copy2(ESPACIAL / 'figuras' / f'{nome}.pdf', FIGURES / f'{nome}.pdf')
    print('Duas tabelas e duas figuras espaciais exportadas.')

UMIDADE = ROOT / 'code/tcc/results/umidade'
ENERGIA = ROOT / 'code/tcc/results/energia'
if (UMIDADE / 'configuracao_umidade.json').exists():
    umidade = ler(UMIDADE / 'tabelas/resumo_umidade.csv')
    tabela('umidade_sensores.tex', ['Sensor', r'Janelas', r'Cobertura (\%)',
                                  r'Média (\%)', 'Desvio (p.p.)'],
           [[r['sensor_id'], r['janelas_validas'], numero(r['cobertura_pct'], 2),
             numero(r['media_ur_pct'], 2), numero(r['desvio_ur_pp'], 2)] for r in umidade], 'rrrrr')
    modelos_h = ler(UMIDADE / 'tabelas/resumo_enriquecimento.csv')
    tabela('enriquecimento_umidade.tex', ['Entradas', 'MAE (°C)', 'RMSE (°C)', r'$R^2$'],
           [[r['variante'], numero(r['MAE_medio'], 5), numero(r['RMSE_medio'], 5),
             numero(r['R2_medio'], 3)] for r in modelos_h], 'lrrr')
    delta_h = ler(UMIDADE / 'tabelas/delta_mae_por_alvo.csv')
    tabela('umidade_por_alvo.tex', ['Sensor', 'Somente T (°C)', 'T e UR (°C)', r'$\Delta$ MAE (°C)'],
           [[r['sensor_alvo'], numero(r['Temperaturas'], 3),
             numero(r['Temperaturas e umidades'], 3), numero(r['delta_MAE_mais_umidade'], 3)]
            for r in delta_h], 'rrrr')
    for nome in ['caracterizacao_umidade', 'efeito_umidade']:
        shutil.copy2(UMIDADE / 'figuras' / f'{nome}.pdf', FIGURES / f'{nome}.pdf')
    print('Três tabelas e duas figuras de umidade exportadas.')
if (ENERGIA / 'configuracao_energia.json').exists():
    shutil.copy2(ENERGIA / 'figuras/energia_temperatura_exploratoria.pdf',
                 FIGURES / 'energia_temperatura_exploratoria.pdf')
    print('Figura exploratória de energia exportada.')
