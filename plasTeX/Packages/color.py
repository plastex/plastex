#!/usr/bin/env python

from plasTeX import Command, Environment

def latex2htmlcolor(arg):
    if ',' in arg:
        red, green, blue = [float(x) for x in arg.split(',')]
        red = min(int(red * 255), 255)
        green = min(int(green * 255), 255)
        blue = min(int(blue * 255), 255)
    else:
        try: 
            red = green = blue = float(arg)
        except TypeError:
            return arg.strip()
    return '#%.2X%.2X%.2X' % (red, green, blue)

class textcolor(Command):
    args = 'color:str self'
    def invoke(self, tex):
        a = self.parse(tex)
        self.style['color'] = latex2htmlcolor(a['color'])

class color(Environment):
    args = 'color:str'
    def invoke(self, tex):
        a = self.parse(tex)
        self.style['color'] = latex2htmlcolor(a['color'])
