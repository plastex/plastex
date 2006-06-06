#!/usr/bin/env python

import time
from plasTeX import Command

def ProcessOptions(options, document):
    context = document.context
    context.newcommand('refname', 0, r"R\'ef\'erences")
    context.newcommand('abstractname', 0, r"R\'esum\'e")
    context.newcommand('bibname', 0, r"Bibliographie")
    context.newcommand('prefacename', 0, r"Pr\'eface")
    context.newcommand('chaptername', 0, r"Chapitre")
    context.newcommand('appendixname', 0, r"Annexe")
    context.newcommand('contentsname', 0, r"Table des mati\`eres")
    context.newcommand('listfigurename', 0, r"Table des figures")
    context.newcommand('listtablename', 0, r"Liste des tableaux")
    context.newcommand('indexname', 0, r"Index")
    context.newcommand('figurename', 0, r"{\scshape Fig.}")
    context.newcommand('tablename', 0, r"{\scshape Tab.}")
    context.newcommand('CaptionSeparator', 0, r"\space\textendash\space")
    context.newcommand('partname', 0, 
        r"""{\ifcase\value{part}\space\or Premi\`ere\or Deuxi\`eme\or
        Troisi\`eme\or Quatri\`eme\or Cinqui\`eme\or Sixi\`eme\or
        Septi\`eme\or Huiti\`eme\or Neuvi\`eme\or Dixi\`eme\or Onzi\`eme\or
        Douzi\`eme\or Treizi\`eme\or Quatorzi\`eme\or Quinzi\`eme\or
        Seizi\`eme\or Dix-septi\`eme\or Dix-huiti\`eme\or Dix-neuvi\`eme\or
        Vingti\`eme\fi}\space partie""")
    context.newcommand('pagename', 0, r"page")
    context.newcommand('seename', 0, r"{\emph{voir}}")
    context.newcommand('alsoname', 0, r"{\emph{voir aussi}}")
    context.newcommand('enclname', 0, r"P.~J. ")
    context.newcommand('ccname', 0, r"Copie \`a ")
    context.newcommand('headtoname', 0, r"")
    context.newcommand('proofname', 0, r"D\'emonstration")
    context.newcommand('glossaryname', 0, r"Glossaire")
