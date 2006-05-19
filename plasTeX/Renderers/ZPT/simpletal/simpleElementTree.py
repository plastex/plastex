""" ElementTree integration for SimpleTAL 

		Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
		All rights reserved.
		
		Redistribution and use in source and binary forms, with or without
		modification, are permitted provided that the following conditions
		are met:
		1. Redistributions of source code must retain the above copyright
		   notice, this list of conditions and the following disclaimer.
		2. Redistributions in binary form must reproduce the above copyright
		   notice, this list of conditions and the following disclaimer in the
		   documentation and/or other materials provided with the distribution.
		3. The name of the author may not be used to endorse or promote products
		   derived from this software without specific prior written permission.
		
		THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
		IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
		OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
		IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
		INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
		NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
		DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
		THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
		THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		The parseFile function in this module will return a Element object that
		implements simpleTALES.ContextVariable and makes XML documents available
		with the following path logic:
			- Accessing Element directly returns the Element.text value
			- Accessing Element/find and Element/findall passes the text
			  (up to attribute accessor) to the corresponding Element function
			- Accessing the Element@name access the attribute "name"
			- Accessing Element/anotherElement is a short-cut for 
			  Element/find/anotherElement
		
		Module Dependencies: simpleTALES, elementtree
"""

from elementtree import ElementTree
import simpleTALES

class SimpleElementTreeVar (ElementTree._ElementInterface, simpleTALES.ContextVariable):
	def __init__(self, tag, attrib):
		ElementTree._ElementInterface.__init__(self, tag, attrib)
		simpleTALES.ContextVariable.__init__(self)
		
	def value (self, pathInfo = None):
		if (pathInfo is not None):
			pathIndex, paths = pathInfo
			ourParams = paths[pathIndex:]
			attributeName = None
			if (len (ourParams) > 0):
				# Look for attribute index
				if (ourParams[-1].startswith ('@')):
					# Attribute lookup
					attributeName = ourParams [-1][1:]
					ourParams = ourParams [:-1]
			# Do we do a find?
			activeElement = self
			if len (ourParams) > 0:
				# Look for a find or findall first
				if (ourParams [0] == 'find'):
					# Find the element if possible
					activeElement = self.find ("/".join (ourParams [1:]))
				elif (ourParams [0] == 'findall'):
					# Short cut this
					raise simpleTALES.ContextVariable (self.findall ("/".join (ourParams[1:])))
				else:
					# Assume that we wanted to use find
					activeElement = self.find ("/".join (ourParams))
			# Did we find an element and are we looking for an attribute?
			if (attributeName is not None and activeElement is not None):
				attrValue = activeElement.attrib.get (attributeName, None)
				raise simpleTALES.ContextVariable (attrValue)
			
			# Just return the element
			if (activeElement is None):
				# Wrap it
				raise simpleTALES.ContextVariable (None)
			raise activeElement
		else:
			return self
			
	def __unicode__ (self):
		return self.text
		
	def __str__ (self):
		return str (self.text)

def parseFile (file):
	treeBuilder = ElementTree.TreeBuilder (element_factory = SimpleElementTreeVar)
	xmlTreeBuilder = ElementTree.XMLTreeBuilder (target=treeBuilder)
	
	if (not hasattr (file, 'read')):
		ourFile = open (file)
		xmlTreeBuilder.feed (ourFile.read())
		ourFile.close()
	else:
		xmlTreeBuilder.feed (file.read())
	
	return xmlTreeBuilder.close()
	