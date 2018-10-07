PDF!=find * -type f -a -not \( -name 'LICENSE.md' -o -name 'README.md' \) -name '*.md' | sed -e 's/\.md$$/.pdf/'

all: $(PDF)

clean:
	rm -f *.tex
	rm -f *.pdf

open: all
	for file in *.pdf; do which xdg-open >/dev/null 2>&1 && (setsid xdg-open *.pdf >/dev/null 2>&1 &) || open *.pdf >/dev/null 2>&1; done

%.pdf: %.tex
	latexmk -pdf $^
	latexmk -c $^

%.tex: %.md
	./convert.py $^ $@
