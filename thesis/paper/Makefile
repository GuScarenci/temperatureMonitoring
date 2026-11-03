.PHONY: all clean

all:
	latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex

clean:
	latexmk -C -outdir=build main.tex
