# Experimentos de reconstrução virtual de temperaturas

A avaliação principal usa nove sensores do QuestDB, no intervalo UTC
[10/06/2026 00:00, 26/07/2026 00:00), com médias de cinco minutos.
A matriz tem 13.248 janelas previstas e 12.892 completas. A divisão é
cronológica: 9.024 linhas para treinamento e 3.868 para teste.
A análise espacial usa seis desses sensores e as mesmas linhas.

## Ambiente

Ambiente verificado: Python 3.12.3. As versões diretas estão em
`requirements.txt`. Na raiz do repositório, para preparar outro ambiente:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r code/tcc/requirements.txt
.venv/bin/python -m ipykernel install --user --name temperature-monitoring
```

Selecione esse kernel no editor. Não é necessário recriar o ambiente
quando as dependências já estiverem instaladas.

## Ordem de execução

| Notebook | Entrada e função | Acesso externo |
|---|---|---|
| `01_exploracao_dados.ipynb` | Exploração Smartlab, inventário de 14 posições e diagnóstico | API nas células de autenticação/cadastro/coleta; CSVs em cache nas análises |
| `02_preprocessamento.ipynb` | Extrai o QuestDB, valida a grade e exporta as matrizes | Somente se não existir CSV ou se a atualização estiver ativada |
| `03_experimentos.ipynb` | Lê a matriz completa; compara métodos e quantidade de entradas | Não |
| `04_analise_espacial.ipynb` | Usa a matriz, configuração do 03, cadastro espacial e CSVs da API para inventário | Não |
| `05_umidade.ipynb` | Caracteriza UR e compara regressão linear com oito temperaturas ou oito temperaturas e oito umidades | QuestDB somente se faltar cache ou atualização ativada |
| `06_energia_exploratoria.ipynb` | Audita o campo energy e sobrepõe o trecho disponível às temperaturas | QuestDB somente se faltar cache ou atualização ativada |

Para reproduzir os resultados consolidados com as extrações presentes,
execute 02 → 03 → 04 → 05 → 06 e salve as saídas. No 02, mantenha
`ATUALIZAR_EXTRACAO = False` para reutilizar a extração congelada.
O 01 não é pré-requisito de uma nova consulta para essa reprodução:
seus metadados e CSVs necessários ao 04 já estão preservados localmente.
Uma execução integral do 01 exige acesso à API; use-a apenas para renovar
a exploração. Os caminhos dos notebooks consolidados são resolvidos
pela raiz do projeto, independentemente da pasta de execução.

## Autenticação opcional da Smartlab

O 01 e o exploratório `../novo.ipynb` leem `SMARTLAB_USERNAME` e
`SMARTLAB_PASSWORD` do ambiente ou solicitam usuário e senha sem exibir
a senha na tela. Não escreva credenciais no notebook ou em arquivos
versionados. O código não carrega `.env` automaticamente.

## Dados, coordenadas e geometria

- `data/raw/questdb/`: extração agregada, SQL e metadados da consulta.
- `data/raw/smartlab/`: respostas CSV da coleta exploratória.
- `data/processed/`: matrizes QuestDB e contagens por janela.
- `data/metadata/`: inventário e auditorias de pré-processamento.
- `../sensorsWithCoordinates`: cadastro espacial confirmado, lido sem executar código.
- `results/experimentos/`: métricas e previsões dos nove alvos.
- `results/espacial/`: métricas espaciais, rankings, previsões e mapa.

O fuso e a resolução efetiva da Smartlab não estão equiparados ao
QuestDB. A disponibilidade nominal do 01 é calculada após reamostragem
na grade completa, sem afirmar equivalência temporal entre fontes.
A média de `avg_value` nessa reamostragem é exploratória, porque a API
não fornece as contagens subjacentes. Não se usa essa matriz na avaliação
principal ou espacial.

As categorias cadastrais 1006, Cluster e Reunião não definem sozinhas
barreiras físicas. A divisória e a abertura do mapa são aproximações da
planta fornecida. O mapa mostra médias de 12.892 janelas, não uma condição
instantânea; o fundo IDW é ilustrativo e exclui o cluster. Os círculos
sem preenchimento apenas indicam posições sem temperatura nesse mapa.

## Conferência e atualização do texto

Na raiz do projeto:

```bash
.venv/bin/python code/tcc/verificar_resultados.py
python3 thesis/scripts/exportar_resultados.py
make -C thesis/paper
```

A conferência recalcula MAE, RMSE e R² a partir das previsões salvas,
verifica hashes, timestamps e as métricas resumidas. Não treina modelos
nem consulta servidores. Os fontes atuais do Overleaf estão em `thesis/paper/`, com entrada
`thesis.tex` e compilação pdfLaTeX. O PDF de referência em
`thesis/TCC_GustavoMoura.pdf` não é sobrescrito. A exportação é opcional
e regrava os artefatos dos fontes locais. O exportador atualiza tabelas e figuras do
LaTeX; números nos parágrafos precisam ser conferidos se os dados mudarem.

Os notebooks `../final.ipynb`, `../main2.ipynb` e `../novo.ipynb` são
registros exploratórios. O `final` também contém outra busca com divisão
60%/20%/20%, que não é a avaliação consolidada do texto. Preserve esses
arquivos, mas não combine métricas de protocolos diferentes.

## Extensões de umidade e energia

A extração complementar está em `data/raw/questdb/complementares/`, com SQL,
CSV e hashes produzidos por `apoio_consultas.py`. A consulta inicial de
inventário também está preservada em JSON; sua conversão para CSV mantém
referência e hash da resposta original. Não renove os snapshots apenas para
reproduzir as métricas: `ATUALIZAR = False` é o padrão.

No 05, o alvo não fornece temperatura nem umidade às entradas. Cada par de
variantes usa os mesmos timestamps, preservando a fronteira temporal do 03.
As duas janelas de umidade ausentes afetam oito alvos no teste. A referência
com somente temperaturas foi reajustada nesse subconjunto; não compare
seu erro diretamente com a Random Forest do 03 como se todas as amostras
fossem idênticas. Resultados: `results/umidade/`.

No 06, só há sensor 23 e 539 janelas válidas no período consultado. O ACS712
é identificado pelo fabricante como sensor de corrente, mas a conversão
realizada pelo firmware para o campo `energy` não foi confirmada. Os valores
não são chamados de kWh, W ou A; não se calcula consumo, economia ou estado
do ar-condicionado. Resultados: `results/energia/`.
