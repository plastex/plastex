#!/usr/bin/env python

"""
B.3 Parameters

"""

from datetime import datetime
from plasTeX import Parameter, Count, Dimen, MuDimen, Glue, MuGlue
from plasTeX import count, dimen, mudimen, glue, muglue

#
# TeX parameters (see The TeXbook, page 272)
#

# Integer parameters
class pretolerance(Parameter): value = count(100)
class tolerance(Parameter): value = count(200)
class hbadness(Parameter): value = count(1000)
class vbadness(Parameter): value = count(1000)
class linepenalty(Parameter): value = count(1000)
class hyphenpenalty(Parameter): value = count(50)
class exhyphenpenalty(Parameter): value = count(50)
class binoppenalty(Parameter): value = count(700)
class relpenalty(Parameter): value = count(500)
class clubpenalty(Parameter): value = count(150)
class widowpenalty(Parameter): value = count(150)
class displaywidowpenalty(Parameter): value = count(50)
class brokenpenalty(Parameter): value = count(100)
class predisplaypenalty(Parameter): value = count(10000)
class postdisplaypenalty(Parameter): value = count(0)
class interlinepenalty(Parameter): value = count(0)
class floatingpenalty(Parameter): value = count(0)
class outputpenalty(Parameter): value = count(0)
class doublehyphendemerits(Parameter): value = count(100000)
class finalhyphendemerits(Parameter): value = count(5000)
class adjdemerits(Parameter): value = count(10000)
class looseness(Parameter): value = count(0)
class pausing(Parameter): value = count(0)
class holdinginserts(Parameter): value = count(0)
class tracingonline(Parameter): value = count(0)
class tracingmacros(Parameter): value = count(0)
class tracingstats(Parameter): value = count(0)
class tracingparagraphs(Parameter): value = count(0)
class tracingpages(Parameter): value = count(0)
class tracingoutput(Parameter): value = count(0)
class tracinglostchars(Parameter): value = count(1)
class tracingcommands(Parameter): value = count(0)
class tracingrestores(Parameter): value = count(0)
class language(Parameter): value = count(0)
class uchyph(Parameter): value = count(1)
class lefthyphenmin(Parameter): value = count(0)
class righthyphenmin(Parameter): value = count(0)
class globaldefs(Parameter): value = count(0)
class defaulthyphenchar(Parameter): value = count(ord('-'))
class defaultskewchar(Parameter): value = count(-1)
class escapechar(Parameter): value = count(ord('\\'))
class endlinechar(Parameter): value = count(ord('\n'))
class newlinechar(Parameter): value = count(-1)
class maxdeadcycles(Parameter): value = count(25)
class hangafter(Parameter): value = count(1)
class fam(Parameter): value = count(0)
class mag(Parameter): value = count(1000)
class delimiterfactor(Parameter): value = count(901)
class time(Parameter): value = count((datetime.now().hour*60) + datetime.now().minute)
class day(Parameter): value = count(datetime.now().day)
class month(Parameter): value = count(datetime.now().month)
class year(Parameter): value = count(datetime.now().year)
class showboxbreadth(Parameter): value = count(5)
class showboxdepth(Parameter): value = count(3)
class errorcontextlines(Parameter): value = count(5)

# Dimen parameters
class hfuzz(Dimen): value = dimen('0.1pt')
class vfuzz(Dimen): value = dimen('0.1pt')
class overfullrule(Dimen): value = dimen('5pt')
class emergencystretch(Dimen): value = dimen(0)
class hsize(Dimen): value = dimen('6.5in')
class vsize(Dimen): value = dimen('8.9in')
class maxdepth(Dimen): value = dimen('4pt')
class splitmaxdepth(Dimen): value = dimen('65536pt')
class boxmaxdepth(Dimen): value = dimen('65536pt')
class lineskipamount(Dimen): value = dimen(0)
class delimitershortfall(Dimen): value = dimen('5pt')
class nulldelimiterspace(Dimen): value = dimen('1.2pt')
class scriptspace(Dimen): value = dimen('0.5pt')
class mathsurround(Dimen): value = dimen(0)
class predisplaysize(Dimen): value = dimen(0)
class displaywidth(Dimen): value = dimen(0)
class displayindent(Dimen): value = dimen(0)
class parindent(Dimen): value = dimen('20pt')
class hangindent(Dimen): value = dimen(0)
class hoffset(Dimen): value = dimen(0)
class voffset(Dimen): value = dimen(0)

# Glue parameters
class baselineskip(Glue): value = glue('12pt')
class lineskip(Glue): value = glue('1pt')
class parskip(Glue): value = glue('0pt', plus='1pt')
class abovedisplayskip(Glue): value = glue('0pt', plus='3pt', minus='9pt')
class abovedisplayshortskip(Glue): value = glue('0pt', plus='3pt')
class belowdisplayskip(Glue): value = glue('12pt', plus='3pt', minus='9pt')
class belowdisplayshortskip(Glue): value = glue('7pt', plus='3pt', minus='4pt')
class leftskip(Glue): value = glue(0)
class rightskip(Glue): value = glue(0)
class topskip(Glue): value = glue('10pt')
class splittopskip(Glue): value = glue('10pt')
class tabskip(Glue): value = glue(0)
class spaceskip(Glue): value = glue(0)
class xspaceskip(Glue): value = glue(0)
class parfillskip(Glue): value = glue('0pt', plus='1fil')

# MuGlue parameters
class thinmuskip(MuGlue): value = muglue('3mu')
class medmuskip(MuGlue): value = muglue('4mu', plus='2mu', minus='4mu')
class thickmuskip(MuGlue): value = muglue('5mu', plus='5mu')

# Token parameters
#class output(Parameter): pass
#class everypar(Parameter): pass
#class everymath(Parameter): pass
#class everydisplay(Parameter): pass
#class everyhbox(Parameter): pass
#class everyvbox(Parameter): pass
#class everyjob(Parameter): pass
#class everycr(Parameter): pass
#class errhelp(Parameter): pass
