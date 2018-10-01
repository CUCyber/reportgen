#!/usr/bin/env python
import re
import sys


if len(sys.argv) != 3:
    sys.stderr.write('Usage: {} <input.md> <output.tex>\n'.format(sys.argv[0]))
    sys.exit(1)


preamble = r'''\documentclass[12pt]{report}
\usepackage[english]{babel}
\usepackage{natbib}
\usepackage{url}
\usepackage[utf8x]{inputenc}
\usepackage{titletoc}
\usepackage{tocloft}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{parskip}
\usepackage{fancyhdr}
\usepackage{vmargin}
\usepackage{hyperref}
\usepackage[usenames,dvipsnames]{xcolor}
\usepackage{sectsty}
\usepackage{lipsum}
\usepackage{listings}
\setmarginsrb{3 cm}{2.5 cm}{3 cm}{2.5 cm}{1 cm}{1.5 cm}{1 cm}{1.5 cm}

\title{%title%}
\author{%author%}
\date{%date%}

\makeatletter
\let\thetitle\@title
\let\theauthor\@author
\let\thedate\@date
\makeatother

\pagestyle{fancy}
\fancyhf{}
\lhead{\includegraphics[height=1.5 cm]{%logo%}}
\rhead{\thetitle\text{ - }\theauthor}
\cfoot{\thepage}

\makeatletter
\renewcommand*\l@section{\@dottedtocline{1}{1.5em}{2.3em}}
\makeatother

\renewcommand{\thesection}{}
\renewcommand{\thesubsection}{}

\makeatletter
\def\@seccntformat#1{\csname #1ignore\expandafter\endcsname\csname the#1\endcsname\quad}
\let\sectionignore\@gobbletwo
\let\subsectionignore\@gobbletwo
\let\latex@numberline\numberline
\def\numberline#1{\if\relax#1\relax\else\latex@numberline{#1}\fi}
\makeatother

\setlength{\cftsubsecindent}{2cm}

\sectionfont{\color{Blue}}
\subsectionfont{\color{MidnightBlue}}

\addto\captionsenglish{\def\contentsname{\color{Blue} Contents}}

\begin{document}

\begin{titlepage}
  {
    \centering
    \vspace*{0.5 cm}
    \includegraphics[width=5.0 cm]{shield.png}\\[1.0 cm]
    { \huge \textbf{\thetitle} }\\[1.5 cm]
  }

  {
    \raggedleft
    { \Large \textbf{%company%} }\\[0.5 cm]
    \textsc{\normalsize \thedate}\\[0.5 cm]
  }

  {
    \vfill
    \raggedright
    { \large \textbf{\theauthor} }\\[0.5 cm]
    \textsc{\normalsize %address1%\\%address2%}\\[2.0 cm]
  }
\end{titlepage}

\tableofcontents\thispagestyle{fancy}
\pagebreak
'''

subsubsection = r'''
\subsubsection{%title%}
'''
subsection = r'''
\subsection{%title%}
'''
section = r'''
\section{%title%}
'''

vuln = r'''\begin{tabular}{p{3 cm}p{7 cm}}
  \textbf{Rating:} &
  \textcolor{%color%}{\textbf{%rating%}} \\[0.5 cm]
  \textbf{Description:} &
  %description% \\[0.5 cm]
  \textbf{Impact:} &
  %impact% \\[0.5 cm]
  \textbf{Remediation:} &
  %remediation% \\[0.5 cm]
\end{tabular}
'''
figure = r'''\begin{figure}[h]
  \centering
  \includegraphics[height=3.0 cm]{%graphic%}
  \caption{%caption%}
  \label{%label%}
\end{figure}
'''
listing = r'''\begin{lstlisting}
'''
listing_language = r'''\begin{lstlisting}[language=%language%]
'''
listing_end = r'''\end{lstlisting}
'''
href = r'\href{%href%}{%description%}'
ref = r'\autoref{%ref%}'
bold = r'\textbf{%text%}'
italic = r'\textit{%text%}'
bolditalic = r'\textbf{\textit{%text%}}'
footnote = r'\footnote{%footnote%}'

postamble = r'''

\end{document}
'''


def parse(infile, delimeter):
    values = {}

    line = infile.readline()

    while line[:-1] != delimeter:
        if not line.strip():
            line = infile.readline()
            continue

        var, val = line.split('=')
        values[var] = val.strip()

        line = infile.readline()
        while line.startswith(' ') or line.startswith('\t'):
            values[var] += ' ' + line.strip()

            line = infile.readline()

    return values


def replace(text, values):
    for var, val in values.items():
        text = text.replace('%{}%'.format(var), val)

    return text


def link(text):
    text = re.sub(r'\[([^\]]*)\]\(([^)]*)\)', replace(href.replace('\\', '\\\\'), {'description': r'\1', 'href': r'\2'}), text)

    text = re.sub(r'\*\*\*([^*]*)\*\*\*', replace(bolditalic.replace('\\', '\\\\'), {'text': r'\1'}), text)
    text = re.sub(r'\*\*([^*]*)\*\*', replace(bold.replace('\\', '\\\\'), {'text': r'\1'}), text)
    text = re.sub(r'\*([^*]*)\*', replace(italic.replace('\\', '\\\\'), {'text': r'\1'}), text)

    text = re.sub(r'___([^_]*)___', replace(bolditalic.replace('\\', '\\\\'), {'text': r'\1'}), text)
    text = re.sub(r'__([^_]*)__', replace(bold.replace('\\', '\\\\'), {'text': r'\1'}), text)
    text = re.sub(r'_([^_]*)_', replace(italic.replace('\\', '\\\\'), {'text': r'\1'}), text)

    text = re.sub(r'\^([^^]*)\^', replace(footnote.replace('\\', '\\\\'), {'footnote': r'\1'}), text)
    text = re.sub(r'\$([^$]*)\$', replace(ref.replace('\\', '\\\\'), {'ref': r'\1'}), text)

    return text


with open(sys.argv[1], 'r') as infile:
    with open(sys.argv[2], 'w') as outfile:
        line = infile.readline()

        if line.startswith('==='):
            outfile.write(replace(preamble, parse(infile, '===')))

        for line in infile:
            if line.startswith('###'):
                outfile.write(link(replace(subsubsection, {'title': line[3:].strip()})))
            elif line.startswith('##'):
                outfile.write(link(replace(subsection, {'title': line[2:].strip()})))
            elif line.startswith('#'):
                outfile.write(link(replace(section, {'title': line[1:].strip()})))
            elif line.startswith('---'):
                values = parse(infile, '---')

                if values['rating'].lower() == 'critical':
                    values['color'] = 'Red'
                elif values['rating'].lower() == 'high':
                    values['color'] = 'Orange'
                elif values['rating'].lower() == 'medium':
                    values['color'] = 'Dandelion'
                else:
                    values['color'] = 'Black'

                outfile.write(link(replace(vuln, values)))
            elif line.startswith('...'):
                outfile.write(link(replace(figure, parse(infile, '...'))))
            elif line.startswith('```'):
                if len(line) > 4:
                    outfile.write(replace(listing_language, {'language': line[3:-1]}))
                else:
                    outfile.write(listing)

                line = infile.readline()

                while line != '```\n':
                    outfile.write(line)
                    line = infile.readline()

                outfile.write(listing_end)
            else:
                outfile.write(link(line))


        outfile.write(postamble)
