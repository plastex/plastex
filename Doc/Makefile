export TEXINPUTS=.:./commontex:./texinputs/:

pdf: plastex.aux
	pdflatex plastex

html:
	plastex plastex

html5:
	plastex --renderer=HTML5 plastex

plastex.aux:
	pdflatex plastex

clean:
	rm -rf plastex *.idx *.paux *.aux *.out *.syn *.log *.toc plastex.pdf
