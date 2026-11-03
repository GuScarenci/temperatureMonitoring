.PHONY: all clean

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build thesis.tex

clean:
	latexmk -c -outdir=build thesis.tex
