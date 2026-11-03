# Avaliação do TCC e dos artefatos experimentais

Referência: `new_thesis/TCC_GustavoMoura_atualizado (5).pdf`, revisão de 02/11/2026. Avaliação baseada na leitura do texto extraído do PDF, inspeção dos fontes do ZIP sem alterá-lo, leitura dos notebooks e conferência dos dados locais. Não constitui validação acadêmica pelo orientador, revisão visual de todas as páginas ou auditoria externa das referências bibliográficas.

## Parecer geral

O trabalho apresenta uma investigação experimental coerente com o código consolidado em `code/tcc/`. O problema está delimitado, a comparação inclui uma referência simples e as conclusões reconhecem limites importantes. A contribuição está na preparação rastreável de dados reais e na avaliação da reconstrução contemporânea de sensores, com análises complementares de seleção e umidade.

Não identifiquei divergência nos resultados centrais conferidos entre o PDF, as configurações e as tabelas. Não há motivo identificado nesta revisão para alterar os modelos ou recalcular a entrega. Os principais pontos a resolver são de apresentação do repositório e preservação da versão acadêmica correta.

## Conferências realizadas

| Conferência | Evidência e resultado |
|---|---|
| Integridade do conjunto consolidado | Todos os 178 arquivos listados em `code/tcc/manifesto_reproducao.json` correspondiam aos hashes registrados |
| Avaliação principal | O verificador passou nas 27 combinações de nove alvos e três métodos; métricas recalculadas das previsões e timestamps compatíveis com a matriz |
| Avaliação espacial | O verificador passou nas 60 avaliações, na exclusão do alvo, nas amostras comuns, no hash das coordenadas e na máscara do cluster |
| Umidade | O verificador passou nas 18 avaliações, nas amostras pareadas por alvo, nas máscaras de disponibilidade e na exclusão de temperatura e umidade do alvo |
| Energia | Hash da extração, 539 janelas válidas e cobertura consistentes; configuração não converte os valores em consumo |
| Reprodução dos notebooks | Notebooks 02, 03, 04, 05 e 06 executados integralmente em cópia temporária, com caches preservados e opções de atualização desativadas |
| Comparação após reprodução | Resumo principal, 54 avaliações de quantidade, 60 avaliações espaciais e 18 avaliações de umidade compatíveis com os originais (`rtol=1e-9`, `atol=1e-10`); verificador também passou na cópia |

A reprodução utilizou o ambiente `.venv` já disponível. Não foi testada uma instalação nova das dependências. O notebook 01 e a disponibilidade dos serviços externos não foram testados. Os arquivos originais de dados, código e entrega foram preservados.

O script `verificar_resultados.py` **não verifica automaticamente todos os 178 hashes**: ele confere hashes específicos e relações experimentais. A comparação integral do manifesto foi realizada separadamente nesta revisão. O manifesto não abrange `new_thesis/` e não estabelece sozinho correspondência entre o PDF e cada artefato.

## Correspondência entre texto e código

| Tema | PDF | Implementação e observação |
|---|---|---|
| Fonte e período | Seções 3.3.2–3.3.3, pp. 27–28 | O 02 consulta o ambiente 1006 entre 10/06 e 26/07/2026, fim exclusivo, com `SAMPLE BY 5m` |
| Casos completos | Seções 3.3.3 e 3.4.1 | A grade tem 13.248 linhas; `dropna` mantém 12.892, sem imputação |
| Protocolo temporal | Seção 3.3.5, p. 28 | O 03 usa corte inteiro de 70%, sem embaralhamento: 9.024/3.868 amostras |
| Métodos | Seção 3.3.4, p. 28 | Média dos oito outros sensores, `LinearRegression` e `RandomForestRegressor` com 100 árvores e semente 42 |
| Comparação agregada | Tabela 3, p. 33 | MAE de 0,927298 / 0,256674 / 0,254268 °C; RMSE e R² também compatíveis com os arredondamentos do PDF |
| Quantidade de entradas | Tabela 5, p. 35 | O 03 avalia k = 1, 2, 3, 4, 6, 8; menor MAE médio observado em k = 4: 0,238224 °C |
| Seleção espacial | Seções 3.3.7 e 3.4.6 | O 04 mantém os mesmos instantes e compara critérios em seis alvos; correlação usa apenas treinamento |
| Umidade | Tabelas 9–10, pp. 40–41 | O 05 reajusta as duas variantes em amostras comuns por alvo, retirando também a umidade do alvo |
| Energia | Seção 3.4.9, pp. 41–42 | O 06 limita-se à disponibilidade e sobreposição; não estima consumo ou estados da climatização |

## Pontos fortes do conteúdo

- A introdução explica a evolução da proposta e distingue reconstrução de temperatura, conforto térmico e controle de climatização.
- O alvo fica fora das entradas e a seleção por correlação é feita no treinamento. A divisão cronológica é apropriada ao problema temporal apresentado.
- A avaliação por sensor mostra que o resultado agregado não vale igualmente para todos: a média simples vence em dois alvos.
- O texto reconhece que o menor erro com quatro entradas foi observado no teste. Não apresenta esse resultado como ótimo geral ou teste independente.
- A comparação com umidade preserva amostras pareadas e encontra efeitos pequenos e distintos entre alvos, sem prometer ganho uniforme.
- A interpretação da energia e do mapa é cuidadosa: não se atribuem unidades não confirmadas, causalidade, consumo ou validação de um campo térmico contínuo.

## Pontos a conferir antes da entrega

| Prioridade | Ponto | Encaminhamento sem alterar os experimentos |
|---|---|---|
| Alta | Duas árvores de fontes acadêmicos | O ZIP do Overleaf usa `thesis.tex` e a classe `packages/icmc`; `thesis/paper/` usa `main.tex` e outro fluxo. Identificar claramente a entrega atual e evitar sobrescrevê-la com o exportador antigo |
| Alta | Arquivos ainda não versionados | Na revisão, `code/tcc/` e `new_thesis/` apareciam como não rastreados no Git. Eles precisam integrar o commit e o envio ao GitHub para que o repositório citado no PDF contenha os artefatos |
| Média | Ano na capa e folha de rosto | A extração do PDF não mostra o ano nessas páginas, e o `metadata.tex` do ZIP não define `\data`. Conferir visualmente e validar a exigência com o modelo institucional; não foi corrigido |
| Média | Instrução antiga sobre umidade | O README de `thesis/paper/` ainda diz “sem experimentos de umidade”, embora descreva depois o notebook 05. Essa frase não deve ser usada para caracterizar a entrega atual |
| Média | Material de apoio público | Antes de publicar, confirmar a autorização de redistribuição dos PDFs de terceiros em `thesis/relatedPapers/`. A presença de uma referência bibliográfica não resolve essa autorização |
| Baixa | Identificação estável da versão | Após consolidar os arquivos, registrar commit ou tag associado ao PDF. Isso permite recuperar o estado efetivamente citado sem depender apenas do branch padrão |

O PDF atualizado permanece a referência de leitura. O README da raiz esclarece as diferenças entre as versões sem alterar fontes da monografia. Não foi criada licença para código, dados ou artigos: essa escolha depende dos direitos de seus titulares.

## Limitações metodológicas e efeito sobre as conclusões

**Diferença entre modelos.** O MAE médio da Random Forest supera o da regressão linear em aproximadamente 0,0024 °C. Sem intervalos ou avaliação em novos períodos, essa diferença deve permanecer descritiva. O texto já faz essa ressalva; o desempenho competitivo e a simplicidade da regressão linear são conclusões mais sustentadas que uma superioridade universal.

**Seleção após observar o teste.** Calcular correlações apenas no treinamento evita usar o teste no ranking, mas examinar vários valores de k no mesmo teste torna exploratória a escolha do melhor k. A avaliação independente dessa escolha exigiria validação temporal adicional e um teste final reservado. Isso é continuidade de pesquisa, não uma alteração recomendada para esta entrega.

**Disponibilidade das entradas.** Excluir janelas incompletas garante comparação comum, mas mede desempenho com entradas disponíveis. Não demonstra funcionamento durante falhas simultâneas. As contagens por janela variam, sem mínimo uniforme; a representatividade de cada média também pode variar.

**Reconstrução contemporânea.** As entradas e o alvo pertencem ao mesmo instante. O experimento não demonstra previsão de temperatura futura nem estima diretamente posições sem histórico de referência. O mapa de médias é uma visualização separada da avaliação supervisionada.

**Referência metrológica.** Os sensores físicos são a referência experimental; não há instrumento calibrado independente. Um MAE de 0,25 °C mede concordância com esses sensores, não exatidão absoluta do ambiente.

**Umidade e energia.** O ganho médio de umidade é aproximadamente 0,00325 °C e não é uniforme. O campo `energy` cobre cerca de 4,07% da grade, com unidade não confirmada. Os limites declarados no texto são compatíveis com esses dados.

## Avaliação do código e organização

Os notebooks consolidados mantêm parâmetros explícitos, validam estruturas e exportam previsões, métricas e configurações. O uso de caches e hashes favorece a rastreabilidade. Os notebooks antigos devem permanecer identificados como exploração: em particular, o protocolo 60%/20%/20% de `final.ipynb` não é o protocolo consolidado do PDF.

Há oportunidades para uma evolução futura: extrair funções repetidas dos notebooks, automatizar uma validação integral do manifesto e ampliar a conferência da análise de quantidade de entradas. Hoje suas 54 avaliações não são recalculadas pelo verificador a partir de previsões salvas próprias. Não é necessário refatorar esses códigos para organizar a entrega atual.

A organização adotada nesta revisão preserva caminhos, código, dados e manifesto, acrescentando uma entrada clara no README da raiz e esta avaliação. Não foram movidas pastas nem reescritos notebooks. O ZIP do Overleaf e o PDF atualizado foram mantidos intactos.
