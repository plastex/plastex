from lxml import etree
import os
import sys
import pexpect
try:
    import cPickle as pickle
except:
    import pickle
from string import Template
import re

XMLNS = 'http://www.w3.org/1998/Math/MathML'
XMLNS_qname = '{%s}' % XMLNS

bad_elem = Template('''<formula type="display">
  <math xmlns="%s">
    <mtext mathbackground="maroon"
           mathcolor="white">Problem: $error_text (rc = $return_code)</mtext>
    <mtext>$expr</mtext>
  </math>
</formula>''' % XMLNS)

def unescape(s):
    s = s.strip()
    s = s.replace('&lt;', '<',)
    s = s.replace('&gt;', '>',)
    s = s.replace('&amp;', '&',)
    s = s.replace(u'’', u'\'')
    s = s.replace(u'‘', u'\'')
    s = s.replace('\r', '')
    s = s.replace('\n', ' ')
    s = s.replace('\\cr', '\\\\')
    s = re.sub(r'\\\\\s+\\]', '\\]', s)
    if s.startswith(u'\\[') or s.startswith(u'\\begin'):
        s = s + u'\n'
    return s

def escape(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s

class TralicsDriver(object):
    def __init__(self, tralics_dir, options='-etex -noentnames -utf8 -oe8'):
        binary = os.path.join(tralics_dir, 'bin', 'tralics')
        cfgdir = os.path.join(tralics_dir, 'conf', 'tralics')
        self.newcommands = os.path.join(cfgdir, 'newcommands')

        self.tralics_cmd = '%s -interactivemath %s -confdir %s' % (binary, options, cfgdir)

        self.pickle_cache = os.path.join(cfgdir, 'cache.pkl')
        if os.path.isfile(self.pickle_cache):
            with open(self.pickle_cache) as f:
                self.cache = pickle.load(f)
            print 'cache %s keys' % len(self.cache)
        else:
            self.cache = dict()
        self.started = False
        self.errors = list()

    def start(self):
        self.child = pexpect.spawnu(self.tralics_cmd, maxread=4096, timeout=5)
        self.child.expect(u'> ')
        self.child.send(u'\\usepackage{amsmath}\n')
        self.child.expect(u'> ')
        if os.path.isfile(u'%s.tex' % self.newcommands):
            self.child.send(u'\\input{%s}\n' % self.newcommands)
            self.child.expect(u'> ')
        self.started = True

    def stop(self):
        if self.started:
            self.child.close()
            with open(self.pickle_cache, 'wb') as f:
                print 'writing cache %s keys' % len(self.cache)
                pickle.dump(self.cache, f)

    def convert(self, fname, mathstring):
        '''Driver entry point'''
        self.fname = fname
        mathstring = unescape(mathstring)
        elem = self.cache.get(mathstring)
        if elem:
            sys.stdout.write('.');sys.stdout.flush()
        else:
            if not self.started:
                self.start()
            sys.stdout.write('+');sys.stdout.flush()
            elem = self.getmath(mathstring)

        return elem

    def getmath(self, expr):
        exception_text = ''
        if expr.startswith('\\begin') or expr.startswith('\\['):
            self.child.sendline('%s\n' % expr)
        else:
            self.child.sendline(expr)
        try:
            rc = self.child.expect([unicode('<formula.*formula>'), pexpect.EOF])
        except (pexpect.TIMEOUT, UnicodeDecodeError):
            exception_text = 'timeout exceeded or unicode problem'
            rc = 4
        if rc:
            if not exception_text:
                exception_text = 'tralics error'
            return self.handle_error({
                'message': exception_text,
                'filename': self.fname,
                'latex': expr,
                'rc': rc})

        else:
            text_before, result = (self.child.before.strip(), self.child.after.strip())
            error_found = text_before.find('Error')

            if error_found != -1:
                exception_text = text_before[error_found:].replace('\n', '')
                return self.handle_error({
                    'message': exception_text,
                    'filename': self.fname,
                    'latex': expr,
                    'rc': 3})
            else:
                return self.clean_formula(expr, result)

    def clean_formula(self, expr, result):
        try:
            formula = etree.fromstring(result)
        except etree.XMLSyntaxError as e:
            exception_text = str(e)
            return self.handle_error({
                'message': exception_text,
                'filename': self.fname,
                'latex': expr,
                'rc': 5})
            
        elem = formula.find('%smath' % XMLNS_qname)
        if formula.attrib.get('type') == 'display':
            elem.attrib['display'] = 'block'
        else:
            elem.attrib['display'] = 'inline'

        if elem.attrib.get('mode'):
            del elem.attrib['mode']

        s = etree.tostring(elem)
        if not self.cache.get(expr):
            self.cache[expr] = s

        return s

    def handle_error(self, data):
        sys.stdout.write('x');sys.stdout.flush()
        self.child.close()
        self.start()
        
        if not data['message']:
            data['message'] = 'message placeholder'
        if not data['latex']:
            data['latex'] = 'latex placeholder'
            
        self.errors.append(data)
        return bad_elem.substitute({
                    'error_text': escape(data['message']),
                    'expr': escape(data['latex']),
                    'return_code': data['rc']})

