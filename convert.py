#!/usr/bin/env python
import collections
import logging
import re
import sys


logger = logging.getLogger('reportgen.convert')


class safe(str):
    def __repr__(self):
        return self.__class__.__name__ + '(' + super().__repr__() + ')'

    def __add__(self, rhs):
        if not isinstance(rhs, safe):
            raise RuntimeError('Attempted concatenation of \'safe\' and unsafe strings')
        s = super().__add__(rhs)
        return safe(s)

    def join(self, iter, *args, **kwargs):
        def checkiter(iter):
            for elem in iter:
                if not isinstance(elem, safe):
                    raise RuntimeError('Attempted join on \'safe\' and unsafe strings')
                yield elem
        return safe(super().join(checkiter(iter), *args, **kwargs))

    def replace(self, old, new, *args, **kwargs):
        if not isinstance(new, safe):
            raise RuntimeError('Attempted replacement of \'safe\' and unsafe strings')
        s = super().replace(old, new, *args, **kwargs)
        return safe(s)


preamble = safe(r'''\documentclass[12pt]{report}
\usepackage[letterpaper,left=3 cm,top=2.5 cm,right=3 cm,bottom=2.5 cm,headheight=1.5 cm,headsep=1.5 cm,foot=1 cm,footskip=1.5 cm,includeheadfoot]{geometry}
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
\usepackage[hidelinks]{hyperref}
\usepackage[usenames,dvipsnames]{xcolor}
\usepackage{sectsty}
\usepackage{lipsum}
\usepackage{listings}
\usepackage{float}
\usepackage{realboxes}
\usepackage{longtable}%watermark%

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

\definecolor{mygreen}{rgb}{0,0.6,0}
\definecolor{mygray}{rgb}{0.5,0.5,0.5}
\definecolor{mymauve}{rgb}{0.58,0,0.82}

\lstset{
  backgroundcolor=\color{white},
  basicstyle=\footnotesize,
  breakatwhitespace=false,
  breaklines=true,
  captionpos=b,
  commentstyle=\color{mygreen},
  deletekeywords={...},
  escapeinside={\%*}{*)},
  extendedchars=true,
  frame=single,
  keepspaces=true,
  keywordstyle=\color{blue},
  morekeywords={*,...},
  numbers=left,
  numbersep=5pt,
  numberstyle=\tiny\color{mygray},
  rulecolor=\color{black},
  showspaces=false,
  showstringspaces=false,
  showtabs=false,
  stepnumber=1,
  stringstyle=\color{mymauve},
  tabsize=2,
}

\begin{document}

\begin{titlepage}
  {
    \centering
    \vspace*{0.5 cm}
    \includegraphics[width=5.0 cm]{%logo%}\\[1.0 cm]
    { \huge \textbf{\thetitle} }%subtitle%\\[1.5 cm]
  }

  {
    \raggedleft%client%
    \textsc{\normalsize \thedate}\\[0.5 cm]
  }

  {
    \vfill
    \raggedright
    { \large \textbf{\theauthor} }%address%\\[2.0 cm]
  }%footer%
\end{titlepage}

\tableofcontents\thispagestyle{fancy}
\pagebreak
''')

watermark = safe(r'''
\usepackage{draftwatermark}

\SetWatermarkText{\textsc{%watermark%}}
\SetWatermarkScale{3.5}
\SetWatermarkLightness{0.95}''')

subtitle = safe(r'''\\[0.5 cm]
    { \Large \textbf{%subtitle%} }''')
client = safe(r'''
    { \Large \textbf{%client%} }\\[0.5 cm]''')
address = safe(r'''\\[0.5 cm]
    \textsc{\normalsize %address1%\\%address2%}''')
footer = safe(r'''

  {
    \begin{center}
      \textbf{%footer%}
    \end{center}
  }''')

preamble_formatted = {
    'watermark': (watermark, ['watermark']),
    'subtitle': (subtitle, ['subtitle']),
    'client': (client, ['client']),
    'address': (address, ['address1', 'address2']),
    'footer': (footer, ['footer'])
}

subsubsection = safe(r'''
\subsubsection{%title%}
\label{%label%}
''')
subsection = safe(r'''
\subsection{%title%}
\label{%label%}
''')
section = safe(r'''
\section{%title%}
\label{%label%}
''')

pagebreak = safe(r'''\pagebreak

''')

vuln = safe(r'''\begin{longtable}{p{4 cm}p{9 cm}}
  \textbf{Rating:} &
  \textcolor{%color%}{\textbf{%rating%}} \\[0.5 cm]
  \textbf{Description:} &
  %description% \\[0.5 cm]
  \textbf{Impact:} &
  %impact% \\[0.5 cm]
  \textbf{Recommendation:} &
  %recommendation% \\[0.5 cm]
\end{longtable}
''')
figure = safe(r'''\begin{figure}[H]
  \centering
  \includegraphics[width=14.0 cm]{%graphic%}
  \caption{%caption%}
  \label{fig:%label%}
\end{figure}
''')
unordered = safe(r'''\begin{itemize}
''')
unordered_item = safe(r'''\item %item%
''')
unordered_end = safe(r'''\end{itemize}
''')
ordered = safe(r'''\begin{enumerate}
''')
ordered_item = safe(r'''\item %item%
''')
ordered_end = safe(r'''\end{enumerate}
''')
listing = safe(r'''\begin{lstlisting}
''')
listing_language = safe(r'''\begin{lstlisting}[language=%language%]
''')
listing_end = safe(r'''\end{lstlisting}
''')
inline = safe(r'''\Colorbox{lightgray}{\lstinline$%code%$}''')
href = safe(r'\href{%href%}{%description%}')
numref = safe(r'\autoref{%ref%}')
nameref = safe(r'\nameref{%ref%}')
quote = safe(r"``%text%''")
single = safe(r"`%text%'")
bold = safe(r'\textbf{%text%}')
italic = safe(r'\textit{%text%}')
bolditalic = safe(r'\textbf{\textit{%text%}}')
footnote = safe(r'\footnote{%footnote%}')

postamble = safe(r'''

\end{document}
''')

tokens = collections.OrderedDict()
tokens['inline'] = r'(?<!\\)`([^`]*)`'
tokens['href'] = r'\[([^\]]*)\]\(([^)]*)\)'
tokens['bolditalic'] = r'\*\*\*((?:\\*|[^*])*)\*\*\*|___((?:\\_|[^_])*)___'
tokens['bold'] = r'\*\*((?:\\*|[^*])*)\*\*|__((?:\\_|[^_])*)__'
tokens['italic'] = r'\*((?:\\*|[^*])*)\*|_((?:\\_|[^_])*)_'
tokens['footnote'] = r'(?<!\\)\^((?:\\\^|[^^])*)\^'
tokens['ref'] = r'(?<!\\)\$((?:\\\$|[^$])*)\$'
tokens['single'] = r"(?<!\\)'((?:\\'|[^'])*)'"
tokens['quote'] = r'(?<!\\)"((?:\\"|[^"])*)"'
tokens['text'] = r'.+?'
tokenizer = r'|'.join(r'(?P<{}>{})'.format(key, value) for key, value in tokens.items())

symbols = collections.OrderedDict()
symbols['lbrace'] = (r'{', r'\{')
symbols['rbrace'] = (r'}', r'\}')
symbols['hash'] = (r'#', r'\#')
symbols['dollar'] = (r'\$', r'\$')
symbols['percent'] = (r'%', r'\%')
symbols['ampersand'] = (r'&', r'\&')
symbols['underscore'] = (r'_', r'\_')
symbols['backslash'] = (r'\\', r'\textbackslash{}')
symbols['circumflex'] = (r'\^', r'\textasciicircum{}')
symbols['tilde'] = (r'~', r'\textasciitilde{}')
symbols['default'] = (r'.+?', None)
symbolizer = r'|'.join(r'(?P<{}>{})'.format(key, value[0]) for key, value in symbols.items())


def escape(text):
    if isinstance(text, safe):
      return text

    def helper(text):
        for match in re.finditer(symbolizer, text):
            escaped = symbols[match.lastgroup][1]
            if escaped is None:
                yield safe(match.group())
            else:
                yield safe(escaped)

    return safe('').join(helper(text))


def format(text):
    if isinstance(text, safe):
      return text

    def helper(text):
        for match in re.finditer(tokenizer, text):
            if match.lastgroup == 'inline':
                nested = re.match(tokens['inline'], match.group())
                yield replace(inline, {'code': nested.group(1)})
            elif match.lastgroup == 'href':
                nested = re.match(tokens['href'], match.group())
                yield replace(href, {'description': nested.group(1), 'href': nested.group(2)})
            elif match.lastgroup == 'bolditalic':
                nested = re.match(tokens['bolditalic'], match.group())
                yield replace(bolditalic, {'text': nested.group(1) or nested.group(2)})
            elif match.lastgroup == 'bold':
                nested = re.match(tokens['bold'], match.group())
                yield replace(bold, {'text': nested.group(1) or nested.group(2)})
            elif match.lastgroup == 'italic':
                nested = re.match(tokens['italic'], match.group())
                yield replace(italic, {'text': nested.group(1) or nested.group(2)})
            elif match.lastgroup == 'footnote':
                nested = re.match(tokens['footnote'], match.group())
                yield replace(footnote, {'footnote': nested.group(1)})
            elif match.lastgroup == 'ref':
                nested = re.match(tokens['ref'], match.group())
                label = nested.group(1)
                if label.startswith('sec:'):
                    yield replace(nameref, {'ref': label})
                else:
                    yield replace(numref, {'ref': label})
            elif match.lastgroup == 'single':
                nested = re.match(tokens['single'], match.group())
                yield replace(single, {'text': nested.group(1)})
            elif match.lastgroup == 'quote':
                nested = re.match(tokens['quote'], match.group())
                yield replace(quote, {'text': nested.group(1)})
            elif match.lastgroup == 'text':
                yield match.group()
            else:
                logger.error('unknown format match group "{}"'.format(match.lastgroup))
                raise RuntimeError('Unknown format match group "{}"'.format(match.lastgroup))

    return safe('').join(formatted if isinstance(formatted, safe) else escape(formatted) for formatted in helper(text))


def slugify(text):
    return re.sub('^-+|-+$', '', re.sub('--+', '-', re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-').replace('.', '-'))))


def parse(infile, delimeter='```', noformat=['logo', 'graphic', 'date']):
    values = {}

    line = infile.readline()

    while line[:-1] != delimeter:
        if not line.strip():
            line = infile.readline()
            continue

        var, val = (token.strip() for token in line.split('='))
        values[var] = format(val) if var not in noformat else safe(val)

        line = infile.readline()
        while line.startswith(' ') or line.startswith('\t'):
            if values[var]:
                values[var] += safe(' ')

            values[var] += format(line.strip()) if var not in noformat else safe(line.strip())

            line = infile.readline()

    return values


def item(infile, line, level):
    output = []
    output.append(unordered)

    while line and line[level*2:].startswith('* ') or line[level*2:].startswith('- ') or line[level*2:].startswith('  '):
        if line[level*2:].startswith('  '):
            if line[level*2 + 2].isdigit():
                out, line = enum(infile, line, level + 1)
                output.append(out)
            else:
                out, line = item(infile, line, level + 1)
                output.append(out)
        else:
            output.append(replace(unordered_item, {'item': format(line[level*2 + 2:-1])}))

            line = infile.readline()

    output.append(unordered_end)

    return ''.join(output), line


def enum(infile, line, level):
    output = []
    output.append(ordered)

    while line and (line[level*2].isdigit() and line[level*2 + 1:].startswith('. ')) or line[level*2:].startswith('  '):
        if line[level*2:].startswith('  '):
            if line[level*2 + 2].isdigit():
                out, line = enum(infile, line, level + 1)
                output.append(out)
            else:
                out, line = item(infile, line, level + 1)
                output.append(out)
        else:
            output.append(replace(ordered_item, {'item': format(line[level*2 + 2:-1])}))

            line = infile.readline()

    output.append(ordered_end)

    return ''.join(output), line


def replace(text, values, variables=None, left='%', right='%'):
    if variables is None:
        variables = values

    for var, val in values.items():
        if left == '%' and right == '%':
            val = replace(val, variables, None, '[', ']')
        if isinstance(text, safe):
            val = escape(val)
        text = text.replace('{}{}{}'.format(left, var, right), val)

    return text


def convert(infile, outfile):
    line = infile.readline()

    while line.strip() == '':
        line = infile.readline()

    if line.startswith('```title'):
        values = parse(infile)

        rendered = values.copy()

        for formatted, (text, variables) in preamble_formatted.items():
          if all(var in rendered for var in variables):
            rendered[formatted] = replace(text, {var: rendered.pop(var) for var in variables}, values)
          else:
            rendered[formatted] = ''

        outfile.write(replace(preamble, rendered, values))
    else:
        logger.error('title block must be at start of file')
        raise RuntimeError('Title block must be at start of file')

    read = False
    newlines = 0

    while True:
        if not read:
            line = infile.readline()

        read = False

        if not line:
            break

        if line.startswith('###'):
            outfile.write(replace(subsubsection, {'title': format(line[3:].strip()), 'label': 'sec:' + slugify(line[3:].strip())}))
        elif line.startswith('##'):
            outfile.write(replace(subsection, {'title': format(line[2:].strip()), 'label': 'sec:' + slugify(line[2:].strip())}))
        elif line.startswith('#'):
            outfile.write(replace(section, {'title': format(line[1:].strip()), 'label': 'sec:' + slugify(line[1:].strip())}))
        elif line.startswith('* '):
            out, line = item(infile, line, 0)
            read = True

            outfile.write(out)
        elif line[0].isdigit() and line[1:].startswith('. '):
            out, line = enum(infile, line, 0)
            read = True

            outfile.write(out)
        elif line.startswith('```vuln'):
            values = parse(infile)

            if values['rating'].lower() == 'critical':
                values['color'] = 'Red'
            elif values['rating'].lower() == 'high':
                values['color'] = 'Orange'
            elif values['rating'].lower() == 'medium':
                values['color'] = 'Dandelion'
            else:
                values['color'] = 'Black'

            outfile.write(replace(vuln, values))
        elif line.startswith('```figure'):
            outfile.write(replace(figure, parse(infile)))
        elif line.startswith('```inline'):
            outfile.write('% BEGIN INLINE BLOCK %\n')

            line = infile.readline()

            while line != '```\n':
                outfile.write(line)
                line = infile.readline()

            outfile.write('% END INLINE BLOCK %\n')
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
        elif line.strip() == '':
            newlines += 1
            if newlines >= 3:
                outfile.write(pagebreak)
            else:
                outfile.write('\n')
                continue
        else:
            outfile.write(format(line))
            outfile.write('\n')

        newlines = 0

    outfile.write(postamble)


def convertv1(infile, outfile):
    line = infile.readline()

    if line.startswith('==='):
        values = parse(infile, '===')

        rendered = values.copy()

        for formatted, (text, variables) in preamble_formatted.items():
          if all(var in rendered for var in variables):
            rendered[formatted] = replace(text, {var: rendered.pop(var) for var in variables}, values)
          else:
            rendered[formatted] = ''

        outfile.write(replace(preamble, rendered, values))
    else:
        logger.error('title block must be at start of file')
        raise RuntimeError('Title block must be at start of file')

    read = False

    while True:
        if not read:
            line = infile.readline()

        read = False

        if not line:
            break

        if line.startswith('###'):
            outfile.write(replace(subsubsection, {'title': format(line[3:].strip()), 'label': 'sec:' + slugify(line[3:].strip())}))
        elif line.startswith('##'):
            outfile.write(replace(subsection, {'title': format(line[2:].strip()), 'label': 'sec:' + slugify(line[2:].strip())}))
        elif line.startswith('#'):
            outfile.write(replace(section, {'title': format(line[1:].strip()), 'label': 'sec:' + slugify(line[1:].strip())}))
        elif line.startswith('* '):
            out, line = item(infile, line, 0)
            read = True

            outfile.write(out)
        elif line[0].isdigit() and line[1:].startswith('. '):
            out, line = enum(infile, line, 0)
            read = True

            outfile.write(out)
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

            outfile.write(replace(vuln, values))
        elif line.startswith('...'):
            outfile.write(replace(figure, parse(infile, '...')))
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
        elif line.strip() == '':
            outfile.write('\n')
        else:
            outfile.write(format(line))
            outfile.write('\n')

    outfile.write(postamble)


def main():
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: {} <input.md> <output.tex>\n'.format(sys.argv[0]))
        sys.exit(1)

    logging.basicConfig()

    with open(sys.argv[1], 'r') as infile:
        with open(sys.argv[2], 'w') as outfile:
            first = infile.readline()
            infile.seek(0)

            try:
                if first.startswith('==='):
                    convertv1(infile, outfile)
                else:
                    convert(infile, outfile)
            except RuntimeError:
                logger.exception('Error while parsing input')
                sys.exit(2)


if __name__ == '__main__':
    main()
