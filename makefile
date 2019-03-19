PDF!=find * -type f -a -not \( -name 'LICENSE.md' -o -name 'README.md' \) -name '*.md' | sed -e 's/\.md$$/.pdf/'

all: $(PDF)

clean:
	find * -type f -name '*.tex' -exec rm -f '{}' ';'
	find * -type f -name '*.pdf' -exec rm -f '{}' ';'

open: all
	find * -type f -name '*.pdf' -exec sh -c 'which xdg-open >/dev/null 2>&1 && (setsid xdg-open {} >/dev/null 2>&1 &) || open {} >/dev/null 2>&1' ';'

%.pdf: %.tex
	sh -c 'cd `dirname $^` && latexmk -pdf `basename $^` && latexmk -c `basename $^`'

%.tex: %.md
	./convert.py $^ $@
