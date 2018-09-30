PDF!=find . -name '*.md' | sed -e 's/\.md$$/.pdf/'

all: $(PDF)

clean:
	rm -f *.pdf

open: all
	setsid xdg-open *.pdf &>/dev/null &

%.pdf: %.tex
	latexmk -pdf $^
	latexmk -c $^
	rm $^

%.tex: %.md
	./convert.py $^ $@
