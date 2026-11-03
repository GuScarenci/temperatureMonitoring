"""Cache auditável para consultas complementares de leitura no QuestDB."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

import pandas as pd
import requests

URL = 'http://andromeda.lasdpc.icmc.usp.br:61102/questdb/exec'


def consultar_cache(sql, arquivo, atualizar=False):
    """Salva CSV, SQL e metadados; reutiliza o snapshot se íntegro e compatível."""
    arquivo = Path(arquivo)
    meta_file, sql_file = arquivo.with_suffix('.json'), arquivo.with_suffix('.sql')
    if arquivo.exists() and not atualizar:
        if not meta_file.exists() or not sql_file.exists():
            raise ValueError(f'Cache sem metadados: {arquivo}')
        meta = json.loads(meta_file.read_text())
        if meta['sql'] != sql or hashlib.sha256(arquivo.read_bytes()).hexdigest() != meta['sha256_csv']:
            raise ValueError(f'Cache incompatível ou alterado: {arquivo}')
        return pd.read_csv(arquivo)
    try:
        resposta = requests.get(URL, params={'query': sql, 'limit': '0,200000'}, timeout=(15, 150))
        resposta.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f'Não foi possível consultar o QuestDB e falta a extração local {arquivo.name}. '
            'Reexecute quando o servidor estiver acessível; nenhum resultado foi simulado.'
        ) from exc
    dados = resposta.json()
    if 'error' in dados:
        raise RuntimeError(dados['error'])
    if not {'columns', 'dataset'}.issubset(dados):
        raise ValueError('Resposta sem columns/dataset.')
    if dados.get('count', len(dados['dataset'])) > len(dados['dataset']) or len(dados['dataset']) >= 200000:
        raise ValueError('Possível truncamento da resposta; reduzir ou paginar a consulta.')
    df = pd.DataFrame(dados['dataset'], columns=[c['name'] for c in dados['columns']])
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(arquivo, index=False)
    sql_file.write_text(sql, encoding='utf-8')
    meta_file.write_text(json.dumps({
        'extraido_em_utc': datetime.now(timezone.utc).isoformat(), 'endpoint': URL,
        'sql': sql, 'linhas': len(df),
        'sha256_csv': hashlib.sha256(arquivo.read_bytes()).hexdigest(),
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    return df
