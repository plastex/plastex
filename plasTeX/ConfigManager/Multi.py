#!/usr/bin/env python

import os
from Generic import *
from plasTeX.ConfigManager import TooManyValues
from String import StringOption
from UserList import UserList


class MultiParser(GenericParser):

   def getArgument(self, args, range=None, delim=None, forcedarg=False):
      if range is None:
         range = self.range[:]
      if delim is None:
         delim = self.delim
      new_args, args = GenericParser.getArgument(self, args, range, delim, forcedarg=forcedarg)
      if type(new_args) in [list, tuple]:
         return new_args, args
      elif new_args is None:
         return [], args
      return [new_args], args


class MultiOption(MultiParser, GenericOption, UserList):
   """
   Multiple configuration option

   Multi options are options delimited by a specified character.  They
   can also be represented by an option specified multiple times.
   All other options, when specified more than once, will overwrite
   their previous value.  Multi options will append values each
   time an option is specified.

   """

   synopsis = 'val1,val2,...'

   def __init__(self, docstring=DEFAULTS['docstring'],
                      options=DEFAULTS['options'],
                      default=[],
                      optional=DEFAULTS['optional'],
                      values=DEFAULTS['values'],
                      category=DEFAULTS['category'],
                      callback=DEFAULTS['callback'],
                      synopsis=DEFAULTS['synopsis'],
                      environ=DEFAULTS['environ'],
                      registry=DEFAULTS['registry'],
                      delim=',',
                      range=[1,'*'],
                      mandatory=None,
                      name=DEFAULTS['name'],
                      source=DEFAULTS['source'],
                      template=StringOption):
      """
      Initialize a multi option

      This class is initialized with the same options as the
      Option class with one addition: delim.  The 'delim' argument
      specifies what the delimiter is for each item in the list.
      If the delimiter is 'None' or whitespace, each item in the
      list is assumed to be delimited by whitespace.

      """
      self.delim = delim
      self.range = range
      assert not issubclass(template, MultiOption), \
             'MultiOptions can not have a MultiOption as a template'
      assert issubclass(template, GenericOption), \
             'Templates must be a subclass of GenericOption'
      self.template = template(options=options,name=name,values=values)
      UserList.__init__(self, [])
      GenericOption.initialize(self, locals())

   def cast(self, arg):
      if arg is None: return []
      if type(arg) in [list,tuple]:
         return [self.template.cast(x) for x in list(arg)]
      delim = self.delim
      if not delim:
         delim = ' '
      return [self.template.cast(v.strip()) for v in str(arg).split(delim)
                                            if v.strip()]

   def getValue(self, value=None):
      """ Return value for option """
      if self.data and self.source & COMMANDLINE:
         return self.data

      if self.environ and os.environ.has_key(str(self.environ)):
         self.source = ENVIRONMENT
         self.file = None
         return self.cast(os.environ[str(self.environ)])

      if self.data:
         return self.data

      if self.default:
         self.source = BUILTIN
         self.file = None
         return self.default

      self.source = CODE
      self.file = None

      if value is None:
         return []

      return value

   def clearValue(self):
      """ Clear the value to be unset """
      self.data = []

   def __repr__(self):
      """ Print command-line representation """
      delim = self.delim
      if not delim:
         delim = ' '
      if self.data:
         option = self.actual
         if not option:
            args = self.getPossibleOptions()
            if args: option = args[0]
         if option:
            return str('%s %s' % (option, delim.join(self.data))).strip()
      return ''

   def __iadd__(self, other):
      """ Append a value to the list """
      if callable(self.callback):
         other = self.callback(self.cast(other))
      self.data += self.validate(other)
      range = self.validateRange(self.range)
      name = self.name
      if self.actual: name = self.actual
      if len(self.data) > range[1]:
         raise TooManyValues, "Expecting at most %s values for option '%s'." % (range[1], name)
      return self
 
   def validate(self, arg):
      """ Validate the value of the option """
      new_values = []
      for i in self.cast(arg):
#        new_values.append(self.checkValues(i))
         new_values.append(self.template.validate(i))
      return new_values

   def checkValues(self, value):
      return self.template.checkValues(value)
  
   def __str__(self):
      if self.delim and self.delim.strip():
         delim = '%s ' % self.delim
         return delim.join([str(x) for x in self.data])
      else:
         return '\n'.join([str(x) for x in self.data])
      return str(self.data)

   def acceptsArgument(self):
      """ Return a boolean indicating if the option accepts an argument """
      range = self.validateRange(self.range)
      return not(not(range[1]))

   def requiresArgument(self):
      """ Return a boolean indicating if the option requires an argument """
      range = self.validateRange(self.range)
      return not(not(range[0]))

   def setValue(self, value):
      """
      Set the value of the option to the given value

      Once the value is set to the new value and validated, the
      specified callback function is called with that value as its
      only argument.

      """
      if value is None or ((type(value) in [list,tuple]) and not(value)):
         self.clearValue()
      else:
         if callable(self.callback):
            value = self.callback(self.cast(value))
         self.data = self.validate(value)


class MultiArgument(GenericArgument, MultiOption):
   """ Multiple command-line option """

   def __init__(self, docstring=DEFAULTS['docstring'],
                      options=DEFAULTS['options'],
                      default=[],
                      optional=DEFAULTS['optional'],
                      values=DEFAULTS['values'],
                      category=DEFAULTS['category'],
                      callback=DEFAULTS['callback'],
                      synopsis=DEFAULTS['synopsis'],
                      environ=DEFAULTS['environ'],
                      registry=DEFAULTS['registry'],
                      delim=' ',
                      range=[1,'*'],
                      mandatory=None,
                      name=DEFAULTS['name'],
                      source=DEFAULTS['source'],
                      template=StringOption):
      """ Initialize a multi argument """
      self.delim = delim
      self.range = range
      assert not issubclass(template, MultiArgument), \
             'MultiArguments can not have a MultiArguments as a template'
      assert not issubclass(template, MultiOption), \
             'MultiOptions can not have a MultiOptions as a template'
      assert issubclass(template, GenericOption), \
             'Templates must be a subclass of GenericOption'
      self.template = template(options=options,name=name,values=values)
      UserList.__init__(self, [])
      GenericOption.initialize(self, locals())
