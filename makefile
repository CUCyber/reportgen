PDF!=find * -type f -a -not \( -name 'LICENSE.md' -o -name 'README.md' \) -name '*.md' | sed -e 's/\.md$$/.pdf/'

all: $(PDF)

clean:
	rm -f *.tex
	rm -f *.pdf

open: all
	find * -type f -name '*.pdf' -exec sh -c 'which xdg-open >/dev/null 2>&1 && (setsid xdg-open {} >/dev/null 2>&1 &) || open {} >/dev/null 2>&1' ';'

%.pdf: %.tex
	latexmk -pdf $^
	latexmk -c $^

%.tex: %.md
	./convert.py $^ $@
