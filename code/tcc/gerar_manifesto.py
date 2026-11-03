"""Registra hashes da versão local consolidada, sem modificar o Git."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'code/tcc'
ARQUIVO = BASE / 'manifesto_reproducao.json'
paths = set()
for pasta in [BASE, ROOT / 'thesis']:
    for p in pasta.rglob('*'):
        if not p.is_file() or p == ARQUIVO:
            continue
        relativos = p.relative_to(pasta).parts
        if any(x in {'build', '__pycache__', '.ipynb_checkpoints'} for x in relativos):
            continue
        paths.add(p)
paths.update([ROOT / 'code/sensores.json', ROOT / 'code/sensorsWithCoordinates',
              ROOT / 'thesis/propose.pdf'])
paths.update((ROOT / 'thesis/relatedPapers').glob('*.pdf'))
linhas = []
for p in sorted(paths):
    digest = hashlib.sha256()
    with p.open('rb') as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b''):
            digest.update(bloco)
    linhas.append({'arquivo': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                   'sha256': digest.hexdigest()})
ARQUIVO.write_text(json.dumps({'gerado_em_utc': datetime.now(timezone.utc).isoformat(),
                               'arquivos': linhas}, ensure_ascii=False, indent=2) + '\n')
print(f'Manifesto salvo: {len(linhas)} arquivos.')
