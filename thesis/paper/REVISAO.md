# Revisão da versão consolidada

Revisão realizada em 30/10/2026. Este registro documenta a conferência técnica
e editorial; não substitui a avaliação acadêmica do orientador.

## Identificação e estrutura

- Autor e orientador preenchidos conforme o contexto fornecido.
- Título ajustado ao recorte real: reconstrução virtual de temperaturas.
- SSC0670 identificada como **Projeto de Formatura I**, conforme
  [Júpiter Web](https://portalservicos.usp.br/jupiterweb/obterDisciplina?codcur=97001&codhab=0&sgldis=SSC0670).
- Organização da introdução alinhada aos quatro capítulos.
- Objetivos específicos apresentados como lista; não foram acrescentados
  experimentos de conforto térmico, umidade ou climatização.
- Descrição da infraestrutura reduzida para evitar repetir a introdução.
- Equações de média, regressão e erro referenciadas na metodologia, sem duplicação.
- Categorias cadastrais diferenciadas de regiões físicas e divisórias.
- Modelo local conferido: `../pdf_template/Monografias.v2026.pdf`.

## Conferência bibliográfica

Os seis artigos originais foram conferidos pelos PDFs em `../relatedPapers/`.

| Chave | Evidência conferida |
|---|---|
| `marques2026testbed` | Título, autores, DOI e páginas 393–399 no PDF; o resumo relata redução de energia de 55,7% no cenário dos autores. Esse número não é resultado deste TCC. |
| `brunello2021virtual` | Sensoriamento virtual em escritório, métricas espaciais/estatísticas e seleção de sensores, com programação genética e comparação de métodos. Autores, DOI, volume 21 e artigo 2728 conferidos no PDF. |
| `yuan2025optimization` | Reconstrução numérica estacionária/transiente, posicionamento de sensores e métodos POD. Autores, DOI, volume 25 e artigo 4984 conferidos. |
| `jedermann2011interpolation` | O PDF relata comparação entre Kriging e IDW, com erro de interpolação cerca de 20% menor para Kriging nos dados dos autores. Evento e páginas completados por fonte do projeto de pesquisa. |
| `alsalehy2025timeseries` | Métodos estatísticos e detecção de anomalias; interpolação linear, PCHIP e Akima. Autores, DOI, volume 8 e artigo 82 conferidos. |
| `cho2022preprocessing` | Pré-processamento, valores ausentes e desbalanceamento em classificação industrial. Contexto distinto explicitado; autores, DOI, volume 11 e artigo 477 conferidos. |

A referência de Jedermann foi completada com **2011 IEEE SENSORS Proceedings**,
Limerick, IEEE, páginas **778–781**, conforme a
[lista de publicações do projeto na Universidade de Bremen](https://www.icia.uni-bremen.de/en/publications.html).
A página do [repositório UPM](https://oa.upm.es/10451/) registra a publicação
em janeiro de 2012 e o evento em 2011; foi mantido 2011, coerente com o PDF e
a bibliografia do projeto dos autores. O DOI não foi acrescentado por não ter
sido confirmado diretamente em uma fonte primária acessível nesta revisão.

Duas referências foram acrescentadas para fundamentar método e implementação:

- Breiman, *Random Forests*, Machine Learning 45, 5–32, 2001:
  [editora](https://doi.org/10.1023/A:1010933404324).
- Pedregosa et al., *Scikit-learn: Machine Learning in Python*, JMLR 12,
  2825–2830, 2011: [periódico](https://www.jmlr.org/papers/v12/pedregosa11a.html).

Os identificadores dos artigos MDPI foram registrados como números de artigo,
sem apresentá-los como páginas. Todas as entradas bibliográficas são citadas. A compilação usa o estilo
ABNT já presente no modelo; a conferência bibliográfica não equivale a uma
certificação formal de conformidade com todas as normas institucionais.

## Experimentos e disponibilidade

- Protocolo principal: nove alvos, 9.024 linhas de treino e 3.868 de teste.
- Seleção por correlação calculada exclusivamente no treinamento.
- Comparação espacial: seis alvos, candidatos comuns e mesmos timestamps.
- Resultados por quantidade interpretados como descritivos; o menor erro
  observado no teste não é apresentado como seleção validada independentemente.
- Mapa de médias: os seis valores usam as mesmas 12.892 janelas; IDW ilustrativa
  e sem preenchimento no cluster. Não há validação de campo térmico contínuo.
- Diferenças de disponibilidade referem-se às extrações locais e consultas
  preservadas, não à totalidade dos servidores.
- A análise do notebook 01 foi recalculada dos CSVs locais: a disponibilidade
  conta janelas após agregação, sobre a grade nominal completa. O fuso da API
  e a ponderação das médias continuam explicitamente pendentes de equiparação;
  essa matriz não participa dos experimentos do QuestDB.
- Credenciais literais removidas do 01 e do notebook exploratório `novo`.
  As células de autenticação foram deixadas sem saídas de execução; nenhuma
  nova autenticação foi necessária para a revisão.

## Reprodução e preservação

As versões diretas estão em `../../code/tcc/requirements.txt`; a ordem de
execução está em `../../code/tcc/README.md`. A conferência de métricas e
hashes pode ser repetida com `verificar_resultados.py`. Um manifesto de hashes
identifica a versão dos arquivos e dados consolidados, sem modificar o histórico
Git. Alterações e arquivos novos continuam disponíveis para revisão local;
a revisão não publica arquivos no GitHub.

As limitações científicas que permanecem são parte do escopo: uma divisão
temporal, ausência de referência calibrada e ausência de integração temporal
entre fontes. Não foram encobertas com novas suposições ou resultados.

## Resultado da verificação final

- PDF compilado com LuaLaTeX e BibTeX: 27 páginas no total.
- Revisão bibliográfica: quatro páginas; desenvolvimento: 14 páginas;
  conclusão: uma página. A introdução tem duas páginas; as extensões do
  modelo foram tratadas como recomendações editoriais, sem ampliar o texto
  artificialmente.
- Última compilação sem avisos de LaTeX, referências indefinidas,
  rótulos duplicados, linhas excedendo margens ou destinos PDF duplicados.
- Oito referências citadas e oito entradas cadastradas.
- Conferência das 27 avaliações principais e 60 espaciais concluída.
- Notebook 01 recalculado do cache, com disponibilidades nominais entre
  97,20% e 97,39%; essa medida ainda depende da convenção textual da API.
- Capa, resumo, conclusão, referências e páginas de figuras inspecionados.

## Extensão de 31/10/2026: umidade e energia

A auditoria inicial foi preservada antes de uma interrupção de disponibilidade
do servidor. Após o restabelecimento, os notebooks 05 e 06 foram executados
integralmente com extrações reais, sem modificar os resultados dos notebooks
03 e 04.

- Umidade: nove sensores, cobertura de 97,52% a 97,85% da grade; nenhuma
  janela retornada dos nove sensores foi excluída pelo critério [0,100].
- Comparação: 18 avaliações de regressão linear, sem temperatura ou umidade
  do alvo nas entradas. Foram preservadas 9.024 linhas de treinamento; o
  teste tem 3.868 linhas para o alvo 48 e 3.866 para os demais. As duas
  variantes usam amostras idênticas em cada alvo.
- MAE médio: 0,25667949 °C com temperaturas e 0,25342678 °C com temperaturas
  e umidades. A melhora é pequena, com cinco alvos melhores e quatro piores;
  não foi afirmada significância nem superioridade geral.
- Energia: sensor 23, 8.193 registros e 539 janelas válidas, apenas 4,07% da
  grade. Unidade do campo não confirmada; sem conversão, integração ou
  classificação ligada/desligada.
- Fontes técnicas acrescentadas: [manual Aosong AM2302](https://www.aosong.com/uploadfiles/2025/04/20250417105409216.pdf)
  para a grandeza UR e [fabricante Allegro ACS712](https://www.allegromicro.com/en/products/sense/current-sensor-ics/integrated-current-sensors/acs712)
  para identificar corrente. Nenhuma dessas fontes comprova a calibração ou
  a transformação aplicada pelo firmware do laboratório.
- A conclusão e o resumo foram atualizados; o título continua centrado em
  reconstrução de temperaturas. A contagem de referências passou de oito
  para dez. Os números de páginas do registro anterior descrevem a versão
  antes destas extensões.

### Verificação final da extensão

Os notebooks 05 e 06 estão salvos com todas as células executadas, sem
saídas de erro. A conferência das previsões confirmou as 18 métricas,
as máscaras de disponibilidade por alvo e a igualdade dos timestamps
entre variantes. O hash da extração de energia e suas 539 janelas também
foram conferidos. A compilação final tem 33 páginas, mantém a conclusão
em uma página e não apresenta avisos de LaTeX/BibTeX, referências pendentes
ou linhas excedendo as margens. As datas desconhecidas dos manuais foram
explicitadas como sem data, sem inferir o ano pelo endereço do arquivo.

## Alinhamento à proposta e novo trabalho relacionado

A proposta `thesis/propose.pdf` foi comparada à execução. A introdução agora
explicita a delimitação, sem declarar aprovação externa ou cumprimento de
inferência de conforto. A metodologia distingue estruturação, associação de
metadados espaciais e inclusão de umidade como entradas. A revisão explica
aprendizado supervisionado como a abordagem de IA efetivamente utilizada.

O novo PDF `3748522.3779987.pdf` foi lido integralmente e registrado sob a chave
`tavoni2026digitaltwin`, com os cinco autores na ordem do PDF, SAC '26,
três páginas e DOI 10.1145/3748522.3779987. A redação preserva “A Open-Source”
no título bibliográfico, como consta no original. Não foram inventados números
de página que não constam no PDF. A revisão relaciona integração de dados e
validação temporal, distinguindo resposta, algoritmo, sensores de corrente e
arquitetura da avaliação realizada neste TCC.

Foi acrescentada a página institucional da ASHRAE Standard 55 como referência
conceitual dos fatores de conforto; não se afirma avaliação de conformidade
com a norma ou leitura integral de um documento normativo não disponibilizado.
O trabalho não calcula índices de conforto com suposições não verificadas.
As referências passaram a doze, todas citadas. Os pontos de validação do
recorte e do título estão preparados em `ALINHAMENTO_PROPOSTA.md`.

A compilação após esse alinhamento contém 34 páginas, com a conclusão em
uma página. As doze referências foram conferidas contra as citações do texto;
não há rótulos duplicados, referências pendentes ou avisos de LaTeX/BibTeX.
As páginas de evolução do escopo, novo artigo e conclusão foram inspecionadas.
Os resultados experimentais permaneceram inalterados. O manifesto passou a
incluir também a proposta e os PDFs de trabalhos relacionados como fontes.
