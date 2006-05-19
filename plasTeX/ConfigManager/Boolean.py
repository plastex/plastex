#!/usr/bin/env python

from Generic import *
from plasTeX.ConfigManager import InvalidOptionError

class BooleanParser(GenericParser): pass

class BooleanOption(BooleanParser, GenericOption):
   """ Boolean configuration option """

   def cast(self, data):
      if data is None: return

      values = {'on':1,'off':0,'true':1,'false':0,'yes':1,'no':0}

      try:
         bool = int(data)
         if bool in [0, 1]:
             return bool
      except:
         try:
            bool = values[str(data).lower()]
            if bool in [0, 1]:
                return bool
         except: pass
      name = self.name
      if self.actual: name = self.actual
      raise InvalidOptionError(name, data, type='boolean')

   def validate(self, data):
      return self.cast(data)

   def defaultValue(self):
      if self.default:
          return 'yes'
      return 'no'

   def __repr__(self):
      """ Return command-line syntax as entered """
      if self.actual: return self.actual
      options = self.getPossibleOptions()
      negative = [x.replace('!','',1) for x in options if x.startswith('!')]
      positive = [x for x in options if not x.startswith('!')]
      if self.data and positive:
         return positive[0]
      elif not(self.data) and negative:
         return negative[0]
      return ''

   def __str__(self):
      """ Return string representation of the current option value """
      value = self.getValue()
      if value is not None:
         if value: return 'on'
         else: return 'off'
      return ''

   def acceptsArgument(self):
      """ Return a boolean indicating if the option accepts an argument """
      return 0

   def requiresArgument(self):
      """ Return a boolean indicating if the option requires an argument """
      return 0


class BooleanArgument(GenericArgument, BooleanOption):
   """ Boolean command-line option """
