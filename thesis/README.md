# Monografia — versão consolidada do Overleaf

**Reconstrução virtual de temperaturas a partir de sensores IoT no LASDPC**  
Gustavo Moura Scarenci de Carvalho Ferreira — Orientador: Prof. Dr. Júlio Cezar Estrella — ICMC/USP, 2026.

O [PDF de referência](TCC_GustavoMoura.pdf) é o arquivo atualizado fornecido pelo autor, preservado sem alterações. Os [fontes locais](paper/) foram extraídos do mesmo projeto do Overleaf, mantendo o conteúdo, as figuras e a classe de formatação ICMC.

| Caminho | Finalidade |
|---|---|
| `TCC_GustavoMoura.pdf` | PDF de referência da entrega atual |
| `paper/thesis.tex` | Documento principal da versão atual |
| `paper/sections/` | Capítulos efetivamente incluídos pelo documento principal |
| `paper/tables/`, `paper/figures/`, `paper/images/` | Tabelas e recursos gráficos da entrega |
| `paper/packages/icmc.cls` | Classe de formatação original do Overleaf |
| `scripts/exportar_resultados.py` | Atualização opcional das tabelas e figuras a partir dos experimentos |
| `archive/overleaf-original.zip` | Exportação original do Overleaf, preservada integralmente |
| `archive/paper-anterior.zip` | Fontes e documentação da versão local anterior, antes da unificação |
| `propose.pdf` | Proposta original do trabalho |
| `pdf_template/`, `relatedPapers/` | Modelo anterior e referências de apoio |

## Compilação local

Requisitos: `latexmk`, pdfLaTeX e os pacotes usados pela classe ICMC/abnTeX2. O projeto atual utiliza **pdfLaTeX**, conforme a configuração do Overleaf exportado.

A partir da raiz do repositório:

```bash
make -C thesis/paper
```

Saída: `thesis/paper/build/thesis.pdf`. Essa compilação não substitui o PDF de referência em `thesis/TCC_GustavoMoura.pdf`. A identidade binária com o PDF do Overleaf não é garantida: versões de TeX e metadados da compilação podem variar.

Para limpar arquivos auxiliares:

```bash
make -C thesis/paper clean
```

Para usar o Overleaf, envie o conteúdo de `paper/`, sem `build/`, selecione `thesis.tex` como documento principal e pdfLaTeX como compilador. Os arquivos em `tex/capitulos/` são remanescentes do modelo exportado e não são incluídos pelo documento principal.

## Atualizar os artefatos da pesquisa

O fluxo experimental está em [code/tcc/README.md](../code/tcc/README.md). Para conferir os resultados locais:

```bash
.venv/bin/python code/tcc/verificar_resultados.py
```

Se houver uma atualização deliberada dos experimentos, o comando abaixo regrava tabelas e figuras nos fontes atuais:

```bash
python3 thesis/scripts/exportar_resultados.py
make -C thesis/paper
```

A exportação não atualiza os números escritos nos parágrafos, o PDF de referência ou os arquivos históricos. Para apenas ler ou compilar a entrega preservada, não é necessário executar o exportador.

## Histórico e preservação

A antiga pasta `new_thesis/` foi incorporada a esta estrutura. O PDF foi apenas renomeado e o ZIP original foi movido para `archive/`; ambos mantêm os bytes originais. Os fontes extraídos preservam os arquivos do ZIP, exceto o README substituído por instruções locais e o PDF interno redundante, que continuam disponíveis no ZIP original.

A árvore local anterior de `thesis/paper/`, incluindo seus documentos de revisão, foi arquivada em `archive/paper-anterior.zip`, sem arquivos de compilação ou caches. Ela utiliza `main.tex`/LuaLaTeX e serve apenas como histórico. A [avaliação do TCC](../docs/avaliacao-tcc.md) registra a revisão realizada antes desta reorganização.
