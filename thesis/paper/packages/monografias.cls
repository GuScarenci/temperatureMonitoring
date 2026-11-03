% Adaptação do documento Monografias.v2026.pdf (ICMC/USP).
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{packages/monografias}[2026/10/30 Monografia de graduacao ICMC]
\LoadClass[12pt,a4paper,oneside,openany]{report}
\RequirePackage{fontspec}
\setmainfont{Times New Roman}
\setsansfont{Arial}
\RequirePackage[brazil]{babel}
\RequirePackage[top=3cm,left=3cm,bottom=2cm,right=2cm]{geometry}
\RequirePackage{setspace}
\RequirePackage{indentfirst}
\RequirePackage{graphicx}
\RequirePackage{caption}
\RequirePackage{booktabs}
\RequirePackage[hidelinks,unicode,pdfpagelabels,hypertexnames=false]{hyperref}
\RequirePackage[alf]{abntex2cite}
\onehalfspacing
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{0pt}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{2}
\captionsetup{position=above,labelsep=endash,font=normalsize}
\newcommand{\fonte}[1]{\par\smallskip{\raggedright\small Fonte: #1\par}}
\newcommand{\fautor}{\fonte{Autor desta monografia.}}

% Dados institucionais configuráveis em metadata.tex.
\newcommand{\titulo}[1]{\title{#1}}
\newcommand{\autor}[2][]{\author{#2}}
\newcommand{\orientador}[3][Orientador:]{%
  \gdef\monorientador{#1\ #2\ #3}}
\newcommand{\curso}[1]{\gdef\moncurso{#1}}
\newcommand{\disciplina}[1]{\gdef\mondisciplina{#1}}
\newcommand{\area}[1]{\gdef\monarea{#1}}
\newcommand{\local}[1]{\gdef\monlocal{#1}}
\newcommand{\preambulo}[1]{\gdef\monpreambulo{#1}}
\preambulo{Monografia referente ao projeto de conclusão de curso dentro do
escopo da disciplina \mondisciplina\ do Departamento de Sistemas de Computação
 do Instituto de Ciências Matemáticas e de Computação -- ICMC-USP para
 obtenção do título de \moncurso.}

% Rodapé à direita, sem cabeçalho, também nas aberturas de capítulo.
\def\ps@plain{%
  \let\@oddhead\@empty\let\@evenhead\@empty
  \def\@oddfoot{\hfil\thepage}\let\@evenfoot\@oddfoot}
\pagestyle{plain}

% Capítulos em uma linha, sem os ornamentos do antigo modelo de pós-graduação.
\def\@makechapterhead#1{%
  {\parindent\z@\raggedright\sffamily\fontsize{20bp}{24bp}\selectfont\bfseries
   \ifnum\c@secnumdepth>\m@ne
     \MakeUppercase{\@chapapp}\space\thechapter:\space
   \fi
   \MakeUppercase{#1}\par\nobreak\vskip 24pt}}
\def\@makeschapterhead#1{%
  {\parindent\z@\centering\sffamily\fontsize{20bp}{24bp}\selectfont\bfseries
   #1\par\nobreak\vskip 24pt}}
\renewcommand\section{\@startsection{section}{1}{\z@}%
  {-3.5ex plus -1ex minus -.2ex}{2.3ex plus .2ex}%
  {\sffamily\fontsize{16bp}{20bp}\selectfont\bfseries}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-3.25ex plus -1ex minus -.2ex}{1.5ex plus .2ex}%
  {\sffamily\fontsize{14bp}{18bp}\selectfont\bfseries}}
\renewcommand\@seccntformat[1]{\csname the#1\endcsname.\quad}
\addto\captionsbrazil{\renewcommand{\contentsname}{Índice}%
  \renewcommand{\bibname}{REFERÊNCIAS}}

\newcommand{\imprimircapa}{%
  \hypersetup{pdftitle={\@title},pdfauthor={\@author}}
  \pagenumbering{arabic}
  \begin{center}
    {\sffamily\large UNIVERSIDADE DE SÃO PAULO\par
     Instituto de Ciências Matemáticas e de Computação\par
     \medskip Departamento de Sistemas de Computação\par}
    \vspace{3cm}
    {\sffamily\LARGE\@title\par}
    \vspace{1.5cm}
    {\sffamily\Large\@author\par}
    \vfill
    {\sffamily\large\monlocal\par}
    \vspace{1cm}
  \end{center}
  \clearpage
}
\newcommand{\imprimirfolhaderosto}{%
  \begin{center}
    {\sffamily\LARGE\@title\par}
    \vspace{1.5cm}
    {\sffamily\Large\@author\par}
    \vspace{2cm}
    {\sffamily\large\monorientador\par}
  \end{center}
  \vspace{1cm}
  \noindent\hspace*{.28\textwidth}%
  \begin{minipage}{.72\textwidth}
    \singlespacing\monpreambulo\par
    \vspace{1cm}
    Área de Concentração: \monarea
  \end{minipage}
  \vfill
  \noindent USP -- São Carlos\par
  \clearpage
}
\newenvironment{resumo}{\chapter*{Resumo}\doublespacing}{\par\clearpage}
\newcommand{\palavraschave}[1]{\par\medskip\noindent\textbf{Palavras-chave:} #1.}
\newcommand{\pretextual}{\clearpage\pagenumbering{roman}}
\newcommand{\textual}{\clearpage\pagenumbering{arabic}\onehalfspacing}
\newcommand{\postextual}{\clearpage}
