# Monografia — ICMC/USP

**Reconstrução virtual de temperaturas a partir de sensores IoT no LASDPC**

Autor: Gustavo Moura Scarenci de Carvalho Ferreira.
Orientador: Prof. Dr. Júlio Cezar Estrella.
Disciplina: SSC0670 — Projeto de Formatura I.

A identificação está em `metadata.tex`. O título reflete o recorte efetivamente
avaliado: reconstrução de temperaturas, sem experimentos de umidade ou índices
de conforto. O documento usa a classe `packages/monografias.cls`, adaptada do
modelo fornecido em `../pdf_template/Monografias.v2026.pdf`.

## Conteúdo

- Introdução: contexto, objetivos e organização dos capítulos.
- Revisão bibliográfica: conceitos, métodos e trabalhos relacionados.
- Desenvolvimento: infraestrutura, metodologia, resultados e limitações.
- Conclusão: síntese das evidências e continuidade do trabalho.

Resumo e referências são incluídos em `main.tex`. O capítulo de desenvolvimento
inclui `sections/metodologia.tex` e `sections/resultados.tex`. A classe anterior
`packages/icmc.cls` foi preservada como legado e não é carregada.

O modelo utiliza A4, margens superior/esquerda de 3 cm e inferior/direita de
2 cm, Times New Roman 12 pt e espaçamento 1,5, com Arial nos títulos. O resumo
é um parágrafo com espaçamento duplo. As legendas ficam acima de tabelas e
figuras, com fonte abaixo. As referências usam `abntex2cite`.
O modelo recomenda cerca de 30 páginas; essa recomendação não é limite automático.

## Compilação

Requisitos: LuaLaTeX, latexmk, BibTeX, fontes Times New Roman e Arial.
Pacotes TeX necessários em Ubuntu/Debian:

```bash
sudo apt install latexmk texlive-luatex texlive-latex-recommended \
  texlive-latex-extra texlive-publishers texlive-lang-portuguese
```

As fontes Microsoft precisam ser instaladas separadamente, respeitando sua
licença. Na raiz do projeto:

```bash
make -C thesis/paper
```

Saída: `thesis/paper/build/main.pdf`. O LuaLaTeX precisa de um diretório de
cache de fontes gravável pelo usuário. Para limpar os arquivos de compilação:

```bash
make -C thesis/paper clean
```

## Resultados e rastreabilidade

O procedimento completo está em [code/tcc/README.md](../../code/tcc/README.md).
Os notebooks 02 e 03 produzem a comparação principal de nove sensores; o 04
compara regras de seleção entre seis sensores e gera o mapa das médias.
O notebook 05 acrescenta a caracterização e o experimento pareado de umidade;
o 06 apresenta a auditoria exploratória de energia.
A exploração Smartlab é separada dos experimentos do QuestDB.

Para conferir os artefatos e atualizar as tabelas/figuras:

```bash
.venv/bin/python code/tcc/verificar_resultados.py
python3 thesis/paper/scripts/exportar_resultados.py
make -C thesis/paper
```

O exportador usa a biblioteca padrão do Python. As tabelas em `tables/` e as
figuras em `figures/` são cópias próprias para o LaTeX. Se a extração ou os
experimentos mudarem, também é necessário conferir os números nos parágrafos.

A conferência bibliográfica e editorial está em `REVISAO.md`.
A correspondência com `thesis/propose.pdf` e os pontos de validação acadêmica
estão em `ALINHAMENTO_PROPOSTA.md`. Os hashes dos
arquivos consolidados podem ser regenerados com:

```bash
python3 code/tcc/gerar_manifesto.py
```

## Overleaf

Envie o conteúdo de `thesis/paper/`, sem `build/`, selecione `main.tex` e
LuaLaTeX. As fontes Times New Roman e Arial precisam estar disponíveis;
se necessário, forneça arquivos de fonte licenciados e adapte sua declaração
na classe. Não é necessário enviar os dados ou notebooks para compilar o texto.
