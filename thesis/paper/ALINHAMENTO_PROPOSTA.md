# Alinhamento entre a proposta registrada e a monografia

Documento de referência: `thesis/propose.pdf`.

**Título registrado:** Enriquecimento de Dados de Sensores IoT para Aprendizado
de Máquina focado em Conforto Térmico no LASDPC.

**Título utilizado na monografia:** Reconstrução virtual de temperaturas a
partir de sensores IoT no LASDPC.

O segundo título descreve a execução consolidada. O ajuste editorial e a
delimitação do objetivo ainda precisam ser validados academicamente pelo
orientador; a revisão dos arquivos não constitui aprovação dessa mudança.

## Correspondência com a execução

| Atividade da proposta | Situação na monografia | Evidência |
|---|---|---|
| Coleta, limpeza e estruturação | Executada | Extrações e matrizes do notebook 02 |
| Mapeamento e coordenadas | Executado para o cadastro disponível | `sensorsWithCoordinates`, inventário do 01 e análise do 04 |
| Aprendizado de máquina | Executado para reconstruir temperatura | Regressão linear e Random Forest no 03; regressões no 04 e 05 |
| Enriquecimento com localização | Executado como associação de metadados, seleção e visualização | Coordenadas orientam distância e mapa; não são colunas dos regressores por alvo |
| Enriquecimento com outra grandeza | Executado com umidade | Comparação pareada entre oito temperaturas e oito temperaturas + oito umidades no 05 |
| Estados da climatização | Não inferidos | Campo energy auditado no 06, com unidade ainda não confirmada |
| Fontes externas | Não integradas | Recorte restrito às extrações locais documentadas |
| Gradiente térmico | Não validado como campo contínuo | Mapa de médias por IDW apenas ilustrativo, limitado ao domínio |
| Inferência de conforto térmico | Não executada | Não há protocolo de conforto, variáveis completas ou votos dos ocupantes |
| Base para controle automatizado | Possibilidade futura | Não há controlador desenvolvido ou validado neste TCC |

## Como o texto explicita o recorte

A introdução apresenta a evolução do escopo. A revisão diferencia aprendizado
supervisionado, enriquecimento, sensoriamento virtual e conforto. A metodologia
descreve separadamente o uso do cadastro espacial e a inclusão de umidade nas
entradas. A conclusão se refere ao objetivo delimitado, sem afirmar cumprimento
integral da proposta de inferência de conforto.

A apresentação institucional da ASHRAE relaciona temperatura, radiação térmica,
umidade, velocidade do ar, atividade e vestimenta. A base utilizada não inclui
caracterização de todas essas variáveis, nem avaliação subjetiva dos ocupantes.
Não foram adotados valores arbitrários para produzir índices aparentes de conforto.
Fonte: https://www.ashrae.org/technical-resources/bookstore/standard-55-thermal-environmental-conditions-for-human-occupancy

## Novo trabalho relacionado

O PDF `thesis/relatedPapers/3748522.3779987.pdf` corresponde a Tavoni et al.
(2026), *Modular Digital Twin Architecture for Smart Building Energy Optimization:
A Open-Source Approach*, SAC '26, DOI 10.1145/3748522.3779987.

O artigo foi lido integralmente. A revisão destaca integração de dados,
XGBoost, variáveis históricas e TimeSeriesSplit. Distingue previsão de consumo
em um gêmeo digital da reconstrução contemporânea de temperatura neste TCC.
Também registra que o SCT-013 citado no artigo difere do ACS712 identificado
na nossa extração; não foi transferida a unidade kWh do artigo para o banco.
Nenhum resultado de energia ou simulação dos autores foi apresentado como
resultado deste TCC.

## Pontos para avaliação do orientador

1. Aceitação do recorte em sensoriamento virtual e enriquecimento, mantendo
   conforto como motivação e continuidade.
2. Adequação do título da monografia ao título registrado na proposta.
3. Caso a inferência de conforto seja exigida nesta etapa, definição prévia
   de critérios, variáveis e validação, antes de acrescentar resultados.

Este documento prepara essa discussão; não houve envio de mensagem ou
validação externa do escopo por meio desta revisão.
