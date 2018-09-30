#!/usr/bin/env python
import re
import sys


if len(sys.argv) != 3:
    sys.stderr.write('Usage: {} <input.md> <output.tex>\n'.format(sys.argv[0]))
    sys.exit(1)


with open(sys.argv[1], 'r') as infile:
    with open(sys.argv[2], 'w') as outfile:
        line = infile.readline()

        if line == '===\n':
            line = infile.readline()

            while line != '===\n':
                if not line.strip():
                    line = infile.readline()
                    continue

                var, val = line.split('=')

                if var == 'logo':
                    logo = val.strip()
                elif var == 'title':
                    title = val.strip()
                elif var == 'author':
                    author = val.strip()
                elif var == 'date':
                    date = val.strip()
                elif var == 'company':
                    company = val.strip()
                elif var == 'address1':
                    address1 = val.strip()
                elif var == 'address2':
                    address2 = val.strip()

                line = infile.readline()
                while line.startswith(' ') or line.startswith('\t'):
                    if var == 'logo':
                        logo += ' ' + line.strip()
                    elif var == 'title':
                        title += ' ' + line.strip()
                    elif var == 'author':
                        author += ' ' + line.strip()
                    elif var == 'date':
                        date += ' ' + line.strip()
                    elif var == 'company':
                        company += ' ' + line.strip()
                    elif var == 'address1':
                        address1 += ' ' + line.strip()
                    elif var == 'address2':
                        address2 += ' ' + line.strip()

                    line = infile.readline()

        outfile.write(r'''\documentclass[12pt]{report}
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

\title{''' + title + r'''}
\author{''' + author + r'''}
\date{''' + date + r'''}

\makeatletter
\let\thetitle\@title
\let\theauthor\@author
\let\thedate\@date
\makeatother

\pagestyle{fancy}
\fancyhf{}
\lhead{\includegraphics[height=1.5 cm]{''' + logo + r'''}}
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
    { \Large \textbf{''' + company + r'''} }\\[0.5 cm]
    \textsc{\normalsize \thedate}\\[0.5 cm]
  }

  {
    \vfill
    \raggedright
    { \large \textbf{\theauthor} }\\[0.5 cm]
    \textsc{\normalsize ''' + address1 + r'''\\''' + address2 + r'''}\\[2.0 cm]
  }
\end{titlepage}

\tableofcontents\thispagestyle{fancy}
\pagebreak

''')

        for line in infile:
            if line.startswith('###'):
              outfile.write(r'''\subsubsection{''' + line[3:].strip() + r'''}

''')
            elif line.startswith('##'):
              outfile.write(r'''\subsection{''' + line[2:].strip() + r'''}

''')
            elif line.startswith('#'):
              outfile.write(r'''\section{''' + line[1:].strip() + r'''}

''')
            elif line == '---\n':
                line = infile.readline()

                while line != '---\n':
                    if not line.strip():
                        line = infile.readline()
                        continue

                    var, val = line.split('=')

                    if var == 'rating':
                        rating = val.strip()
                    elif var == 'description':
                        description = val.strip()
                    elif var == 'impact':
                        impact = val.strip()
                    elif var == 'remediation':
                        remediation = val.strip()

                    line = infile.readline()
                    while line.startswith(' ') or line.startswith('\t'):
                        if var == 'rating':
                            rating += ' ' + line.strip()
                        elif var == 'description':
                            description += ' ' + line.strip()
                        elif var == 'impact':
                            impact += ' ' + line.strip()
                        elif var == 'remediation':
                            remediation += ' ' + line.strip()

                        line = infile.readline()

                outfile.write(r'''\begin{tabular}{p{3 cm}p{7 cm}}
  \textbf{Rating:} &
  \textcolor{''' + ('Red' if rating.lower() == 'critical' else 'Orange' if rating.lower() == 'high' else 'Dandelion' if rating.lower() == 'medium' else 'Black') + r'''}{\textbf{''' + rating + r'''}} \\[0.5 cm]
  \textbf{Description:} &
  ''' + description + r''' \\[0.5 cm]
  \textbf{Impact:} &
  ''' + impact + r''' \\[0.5 cm]
  \textbf{Remediation:} &
  ''' + remediation + r''' \\[0.5 cm]
\end{tabular}
''')
            elif line == '...\n':
                line = infile.readline()

                while line != '...\n':
                    if not line.strip():
                        line = infile.readline()
                        continue

                    var, val = line.split('=')

                    if var == 'graphic':
                        graphic = val.strip()
                    elif var == 'caption':
                        caption = val.strip()
                    elif var == 'label':
                        label = val.strip()

                    line = infile.readline()
                    while line.startswith(' ') or line.startswith('\t'):
                        if var == 'graphic':
                            graphic += ' ' + line.strip()
                        elif var == 'caption':
                            caption += ' ' + line.strip()
                        elif var == 'label':
                            label += ' ' + line.strip()

                        line = infile.readline()

                outfile.write(r'''\begin{figure}[h]
  \centering
  \includegraphics[height=3.0 cm]{''' + graphic + r'''}
  \caption{''' + caption + r'''}
  \label{''' + label + r'''}
\end{figure}
''')
            elif line.startswith('```'):
                if len(line) > 3:
                    outfile.write(r'''\begin{lstlisting}[language=''' + line[3:-1] + r''']
''')
                else:
                    outfile.write(r'''\begin{lstlisting}
''')

                line = infile.readline()

                while line != '```\n':
                    outfile.write(line)
                    line = infile.readline()

                outfile.write(r'''\end{lstlisting}
''')
            elif line == '...\n':
                line = infile.readline()

                while line != '...\n':
                    if not line.strip():
                        line = infile.readline()
                        continue

                    var, val = line.split('=')

                    if var == 'graphic':
                        graphic = val.strip()
                    elif var == 'caption':
                        caption = val.strip()
                    elif var == 'label':
                        label = val.strip()

                    line = infile.readline()
                    while line.startswith(' ') or line.startswith('\t'):
                        if var == 'graphic':
                            graphic += ' ' + line.strip()
                        elif var == 'caption':
                            caption += ' ' + line.strip()
                        elif var == 'label':
                            label += ' ' + line.strip()

                        line = infile.readline()

                outfile.write(r'''\begin{figure}[h]
  \centering
  \includegraphics[height=3.0 cm]{''' + graphic + r'''}
  \caption{''' + caption + r'''}
  \label{''' + label + r'''}
\end{figure}
''')
            else:
                outfile.write(re.sub(r'\$([^$]*)\$', r'\\autoref{\1}', line))


        outfile.write(r'''

\end{document}
''')
