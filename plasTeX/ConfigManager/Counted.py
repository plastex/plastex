#!/usr/bin/env python

from Generic import GenericArgument
from Boolean import BooleanOption
from plasTeX.ConfigManager import InvalidOptionError, COMMANDLINE

class CountedOption(BooleanOption):
   """
   Counted configuration option

   This option is just like a boolean option except that the value
   of the option is the number of times that the option has been
   specified.  This is commonly used to set a verbosity or debugging
   level.  

   """

   def cast(self, data):
      if data is None: return

      values = {'on':1,'off':0,'true':1,'false':0,'yes':1,'no':0}

      # If this is from the command-line, increment or decrement
      if self.source & COMMANDLINE:
         initdata = self.data
         if self.data is None:
            initdata = 0
         if data:
            return max(0, initdata + 1)
         else:
            return max(0, initdata - 1)

      # If this is from any other source, set explicitly
      try:
         return max(0,int(data))
      except:
         try: return values[str(data).lower()]
         except: pass
      name = self.name
      if self.actual: name = self.actual
      raise InvalidOptionError(name, data, type='counted')

   def __str__(self):
      """ Return string representation of the current option value """
      value = self.getValue()
      if value == 1:
         return 'on'
      elif value == 0:
         return 'off'
      return str(value)

   def __repr__(self):
      """ Return command-line syntax as entered """
      if self.actual: return self.actual
      options = self.getPossibleOptions()
      negative = [x.replace('!','',1) for x in options if x.startswith('!')]
      positive = [x for x in options if not x.startswith('!')]
      if self.data and positive:
         return ' '.join(self.data*[positive[0]])
      elif not(self.data) and negative:
         return negative[0]
      return ''


class CountedArgument(GenericArgument, CountedOption):
   """ Counted command-line argument """
