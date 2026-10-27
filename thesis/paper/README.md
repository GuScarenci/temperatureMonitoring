# TCC em LaTeX — ICMC/USP

O documento principal continua sendo `main.tex`, compilado com pdfLaTeX.
A classe `packages/icmc.cls` e os logotipos em `images/` foram extraídos de
`TCC06_PEDRO_GUDIN_OVERLEAF_TEMPLATE_v0_1.zip`, fornecido para a adaptação
solicitada na issue #1. A classe mantém seu cabeçalho e licença LPPL originais.
O conteúdo do TCC de exemplo sobre máquina de café não foi importado.

## Conteúdo e dados pessoais

- Preencha título, autor, orientador, curso, área e data em `metadata.tex`.
- Confirme o curso e a disciplina: a classe fornecida contém um preâmbulo fixo
  para Engenharia de Computação / SSC0670. Alterar `\curso` não altera esse
  texto; use a substituição indicada em `metadata.tex` se necessário.
- Escreva o resumo em `main.tex`. A classe gera capa, folha de rosto, resumo
  e sumário automaticamente. As listas de figuras e tabelas são opcionais.
- Os textos existentes permanecem em `sections/`, agora como capítulos.
- Coloque figuras em `figures/`; preserve `images/`, usado pela capa.
- Cadastre referências em `references.bib`, cite com `\cite{chave}` e ative
  `\bibliography{references}` em `main.tex`. A classe configura citações ABNT.
  Nenhuma referência do TCC de exemplo foi adicionada.

Os campos pessoais e os textos ainda são placeholders. Confirme os requisitos
institucionais atuais antes da entrega; esta adaptação usa a classe fornecida
no ZIP, sem certificação independente de sua versão.

## Instalação (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install latexmk texlive-latex-recommended texlive-latex-extra \
  texlive-publishers texlive-science texlive-fonts-recommended \
  texlive-lang-portuguese
```

`texlive-publishers` fornece `abntex2`; os demais pacotes atendem às
dependências da classe, incluindo `algorithm2e`, `morewrites` e fontes.

## Compilação

Na raiz do repositório:

```bash
make -C thesis/paper
```

O PDF é gerado em `thesis/paper/build/main.pdf`. Para limpar:

```bash
make -C thesis/paper clean
```

Ou, dentro de `thesis/paper`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

## Overleaf

Envie o conteúdo de `thesis/paper/`, incluindo `packages/` e `images/`.
Selecione `main.tex` como documento principal e pdfLaTeX como compilador.
Não é necessário enviar a pasta `build/`.
