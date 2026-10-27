# Artigo em LaTeX

O arquivo principal é `main.tex`. Edite o título e o autor nele, escreva o
conteúdo em `sections/` e coloque imagens em `figures/`.

## Instalação (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install latexmk texlive-latex-recommended texlive-lang-portuguese
```

## Compilação

Na raiz do repositório:

```bash
cd thesis/paper
make
```

O PDF será gerado em `build/main.pdf`. Para limpar os arquivos gerados, execute
`make clean`.

Também é possível compilar sem Make:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

No Overleaf, envie o conteúdo desta pasta e selecione `main.tex` como documento
principal, usando o compilador pdfLaTeX.
