export TEXINPUTS=.:./commontex:./texinputs/:

all: pdf html

pdf: plastex.tex
	pdflatex plastex
	pdflatex plastex
	makeindex plastex.idx
	pdflatex plastex

html:
	plastex plastex

xhtml:
	plastex --renderer=XHTML plastex

clean:
	rm -rf plastex *.idx *.ild *.ind *.paux *.aux *.out *.syn *.log *.toc plastex.pdf
