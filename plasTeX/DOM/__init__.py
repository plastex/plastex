#!/usr/bin/env python

from plasTeX.Logging import getLogger

class DOMString(unicode):
    """
    DOM String

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-C74D1578
    """

class DOMTimeStamp(long):
    """
    DOM Time Stamp

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#Core-DOMTimeStamp
    """

class DOMUserData(object):
    """
    DOM User Data

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#Core-DOMUserData
    """

class DOMObject(object):
    """
    DOM Object

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#Core-DOMObject
    """

# Exception Code
INDEX_SIZE_ERR                 = 1
DOMSTRING_SIZE_ERR             = 2
HIERARCHY_REQUEST_ERR          = 3
WRONG_DOCUMENT_ERR             = 4
INVALID_CHARACTER_ERR          = 5
NO_DATA_ALLOWED_ERR            = 6
NO_MODIFICATION_ALLOWED_ERR    = 7
NOT_FOUND_ERR                  = 8
NOT_SUPPORTED_ERR              = 9
INUSE_ATTRIBUTE_ERR            = 10
INVALID_STATE_ERR              = 11
SYNTAX_ERR                     = 12
INVALID_MODIFICATION_ERR       = 13
NAMESPACE_ERR                  = 14
INVALID_ACCESS_ERR             = 15
VALIDATION_ERR                 = 16

class DOMException(Exception):
    """ 
    DOM Exception 

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-17189187
    """
    def __init__(self, *args, **kw):
        if self.__class__ is DOMException:
            raise RuntimeError(
                "DOMException should not be instantiated directly")
        Exception.__init__(self, *args, **kw)

    def _get_code(self):
        return self.code

class IndexSizeErr(DOMException):
    code = INDEX_SIZE_ERR

class DomstringSizeErr(DOMException):
    code = DOMSTRING_SIZE_ERR

class HierarchyRequestErr(DOMException):
    code = HIERARCHY_REQUEST_ERR

class WrongDocumentErr(DOMException):
    code = WRONG_DOCUMENT_ERR

class InvalidCharacterErr(DOMException):
    code = INVALID_CHARACTER_ERR

class NoDataAllowedErr(DOMException):
    code = NO_DATA_ALLOWED_ERR

class NoModificationAllowedErr(DOMException):
    code = NO_MODIFICATION_ALLOWED_ERR

class NotFoundErr(DOMException):
    code = NOT_FOUND_ERR

class NotSupportedErr(DOMException):
    code = NOT_SUPPORTED_ERR

class InuseAttributeErr(DOMException):
    code = INUSE_ATTRIBUTE_ERR

class InvalidStateErr(DOMException):
    code = INVALID_STATE_ERR

class SyntaxErr(DOMException):
    code = SYNTAX_ERR

class InvalidModificationErr(DOMException):
    code = INVALID_MODIFICATION_ERR

class NamespaceErr(DOMException):
    code = NAMESPACE_ERR

class InvalidAccessErr(DOMException):
    code = INVALID_ACCESS_ERR

class ValidationErr(DOMException):
    code = VALIDATION_ERR


class _DOMList(list):
    """ Generic List """
    def length():
        def fget(self): return len(self)
        return locals()
    length = property(**length())

    def item(self, i):
        try: return self[i]
        except IndexError: return None


class DOMStringList(_DOMList):
    """
    DOM String List

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#DOMStringList
    """

class NameList(_DOMList):
    """ 
    Name List

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#NameList
    """
    def getName(self, i):
        try: return self[i]
        except IndexError: return None

    def getNamespaceURI(self, i):
        return None

    def containsNS(self, ns, name):
        if ns: return False
        return self.contains(name)

class NodeList(_DOMList):
    """
    Node List

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-536297177
    """

class DOMImplementationList(_DOMList):
    """
    DOM Implementation List

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#DOMImplementationList
    """

class DOMImplementationSource(object):
    """
    DOM Implementation Source

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#DOMImplementationSource
    """
    def getDOMImplementation(self, features):
        raise NotImplementedError
    def getDOMImplementationList(self, features):
        raise NotImplementedError

class DOMImplementation(object):
    """
    DOM Implementation

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-102161490
    """
    def hasFeature(self, feature, version):
        raise NotSupportedErr

    def createDocumentType(self, qualifiedName, publicId=None, systemId=None):
        raise NotSupportedErr

    def createDocument(self, namespaceURI, qualifiedName, doctype):
        raise NotSupportedErr

    def getFeature(self, feature, version):
        raise NotSupportedErr

class NamedNodeMap(dict):
    """ 
    DOM Named Node Map 

    This class is a Python dictionary that also supports the 
    DOM Named Node Map interface.  It is used for the `attributes`
    attribute on Node.  Since LaTeX's attributes are actually 
    objects instead of strings, a `parentNode` was also added to
    the instance structure.  Whenever a new object is added to
    the dictionary, the object's parent is set to self.parentNode.

    """
    _parentNode = None
    _ownerDocument = None

    def parentNode():
        def fget(self):
            return self._parentNode
        def fset(self, value):
            self._parentNode = value
            for value in self.values():
                if hasattr(value, 'parentNode'):
                    value.parentNode = value
        return locals()
    parentNode = property(**parentNode())

    def ownerDocument():
        def fget(self):
            return self._ownerDocument
        def fset(self, value):
            self._ownerDocument = value
            for value in self.values():
                if hasattr(value, 'ownerDocument'):
                    value.ownerDocument = value
        return locals()
    ownerDocument = property(**ownerDocument())

    def getNamedItem(self, name):
        return self.get(name)

    def setNamedItem(self, arg):
        self[arg.nodeName] = arg
        return arg

    def removeNamedItem(self, name):
        value = self[name]
        del self[name]
        return value

    def item(self, num):
        try: return self.values()[num]
        except IndexError: return None

    def length():
        def fget(self): return len(self)
        return locals()
    length = property(**length())

    def getNamedItemNS(self, ns, name):
        return self.getNamedItem(name)

    def setNamedItemNS(self, arg):
        return self.setNamedItem(arg)

    def removeNamedItemNS(self, ns, name):
        return self.removeNamedItem(name)

    def __setitem__(self, key, value):
        if isinstance(value, DocumentFragment):
            for item in value:
                if hasattr(item, 'parentNode'):
                    item.parentNode = self.parentNode
        elif hasattr(value, 'parentNode'):
            value.parentNode = self.parentNode
        dict.__setitem__(self, key, value)

    def update(self, other):
        for key, value in other.items():
            self[key] = value


class Node(_DOMList):
    """
    Node

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-1950641247
    """

    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_REFERENCE_NODE = 5
    ENTITY_NODE = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    DOCUMENT_FRAGMENT_NODE = 11
    NOTATION_NODE = 12

    DOCUMENT_POSITION_DISCONNECTED = 0x01
    DOCUMENT_POSITION_PRECEDING = 0x02
    DOCUMENT_POSITION_FOLLOWING = 0x04
    DOCUMENT_POSITION_CONTAINS = 0x08
    DOCUMENT_POSITION_CONTAINED_BY = 0x10
    DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC = 0x20

    namespaceURI = None
    prefix = None
    localName = None
    baseURI = None
  
    nodeName = None
    nodeValue = None
    nodeType = None
    parentNode = None
    attributes = None

    previousSibling = None 
    nextSibling = None

    _parentNode = None
    _ownerDocument = None

    def __init__(self, data=[]):
        _DOMList.__init__(self, data)
        self.attributes = NamedNodeMap()

    def firstChild(self):
        if self: return self[0]
    firstChild = property(firstChild)

    def lastChild(self):
        if self: return self[-1]
    lastChild = property(lastChild)

    def childNodes(self):
        return self
    childNodes = property(childNodes)

    def parentNode():
        def fget(self):
            return self._parentNode
        def fset(self, value):
            self.attributes.parentNode = self._parentNode = value
        return locals()
    parentNode = property(**parentNode())

    def ownerDocument():
        def fget(self):
            return self._ownerDocument
        def fset(self, value):
            self.attributes.ownerDocument = self._ownerDocument = value
            for item in self:
                if hasattr(item, 'ownerDocument'):
                    item.ownerDocument = value
        return locals()
    ownerDocument = property(**ownerDocument())

    def _resetPosition(self, i):
#       if i < 0 or i >= len(self):
#           return

        # Get current, previous, and next nodes
        current = self[i]
        next = previous = None
        if i > 0: previous = self[i-1]
        if i < (len(self)-1): next = self[i+1]

        if hasattr(current, 'previousSibling'):
            current.previousSibling = previous
            current.nextSibling = next
            current.parentNode = self
            current.ownerDocument = self.ownerDocument

        if previous is not None and hasattr(previous, 'nextSibling'):
            previous.nextSibling = current

        if next is not None and hasattr(next, 'previousSibling'):
            next.previousSibling = current

    def insertBefore(self, newChild, refChild):
        """ Insert 'newChild' before 'refChild' """
        # Remove newChild first if it is there
        for i, item in enumerate(self):
            if item is newChild:
                self.pop(i)
                break
        # Insert the new item
        for i, item in enumerate(self):
            if item is refChild:
                self.insert(i, newChild)
                return newChild
        raise NotFoundErr

    def replaceChild(self, newChild, oldChild):
        """ Replace 'newChild' with 'oldChild' """
        # Remove newChild first if it is there
        for i, item in enumerate(self):
            if item is newChild:
                self.pop(i)
                break
        # Do the replacement
        for i, item in enumerate(self):
            if item is oldChild:
                self.pop(i)
                self.insert(i, newChild)
                return oldChild
        raise NotFoundErr

    def removeChild(self, oldChild):
        """ Remove 'oldChild' from list of children """
        for i, item in enumerate(self):
            if item is oldChild:
                return self.pop(i)
        raise NotFoundErr

    def pop(self, index=None):
        last = False
        if index is None:
            last = True
            index = len(self) - 1
        elif index == (len(self)-1):
            last = True
        out = _DOMList.pop(self, index)
        if self:
            if last:
                self._resetPosition(len(self)-1)
            else:
                self._resetPosition(index)
        return out

    def append(self, newChild):
        """ Append node to child list """
        list.append(self, newChild) 
        self._resetPosition(len(self)-1)
#       if isinstance(newChild, DocumentFragment):
#           for item in newChild:
#               list.append(self, item)
#       else:
#           list.append(self, newChild) 
        return newChild

    def insert(self, i, newChild):
        """ Insert `newChild` into child list at position `i` """
        list.insert(self, i, newChild)
        self._resetPosition(i)
#       if isinstance(newChild, DocumentFragment):
#           for item in newChild:
#               list.insert(self, i, item)
#               i += 1
#       else:
#           list.insert(self, i, newChild)

#   def __setitem__(self, index, node):
#       start = index
#       if isinstance(index, slice):
#           start = slice.start
#       list.__delitem__(self, index)
#       if start >= len(self):
#           self.append(node)
#       else:
#           self.insert(start, node)

    def extend(self, other):
        for item in other:
            self.append(item)

    appendChild = append

    def hasChildNodes(self):
        """ Do we have any child nodes? """
        return not(not(len(self)))

    def cloneNode(self, deep=False):
        """ Clone the current node """
        node = type(self)()
        node.nodeName = self.nodeName
        node.nodeValue = self.nodeValue
        node.nodeType = self.nodeType
        node.parentNode = self.parentNode
        if deep:
            node.attributes = self.attributes.deepcopy()
            node[:] = [x.cloneNode(deep) for x in self[:]]
        else:
            node.attributes = self.attributes.copy()
            node[:] = self[:]
        return node 

    def normalize(self):
        pass

    def isSupported(self, feature, version):
        return True

    def hasAttributes(self):
        return not(not(self.attributes))

    def compareDocumentPosition(self, other):
        raise NotSupportedErr

    def textContent(self):
        output = []
        for item in self:
            if isinstance(item, basestring):
                output.append(item)
            else:
                output.append(item.textContent)
        return ''.join(output)
    textContent = property(textContent) 
 
    def isSameNode(self, other):
        """ Is this the same node as 'other'? """
        return other is self

    def lookupPrefix(self, ns):
        return None

    def isDefaultNamespace(self, ns):
        if ns is None: return True
        return False

    def lookupNamespaceURI(self, ns):
        return None

    def isEqualNode(self, arg):
        """ Is this node equivalent to 'other'? """
        return arg == self

    def getFeature(self, feature, version):
        return None

    def setUserData(self, key, data, handler=None):
        if not hasattr(self, 'userdata'):
            self.userdata = {}
        self.userdata[key] = data

    def getUserData(self, key):
        try: return self.userdata[key]
        except (AttributeError, KeyError): return None

class DocumentFragment(Node):
    """
    Document Fragment

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-B63ED1A3
    """
    nodeName = '#document-fragment'

class Document(Node):
    """
    Document

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#i-Document

    """

    elementClass = Node
    documentFragmentClass = DocumentFragment
    textNodeClass = None
    commentClass = None
    cdataSectionClass = None
    processingInstructionClass = None
    attributeClass = None
    entityReferenceClass = None

    nodeName = '#document'

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.doctype = None
        self.implementation = None
        self.documentElement = None
        self.inputEncoding = None
        self.xmlEncoding = None
        self.xmlStandalone = None
        self.xmlVersion = None
        self.strictErrorChecking = None
        self.documentURI = None
        self.domConfig = None

    def createElement(self, tagName):
        o = self.elementClass()
        o.nodeName = tagName
        return o

    def createDocumentFragment(self):
        return self.documentFragmentClass()
         
    def createTextNode(self, data):
        return self.textNodeClass(data)

    def createComment(self, data):
        return self.commentClass(data)

    def createCDATASection(self, data):
        return self.cdataSectionClass(data)
                         
    def createProcessingInstruction(self, target, data):
        return self.processingInstructionClass(data)

    def createAttribute(self, name):
        return self.attributeClass(name)
                   
    def createEntityReference(self, name):
        return self.entityReferenceClass(name)

    def getElementsByTagName(self, tagname):
        output = NodeList()
        if hasattr(self, 'attributes'):
            for item in self.attributes.values():
                if hasattr(item, 'tagName'):
                    if item.tagName == tagname:
                        output.append(item)
                if hasattr(item, 'getElementsByTagName'):
                    output += item.getElementsByTagName(tagname)
        for item in self:
            if hasattr(item, 'tagName'):
                if item.tagName == tagname:
                    output.append(item)
            if hasattr(item, 'getElementsByTagName'):
                output += item.getElementsByTagName(tagname) 
        return output

    def importNode(self, importedNode, deep=False):
        return importedNode.cloneNode(deep)
  
    def createElementNS(self, namespaceURI, qualifiedName):
        return self.createElement(qualifiedName)

    def createAttributeNS(self, namespaceURI, qualifiedName):
        return self.createAttribute(qualifiedName)

    def getElementsByTagNameNS(self, namespaceURI, localName):
        return self.getElementsByTagName(localName)

    def getElementById(self, elementId):
        if hasattr(self, 'attributes'):
            for item in self.attributes.values():
                if id(item) == elementId:
                    output.append(item)
                if hasattr(item, 'getElementsById'):
                    elem = item.getElementsById(tagname)
                    if elem is not None:
                        return elem
        for item in self:
            if id(item) == elementId:
                output.append(item)
            if hasattr(item, 'getElementsById'):
                elem = item.getElementsById(tagname) 
                if elem is not None:
                    return elem

    def adoptNode(self, source):
        if source.parentNode:
            for i, item in enumerate(source.parentNode):
                if item is source:
                    source.parentNode.pop(i)
        self.append(source)
        return source

    def normalizeDocument(self):
        pass

    def renameNode(self, n, namespaceURI, qualifiedName):
        raise NotImplementedError


class CharacterData(Node):
    """
    Character Data

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-FF21A306 
    """

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.data = ''

    def length():
        def fget(self): return len(self.data)
        return locals()
    length = property(**length())

    def substringData(self, offset, count):
        return self.data[offset:offset+count]

    def appendData(self, arg):
        self.data += arg

    def insertData(self, offset, arg):
        d = list(self.data)
        d.insert(offset, arg)
        self.data = ''.join(d) 

    def deleteData(self, offset, count):
        d = list(self.data)
        del d[offset:offset+count]
        self.data = ''.join(d) 
        
    def replaceData(self, offset, count, arg):
        d = list(self.data)
        del d[offset:offset+count]
        if offset >= len(d): d.append(arg)
        else: d.insert(offset, arg)
        self.data = ''.join(d) 

class Attr(Node):
    """
    Attr

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-637646024
    """

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.name = None
        self.specified = None
        self.value = None
        self.ownerElement = None
        self.schemaTypeInfo = None
        self.isId = None

    def nodeName():
        def fget(self): return self.name
        def fset(self, value): self.name = value
        return locals()
    nodeName = property(**nodeName())

    def nodeValue():
        def fget(self): return self.value
        def fset(self, value): self.value = value
        return locals()
    nodeValue = property(**nodeValue())

class Element(Node):
    """
    Element

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-745549614
    """
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.attributes = NamedNodeMap()
        self.attributes.parentNode = self

    def tagName():
        def fget(self): return self.nodeName
        def fset(self, value): self.nodeName = value
        return locals()
    tagName = property(**tagName())
        
    def getAttribute(self, name):
        try: return self.attributes[name]
        except KeyError: return None

    def setAttribute(self, name, value):
        attr = Attr() 
        attr.name = name
        attr.value = value
        self.setAttributeNode(attr)

    def removeAttribute(self, name):
        try: del self.attributes[name]
        except KeyError: pass

    getAttributeNode = getAttribute

    def setAttributeNode(self, newAttr):
        return self.setAttribute(newAttr.name, newAttr)

    def removeAttributeNode(self, oldAttr):
        self.removeAttribute(oldAttr.name)

    def getElementsByTagName(self, name):
        return _getElementsByTagName(self, name)

    def getAttributeNS(self, namespaceURI, localName):
        return self.getAttribute(localName)

    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        return self.setAttribute(self, qualifiedName, value)

    def removeAttributeNS(self, namespaceURI, localName):
        return self.removeAttribute(localName)

    def getAttributeNodeNS(self, namespaceURI, localName):
        return self.getAttributeNode(localName)

    setAttributeNodeNS = setAttributeNode
  
    def getElementsByTagNameNS(self, namespaceURI, localName):
        return _getElementsByTagName(localName)

    def hasAttribute(self, name):
        return self.attributes.has_key(name)

    def hasAttributeNS(self, namespaceURI, localName):
        return self.hasAttribute(localName)

    def setIdAttribute(self, name, isId=True):
        try: self.attributes[name].isId = isId
        except KeyError: raise NotFoundErr

    def setIdAttributeNS(self, namespaceURI, localName, isId=True):
        self.setIdAttribute(localName, isId)

    def setIdAttributeNode(self, idAttr, isId=True):
        self.setIdAttribute(idAttr.name, isId)


class Text(CharacterData):
    """
    Text

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-1312295772
    """
    nodeName = '#text'

    def nodeValue():
        def fget(self): return self.data
        def fset(self, value): self.data = value
        return locals()
    nodeValue = property(**nodeValue())

    def splitText(self, offset):
        if offset > len(self):
            raise IndexSizeErr
        begin = self.data[:offset]
        end = self.data[offset:]
        self.data = begin
        return end
                                        
    def isElementContentWhitespace():
        def fget(self):
            return not(self.textContent.strip())
        return locals()
    isElementContentWhitespace = property(**isElementContentWhitespace())

    def wholeText():
        def fget(self):
            return self.parentNode.textContent
        return locals()
    wholeText = property(**wholeText())

    def replaceWholeText(self, content):
        raise NotImplementedError

class Comment(CharacterData):
    """
    Comment

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-1728279322
    """
    nodeName = '#comment'

    def nodeValue():
        def fget(self): return self.data
        def fset(self, value): self.data = value
        return locals()
    nodeValue = property(**nodeValue())
 
class TypeInfo(object):
    """
    Type Info

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#TypeInfo
    """

    # DerivationMethods
    DERIVATION_RESTRICTION = 0x00000001
    DERIVATION_EXTENSION = 0x00000002
    DERIVATION_UNION = 0x00000004
    DERIVATION_LIST = 0x00000008

    def __init__(self):
        self.typeName = None
        self.typeNamespace = None

    def isDerivedFrom(self, typeNamespaceArg, typeNameArg, derivationMethod):
        raise NotImplementedError

class UserDataHandler(object):
    """
    User Data Handler

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#UserDataHandler
    """

    # OperationType
    NODE_CLONED = 1;
    NODE_IMPORTED = 2;
    NODE_DELETED = 3;
    NODE_RENAMED = 4;
    NODE_ADOPTED = 5;

    def handle(self, operation, key, data, src, dst):
        raise NotImplementedError

class DOMError(object):
    """
    DOM Error

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ERROR-Interfaces-DOMError
    """

    # ErrorSeverity
    SEVERITY_WARNING = 1
    SEVERITY_ERROR = 2
    SEVERITY_FATAL_ERROR = 3

    def __init__(self):
        self.severity = None
        self.message = None
        self.type = None
        self.relatedException = None
        self.relatedData = None
        self.location = None

class DOMErrorHandler(object):
    """
    DOM Error Handler

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ERROR-Interfaces-DOMErrorHandler
    """
    def handleError(self, error):
        raise NotImplementedError

class DOMLocator(object):
    """
    DOM Locator

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#Interfaces-DOMLocator
    """
    def __init__(self):
        self.lineNumber = 0
        self.columnNumber = 0
        self.byteOffset = 0
        self.utf16Offset = 0
        self.relatedNode = None
        self.uri = None

class DOMConfiguration(dict):
    """
    DOM Configuration

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#DOMConfiguration
    """

    def __init__(self, data={}):
        dict.__init__(self, data)
        self['canonical-form'] = False
        self['cdata-sections'] = True
        self['check-character-normalization'] = False
        self['comments'] = True
        self['datatype-normalization'] = False
        self['element-content-whitespace'] = True
        self['entities'] = True
        self['error-handler'] = DOMErrorHandler()
        self['infoset'] = True
        self['namespaces'] = True
        self['namespace-declarations'] = True
        self['normalize-characters'] = False
        self['schema-location'] = None
        self['schema-type'] = None
        self['split-cdata-sections'] = True
        self['validate'] = False
        self['validate-if-schema'] = False
        self['well-formed'] = True

    def parameterNames():
        def fget(self):
            return self.keys()
        return locals()
    parameterNames = property(**parameterNames())

    def setParameter(self, name, value):
        if self.has_key(name):
            raise NotFoundErr
        self[name] = value

    def getParameter(self, name):
        try: return self[name]
        except KeyError: raise NotFoundErr

    def canSetParameter(self, name, value):
        return True

class CDATASection(Text):
    """
    CDATA Section

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-667469212
    """
    nodeName = '#cdata-section'

    def nodeValue():
        def fget(self): return self.data
        def fset(self, value): self.data = value
        return locals()
    nodeValue = property(**nodeValue())

class DocumentType(Node):
    """
    Document Type

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-412266927
    """
    
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.name = None
        self.entities = None
        self.notations = None
        self.publicId = None
        self.systemId = None
        self.internalSubset = None

    def nodeName():
        def fget(self): return self.name
        def fset(self, value): self.name = value
        return locals()
    nodeName = property(**nodeName())

class Notation(Node):
    """
    Notation

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-5431D1B9
    """
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.publicId = None
        self.systemId = None

class Entity(Node):
    """
    Entity

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-527DCFF2
    """
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.publicId = None
        self.systemId = None
        self.notationName = None
        self.inputEncoding = None
        self.xmlEncoding = None
        self.xmlVersion = None

class EntityReference(Node):
    """
    Entity Reference

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-11C98490
    """

class ProcessingInstruction(Node):
    """
    Processing Instruction

    http://www.w3.org/TR/2004/REC-DOM-Level-3-Core-20040407/core.html#ID-1004215813
    """
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.target = None
        self.data = None

    def nodeName():
        def fget(self): return self.target
        def fset(self, value): self.target = value
        return locals()
    nodeName = property(**nodeName())

    def nodeValue():
        def fget(self): return self.data
        def fset(self, value): self.data = value
        return locals()
    nodeValue = property(**nodeValue())
