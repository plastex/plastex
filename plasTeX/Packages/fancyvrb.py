#!/usr/bin/env python

import string
from plasTeX.Utils import *
from plasTeX import Command, Environment
from verbatim import verbatim

class Verbatim(verbatim):
    args = '[ %options ]'
    def parse(self, tex):
        options = self.attributes['options']
        tex.context.categories = ['','','','','','','','','','',
                                  '', string.letters,'','','','']
        Environment.parse(self, tex)
        del tex.context.categories
        content = tex.getVerbatim(r'\end{%s}' % type(self).__name__)

        if options is None:
            options = {}

        # Format command
        formatcom = None
        if options.has_key('formatcom'):
            tex.context.groups.pushGrouping()
            formatcom = type(tex)(options['formatcom'].strip()).getToken()
            tex.context.groups.popGrouping(tex)

        # Frame width
        framerule = '1px'
        if options.has_key('framerule'):
            framerule = options['framerule'].strip()

        # Frame color
        rulecolor = 'black'
        if options.has_key('rulecolor'):
            tex.context.groups.pushGrouping()
            token = type(tex)(options['rulecolor'].strip()).getToken()
            tex.context.groups.popGrouping(tex)
            rulecolor = token.style['color']

        # Frames
        if options.has_key('frame'):
            frame = options['frame'].strip()
            if frame in ['leftline','single']:
                self.style['border-left'] = '%s solid %s' % \
                                             (framerule, rulecolor)
            if frame in ['rightline','single']:
                self.style['border-right'] = '%s solid %s' % \
                                              (framerule, rulecolor)
            if frame in ['topline','single','lines']:
                self.style['border-top'] = '%s solid %s' % \
                                            (framerule, rulecolor)
            if frame in ['bottomline','single','lines']:
                self.style['border-bottom'] = '%s solid %s' % \
                                               (framerule, rulecolor)

        # Padding 
        if options.has_key('framesep'):
            self.style['padding'] = options['framesep'].strip()

        # Font family
        if options.has_key('fontfamily'):
            self.style['font-family'] = options['fontfamily'].strip()

        # Font size
        if options.has_key('fontsize'):
            fontsize = options['fontsize'].strip()[1:]
            if fontsize == 'tiny':
                self.style['font-size'] = 'xx-small'
            elif fontsize == 'footnotesize':
                self.style['font-size'] = 'x-small'
            elif fontsize == 'small':
                self.style['font-size'] = 'small'
            elif fontsize == 'normalsize':
                self.style['font-size'] = 'medium'
            elif fontsize == 'large':
                self.style['font-size'] = 'large'
            elif fontsize == 'Large':
                self.style['font-size'] = 'x-large'
            elif fontsize == 'huge':
                self.style['font-size'] = 'xx-large'
            elif fontsize == 'huge':
                self.style['font-size'] = 'xx-large'

        # Font shape
        if options.has_key('fontshape'):
            fontshape = options['fontshape'].strip()
            if fontshape.startswith('i') or fontshape.startswith('o'):
                self.style['font-style'] = 'italic'

        # Font weight
        if options.has_key('fontseries'):
            fontseries = options['fontseries'].strip()
            if fontshape.startswith('b'):
                self.style['font-weight'] = 'bold'

        # Suppress characters at beginning
        if options.has_key('gobble'):
            gobble = int(options['gobble'])
            content = content.split('\n')
            for i in range(len(content)):
                try: content[i] = content[i][gobble:] 
                except: content[i] = ''
            content = '\n'.join(content)

        tex.context.categories = ['\\','{','}','','','','','','','',
                                  '', string.letters,'','','','']

        # Command chars
        if options.has_key('commandchars'):
            chars = str(options['commandchars'])
            tex.context.categories[0] = chars[0]
            tex.context.categories[1] = chars[1]
            tex.context.categories[2] = chars[2]

        # Comment char
        if options.has_key('commentchar'):
            char = str(options['commentchar'])
            tex.context.categories[14] = char

        content = type(tex)(content).parse()

        # Apply format command
        if formatcom is not None:
            formatcom[:] = content
            self.append(formatcom)
        else:
            self[:] = content

        del tex.context.categories

        return self 
