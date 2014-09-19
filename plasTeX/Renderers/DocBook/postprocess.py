from lxml import etree


xns = {'d': 'http://docbook.org/ns/docbook'}

def drop_tag(elem):
    """
    Remove the tag, but not its children or text.
    The children and text are merged into the parent.
    """
    parent = elem.getparent()
    previous = elem.getprevious()
    if elem.text and isinstance(elem.tag, basestring):
        if previous is None:
            parent.text = (parent.text or '') + elem.text
        else:
            previous.tail = (previous.tail or '') + elem.text
    if elem.tail:
        if len(elem):
            last = elem[-1]
            last.tail = (last.tail or '') + elem.tail
        elif previous is None:
            parent.text = (parent.text or '') + elem.tail
        else:
            previous.tail = (previous.tail or '') + elem.tail
    index = parent.index(elem)
    parent[index:index + 1] = elem[:]

def clean_bib(tree):
    for item in tree.findall('//d:section[@remap="bibliography"]', namespaces=xns):
        e = item.findall('d:itemizedlist/d:para', namespaces=xns)
        if e:
            drop_tag(e[0])

    return tree

def clean_table(tree):
    for table in tree.findall('//d:table', namespaces=xns):
        e = table.findall('d:para', namespaces=xns)
        if e:
            drop_tag(e[0])

    return tree

if __name__ == '__main__':
    tree = etree.parse('index.xml')
    tree = clean_bib(tree)
    tree = clean_table(tree)
    tree.write('index.xml', pretty_print=True, encoding='UTF-8')
