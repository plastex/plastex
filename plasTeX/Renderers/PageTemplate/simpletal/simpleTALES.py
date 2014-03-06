""" simpleTALES Implementation

		Copyright (c) 2005 Colin Stewart (http://www.owlfish.com/)
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
		
		The classes in this module implement the TALES specification, used
		by the simpleTAL module.
		
		Module Dependencies: logging
"""

import types, sys, re

try:
	import logging
except:
	import DummyLogger as logging
	
import simpleTAL
from plasTeX.Renderers.PageTemplate import simpletal

__version__ = simpletal.__version__

DEFAULTVALUE = "This represents a Default value."

class PathNotFoundException (Exception):
	pass
	

class ContextContentException (Exception):
	""" This is raised when invalid content has been placed into the Context object.
		For example using non-ascii characters instead of Unicode strings.
	"""
	pass
	
PATHNOTFOUNDEXCEPTION = PathNotFoundException()

class ContextVariable:
	def __init__ (self, value = None):
		self.ourValue = value
		
	def value (self, currentPath=None):
		if (callable (self.ourValue)):
			return apply (self.ourValue, ())
		return self.ourValue
		
	def rawValue (self):
		return self.ourValue
		
	def __str__ (self):
		return repr (self.ourValue)
		
class RepeatVariable (ContextVariable):
	""" To be written"""
	def __init__ (self, sequence):
		ContextVariable.__init__ (self, 1)
		self.sequence = sequence	
		self.position = 0	
		self.map = None
		
	def value (self, currentPath=None):
		if (self.map is None):
			self.createMap()
		return self.map
		
	def rawValue (self):
		return self.value()
		
	def getCurrentValue (self):
		return self.sequence [self.position]
		
	def increment (self):
		self.position += 1
		if (self.position == len (self.sequence)):
			raise IndexError ("Repeat Finished")
		
	def createMap (self):
		self.map = {}
		self.map ['index'] = self.getIndex
		self.map ['number'] = self.getNumber
		self.map ['even'] = self.getEven
		self.map ['odd'] = self.getOdd
		self.map ['start'] = self.getStart
		self.map ['end'] = self.getEnd
		# TODO: first and last need to be implemented.
		self.map ['length'] = len (self.sequence)
		self.map ['letter'] = self.getLowerLetter
		self.map ['Letter'] = self.getUpperLetter
		self.map ['roman'] = self.getLowerRoman
		self.map ['Roman'] = self.getUpperRoman
	
	# Repeat implementation goes here
	def getIndex (self):
		return self.position
		
	def getNumber (self):
		return self.position + 1
		
	def getEven (self):
		if ((self.position % 2) != 0):
			return 0
		return 1
		
	def getOdd (self):
		if ((self.position % 2) == 0):
			return 0
		return 1
		
	def getStart (self):
		if (self.position == 0):
			return 1
		return 0
		
	def getEnd (self):
		if (self.position == len (self.sequence) - 1):
			return 1
		return 0
		
	def getLowerLetter (self):
		result = ""
		nextCol = self.position
		if (nextCol == 0):
			return 'a'
		while (nextCol > 0):
			nextCol, thisCol = divmod (nextCol, 26)
			result = chr (ord ('a') + thisCol) + result
		return result
	
	def getUpperLetter (self):
		return self.getLowerLetter().upper()
		
	def getLowerRoman (self):
		romanNumeralList = (('m', 1000)
						   ,('cm', 900)
						   ,('d', 500)
						   ,('cd', 400)
						   ,('c', 100)
						   ,('xc', 90)
						   ,('l', 50)
						   ,('xl', 40)
						   ,('x', 10)
						   ,('ix', 9)
						   ,('v', 5)
						   ,('iv', 4)
						   ,('i', 1)
						   )
		if (self.position > 3999):
			# Roman numbers only supported up to 4000
			return ' '
		num = self.position + 1
		result = ""
		for roman, integer in romanNumeralList:
			while (num >= integer):
				result += roman
				num -= integer
		return result
		
	def getUpperRoman (self):
		return self.getLowerRoman().upper()
		
class IteratorRepeatVariable (RepeatVariable):
	def __init__ (self, sequence):
		RepeatVariable.__init__ (self, sequence)
		self.curValue = None
		self.iterStatus = 0
	
	def getCurrentValue (self):
		if (self.iterStatus == 0):
			self.iterStatus = 1
			try:
				self.curValue = self.sequence.next()
			except StopIteration, e:
				self.iterStatus = 2
				raise IndexError ("Repeat Finished")
		return self.curValue
		
	def increment (self):
		# Need this for the repeat variable functions.
		self.position += 1
		try:
			self.curValue = self.sequence.next()
		except StopIteration, e:
			self.iterStatus = 2
			raise IndexError ("Repeat Finished")
			
	def createMap (self):
		self.map = {}
		self.map ['index'] = self.getIndex
		self.map ['number'] = self.getNumber
		self.map ['even'] = self.getEven
		self.map ['odd'] = self.getOdd
		self.map ['start'] = self.getStart
		self.map ['end'] = self.getEnd
		# TODO: first and last need to be implemented.
		self.map ['length'] = sys.maxint
		self.map ['letter'] = self.getLowerLetter
		self.map ['Letter'] = self.getUpperLetter
		self.map ['roman'] = self.getLowerRoman
		self.map ['Roman'] = self.getUpperRoman
		
	def getEnd (self):
		if (self.iterStatus == 2):
			return 1
		return 0
		
class PathFunctionVariable (ContextVariable):
	def __init__ (self, func):
		ContextVariable.__init__ (self, value = func)
		self.func = func
		
	def value (self, currentPath=None):
		if (currentPath is not None):
			index, paths = currentPath
			result = ContextVariable (apply (self.func, ('/'.join (paths[index:]),)))
			# Fast track the result
			raise result
			
class CachedFuncResult (ContextVariable):
	def value (self, currentPath=None):
		try:
			return self.cachedValue
		except:
			self.cachedValue = ContextVariable.value (self)
		return self.cachedValue
	
	def clearCache (self):
		try:
			del self.cachedValue
		except:
			pass
		
class PythonPathFunctions:
	def __init__ (self, context):
		self.context = context
                self.pathHandler = {}
                self.pathHandler['path'] = self.path
                self.pathHandler['string'] = self.string
                self.pathHandler['exists'] = self.exists
                self.pathHandler['nocall'] = self.nocall
                self.pathHandler['test'] = self.test
                self.pathHandler['stripped'] = self.stripped
		
	def path (self, expr):
		return self.context.evaluatePath (expr)
			
	def string (self, expr):
		return self.context.evaluateString (expr)

        def stripped (self, expr):
                return re.sub(r'</?\w+[^>]*>', r'', context.evaluateString (expr))
	
	def exists (self, expr):
		return self.context.evaluateExists (expr)
			
	def nocall (self, expr):
		return self.context.evaluateNoCall (expr)
			
	def test (self, *arguments):
		if (len (arguments) % 2):
			# We have an odd number of arguments - which means the last one is a default
			pairs = arguments[:-1]
			defaultValue = arguments[-1]
		else:
			# No default - so use None
			pairs = arguments
			defaultValue = None
			
		index = 0
		while (index < len (pairs)):
			test = pairs[index]
			index += 1
			value = pairs[index]
			index += 1
			if (test):
				return value
				
		return defaultValue

class Context:
	def __init__ (self, options=None, allowPythonPath=0):
		self.allowPythonPath = allowPythonPath
		self.globals = {}
		self.locals = {}
		self.localStack = []
		self.repeatStack = []
		self.populateDefaultVariables (options)
		self.log = logging.getLogger ("simpleTALES.Context")
		self.true = 1
		self.false = 0
		self.pythonPathFuncs = PythonPathFunctions (self)
                self.prefixHandlers = {}
                self.prefixHandlers['path'] = self.evaluatePath
                self.prefixHandlers['exists'] = self.evaluateExists
                self.prefixHandlers['nocall'] = self.evaluateNoCall
                self.prefixHandlers['not'] = self.evaluateNot
                self.prefixHandlers['string'] = self.evaluateString
                self.prefixHandlers['python'] = self.evaluatePython
                self.prefixHandlers['stripped'] = self.evaluateStripped
		
	def addRepeat (self, name, var, initialValue):
		# Pop the current repeat map onto the stack
		self.repeatStack.append (self.repeatMap)
		self.repeatMap = self.repeatMap.copy()
		self.repeatMap [name] = var
		# Map this repeatMap into the global space
		self.addGlobal ('repeat', self.repeatMap)
		
		# Add in the locals
		self.pushLocals()
		self.setLocal (name, initialValue)
		
	def removeRepeat (self, name):
		# Bring the old repeat map back
		self.repeatMap = self.repeatStack.pop()
		# Map this repeatMap into the global space
		self.addGlobal ('repeat', self.repeatMap)
		
	def addGlobal (self, name, value):
		self.globals[name] = value
		
	def pushLocals (self):
		# Push the current locals onto a stack so that we can safely over-ride them.
		self.localStack.append (self.locals)
		self.locals = self.locals.copy()
				
	def setLocal (self, name, value):
		# Override the current local if present with the new one
		self.locals [name] = value
		
	def popLocals (self):
		self.locals = self.localStack.pop()
		
	def evaluate (self, expr, originalAtts = None):
		# Returns a ContextVariable
		#self.log.debug ("Evaluating %s" % expr)
		if (originalAtts is not None):
			# Call from outside
			self.globals['attrs'] = originalAtts
			suppressException = 1
		else:
			suppressException = 0
			
		# Supports path, exists, nocall, not, and string
		expr = expr.strip ()
		try:
                        for key, function in self.prefixHandlers.items():
                                if expr.startswith (key+':'):
                                        return function (expr[len(key)+1:].lstrip ())
			else:
				# Not specified - so it's a path
				return self.evaluatePath (expr)
		except PathNotFoundException, e:
			if (suppressException):
				return None
			raise e

        def evaluateStripped(self, expr):
                if '${' not in expr:
                        expr = '${%s}' % expr
                return re.sub(r'</?\w+[^>]*>', r'', self.evaluateString (expr))
		
	def evaluatePython (self, expr):
		if (not self.allowPythonPath):
			self.log.warn ("Parameter allowPythonPath is false.  NOT Evaluating python expression %s" % expr)
			return self.false
		#self.log.debug ("Evaluating python expression %s" % expr)
		
		globals={}
		for name, value in self.globals.items():
			if (isinstance (value, ContextVariable)): value = value.rawValue()
			globals [name] = value
                for key, value in self.pythonPathFuncs.pathHandler.items():
                        globals [key] = value
			
		locals={}
		for name, value in self.locals.items():
			if (isinstance (value, ContextVariable)): value = value.rawValue()
			locals [name] = value
			
		try:
			result = eval(expr, globals, locals)
			if (isinstance (result, ContextVariable)):
				return result.value()
			return result
		except Exception, e:
			# An exception occured evaluating the template, return the exception as text
			self.log.warn ("Exception occurred evaluating python path, exception: " + str (e))
			return "Exception: %s" % str (e)

	def evaluatePath (self, expr):
		#self.log.debug ("Evaluating path expression %s" % expr)
		allPaths = expr.split ('|')
		if (len (allPaths) > 1):
			for path in allPaths:
				# Evaluate this path
				try:
					return self.evaluate (path.strip ())
				except PathNotFoundException, e:
					# Path didn't exist, try the next one
					pass
			# No paths evaluated - raise exception.
			raise PATHNOTFOUNDEXCEPTION
		else:
			# A single path - so let's evaluate it.
			# This *can* raise PathNotFoundException
			return self.traversePath (allPaths[0])
	
	def evaluateExists (self, expr):
		#self.log.debug ("Evaluating %s to see if it exists" % expr)
		allPaths = expr.split ('|')
		# The first path is for us
		# Return true if this first bit evaluates, otherwise test the rest
		try:
			result = self.traversePath (allPaths[0], canCall = 0)
			return self.true
		except PathNotFoundException, e:
			# Look at the rest of the paths.
			pass
			
		for path in allPaths[1:]:
			# Evaluate this path
			try:
				pathResult = self.evaluate (path.strip ())
				# If this is part of a "exists: path1 | exists: path2" path then we need to look at the actual result.
				if (pathResult):
					return self.true
			except PathNotFoundException, e:
				pass
		# If we get this far then there are *no* paths that exist.
		return self.false
			
	def evaluateNoCall (self, expr):
		#self.log.debug ("Evaluating %s using nocall" % expr)
		allPaths = expr.split ('|')
		# The first path is for us
		try:
			return self.traversePath (allPaths[0], canCall = 0)
		except PathNotFoundException, e:
			# Try the rest of the paths.
			pass
			
		for path in allPaths[1:]:
			# Evaluate this path
			try:
				return self.evaluate (path.strip ())
			except PathNotFoundException, e:
				pass
		# No path evaluated - raise error
		raise PATHNOTFOUNDEXCEPTION
			
	def evaluateNot (self, expr):
		#self.log.debug ("Evaluating NOT value of %s" % expr)
		
		# Evaluate what I was passed
		try:
			pathResult = self.evaluate (expr)
		except PathNotFoundException, e:
			# In SimpleTAL the result of "not: no/such/path" should be TRUE not FALSE.
			return self.true
			
		if (pathResult is None):
			# Value was Nothing
			return self.true
		if (pathResult == DEFAULTVALUE):
			return self.false
		try:
			resultLen = len (pathResult)
			if (resultLen > 0):
				return self.false
			else:
				return self.true
		except:
			# Not a sequence object.
			pass
		if (not pathResult):
			return self.true
		# Everything else is true, so we return false!
		return self.false
		
	def evaluateString (self, expr):
		#self.log.debug ("Evaluating String %s" % expr)
		result = ""
		skipCount = 0
		for position in xrange (0,len (expr)):
			if (skipCount > 0):
				skipCount -= 1
			else:
				if (expr[position] == '$'):
					try:
						if (expr[position + 1] == '$'):
							# Escaped $ sign
							result += '$'
							skipCount = 1
						elif (expr[position + 1] == '{'):
							# Looking for a path!
							endPos = expr.find ('}', position + 1)
							if (endPos > 0):
								path = expr[position + 2:endPos]
								# Evaluate the path - missing paths raise exceptions as normal.
								try:
									pathResult = self.evaluate (path)
								except PathNotFoundException, e:
									# This part of the path didn't evaluate to anything - leave blank
									pathResult = u''
								if (pathResult is not None):
									if (isinstance (pathResult, types.UnicodeType)):
										result += pathResult
									else:
										# THIS IS NOT A BUG!
										# Use Unicode in Context if you aren't using Ascii!
										result += unicode (pathResult)
								skipCount = endPos - position 
						else:
							# It's a variable
							endPos = expr.find (' ', position + 1)
							if (endPos == -1):
								endPos = len (expr)
							path = expr [position + 1:endPos]
							# Evaluate the variable - missing paths raise exceptions as normal.
							try:
								pathResult = self.traversePath (path)
							except PathNotFoundException, e:
								# This part of the path didn't evaluate to anything - leave blank
								pathResult = u''
							if (pathResult is not None):
								if (isinstance (pathResult, types.UnicodeType)):
										result += pathResult
								else:
									# THIS IS NOT A BUG!
									# Use Unicode in Context if you aren't using Ascii!
									result += unicode (pathResult)
							skipCount = endPos - position - 1
					except IndexError, e:
						# Trailing $ sign - just suppress it
						self.log.warn ("Trailing $ detected")
						pass
				else:
					result += expr[position]
		return result
					
	def traversePath (self, expr, canCall=1):
		# canCall only applies to the *final* path destination, not points down the path.
		# Check for and correct for trailing/leading quotes
		if (expr.startswith ('"') or expr.startswith ("'")):
			if (expr.endswith ('"') or expr.endswith ("'")):
				expr = expr [1:-1]
			else:
				expr = expr [1:]
		elif (expr.endswith ('"') or expr.endswith ("'")):
			expr = expr [0:-1]
		pathList = expr.split ('/')
		
		path = pathList[0]
		if path.startswith ('?'):
			path = path[1:]
			if self.locals.has_key(path):
				path = self.locals[path]
				if (isinstance (path, ContextVariable)): path = path.value()
				elif (callable (path)):path = apply (path, ())
			
			elif self.globals.has_key(path):
				path = self.globals[path]
				if (isinstance (path, ContextVariable)): path = path.value()
				elif (callable (path)):path = apply (path, ())
				#self.log.debug ("Dereferenced to %s" % path)
		if self.locals.has_key(path):
			val = self.locals[path]
		elif self.globals.has_key(path):
			val = self.globals[path]  
		else:
			# If we can't find it then raise an exception
			raise PATHNOTFOUNDEXCEPTION
		index = 1
		for path in pathList[1:]:
			#self.log.debug ("Looking for path element %s" % path)
			if path.startswith ('?'):
				path = path[1:]
				if self.locals.has_key(path):
					path = self.locals[path]
					if (isinstance (path, ContextVariable)): path = path.value()
					elif (callable (path)):path = apply (path, ())
				elif self.globals.has_key(path):
					path = self.globals[path]
					if (isinstance (path, ContextVariable)): path = path.value()
					elif (callable (path)):path = apply (path, ())
				#self.log.debug ("Dereferenced to %s" % path)
			try:
				if (isinstance (val, ContextVariable)): temp = val.value((index,pathList))
				elif (callable (val)):temp = apply (val, ())
				else: temp = val
			except ContextVariable, e:
				# Fast path for those functions that return values
				return e.value()
                        except TypeError:
                                temp = val
				
			if (hasattr (temp, path)):
				val = getattr (temp, path)
			else:
				try:
					try:
						val = temp[path]
					except TypeError:
						val = temp[int(path)]
				except:
					#self.log.debug ("Not found.")
					raise PATHNOTFOUNDEXCEPTION
			index = index + 1
		#self.log.debug ("Found value %s" % str (val))
		if (canCall):
			try:
				if (isinstance (val, ContextVariable)): result = val.value((index,pathList))
				elif (callable (val)):result = apply (val, ())
				else: result = val
			except ContextVariable, e:
				# Fast path for those functions that return values
				return e.value()
		else:
			if (isinstance (val, ContextVariable)): result = val.realValue
			else: result = val
		return result
		
	def __str__ (self):
		return "Globals: " + str (self.globals) + "Locals: " + str (self.locals)
		
	def populateDefaultVariables (self, options):
		vars = {}
		self.repeatMap = {}
		vars['nothing'] = None
		vars['default'] = DEFAULTVALUE
		vars['options'] = options
		# To start with there are no repeats
		vars['repeat'] = self.repeatMap	
		vars['attrs'] = None
		
		# Add all of these to the global context
		for name in vars.keys():
			self.addGlobal (name,vars[name])
			
		# Add also under CONTEXTS
		self.addGlobal ('CONTEXTS', vars)

