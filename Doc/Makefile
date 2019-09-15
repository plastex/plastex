export TEXINPUTS=.:./commontex:./texinputs/:

pdf: plastex.tex
	pdflatex plastex
	pdflatex plastex
	makeindex plastex.idx
	pdflatex plastex


xhtml:
	plastex plastex

html5:
	plastex --renderer=HTML5 plastex

clean:
	rm -rf plastex *.idx *.ild *.ind *.paux *.aux *.out *.syn *.log *.toc plastex.pdf
