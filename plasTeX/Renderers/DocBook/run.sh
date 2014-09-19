export DocBookTEMPLATES=/r/ge.unx.sas.com/vol/vol101/u101/tiarno/tests/jss
export PYTHONPATH=/r/ge.unx.sas.com/vol/vol101/u101/tiarno/tests/jss
plastex --xml --renderer=DocBook --theme article --disable-images --split-level=-1 v58s01.tex
#cd v58s01
#xsltproc ../main.xsl index.xml
#cd ..
#python html2mathml v58s01/index.xml

