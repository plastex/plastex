all: pdf html 

pdf: getting_started.tex
	pdflatex getting_started

html:
	plastex -c getting_started.cfg getting_started

clean:
	rm -rf getting_started *.idx *.ild *.ind *.paux *.aux *.out *.syn *.log *.toc getting_started.pdf

