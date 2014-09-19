from lxml import etree
from tralics import driver
import os
import sys
mathjax_elem = etree.Element('script', attrib= {
    'type': 'text/javascript',
    'src': 'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
    })


def main(name):
    mname = '%s_mathml.html' % os.path.splitext(os.path.basename(name))[0]
    t = driver.TralicsDriver('/AppDocs/local')

    parser = etree.HTMLParser()
    tree = etree.parse(name, parser)

    head = tree.find('head')
    head.append(mathjax_elem)

    for image in tree.xpath('//img[@class="math"]'):
        mtext = image.get('alt')
        if mtext:
            elemstring = t.convert(name, mtext)
            print mtext
            print elemstring
            try:
                math_elem = etree.fromstring(elemstring)

            except etree.XMLSyntaxError as e:
                print e

        image.getparent().replace(image, math_elem)

    mstring = etree.tostring(tree.getroot(), pretty_print=True,
                            encoding='UTF-8', method='html')

    with open(mname, 'wb') as f:
        f.write('<!DOCTYPE html>\n%s' % mstring)

    t.stop()

if __name__ == '__main__':
    main(sys.argv[1])
    print
