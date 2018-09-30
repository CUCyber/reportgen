PDF!=find * -type f -a -not \( -name 'LICENSE.md' -o -name 'README.md' \) -name '*.md' | sed -e 's/\.md$$/.pdf/'

all: $(PDF)

clean:
	rm -f *.tex
	rm -f *.pdf

open: all
	setsid xdg-open *.pdf &>/dev/null &

%.pdf: %.tex
	latexmk -pdf $^
	latexmk -c $^

%.tex: %.md
	./convert.py $^ $@
