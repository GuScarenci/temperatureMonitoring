# Fontes locais da entrega atual

Projeto extraído do Overleaf. Documento principal: **`thesis.tex`**. Compilador: **pdfLaTeX**. Classe de formatação: `packages/icmc.cls`.

Na raiz do repositório:

```bash
make -C thesis/paper
```

Saída: `build/thesis.pdf` dentro desta pasta. O PDF de referência está em [`../TCC_GustavoMoura.pdf`](../TCC_GustavoMoura.pdf) e não é sobrescrito pela compilação.

Consulte o [guia da monografia](../README.md) para organização, histórico, uso do Overleaf e atualização opcional das tabelas e figuras. Os capítulos utilizados estão em `sections/`; os arquivos em `tex/capitulos/` são remanescentes do modelo e não são carregados por `thesis.tex`.
