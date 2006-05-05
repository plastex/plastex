#!/usr/bin/env python

import re
from Generic import GenericArgument
from String import StringOption
from plasTeX.ConfigManager import GetoptError


class UnknownCompoundGroup(GetoptError):
    """ Exception for an unknown grouping character used for a compound """  
    def __init__(self, msg=''):
        GetoptError.__init__(self, msg, '')


class CompoundParser:
   """
   Compound configuration option

   Compound options are options grouped by a pair of grouping characters
   (e.g. '()', '[]', '{}', '<>').  The content between the grouping
   characters can be anything including other command line arguments.
   All content between the grouping characters will be unparsed.

   """

   def getArgument(self, args):
      """ Parse a compound argument """

      groups = {'<':'>', '(':')', '[':']', '{':'}'}

      # Determine grouping characters
      begin = args[0].strip()[0]
      try:
          end = groups[args[0].strip()[0]]
      except KeyError, info:
          name = self.name
          if self.actual: name = self.actual
          raise UnknownCompoundGroup(
                "Unknown compound grouping character '%s' in option '%s'" % (info, name))

      new_args = []
      while args and args[0].strip()[-1] != end:
          new_args.append(args.pop(0).strip())
      new_args.append(args.pop(0).strip())

      # Strip delimiters
      new_args[0] = new_args[0][1:]
      new_args[-1] = new_args[-1][:-1]

      output = []
      for item in new_args:
          item = item.strip()
          if not item:
              continue
          if ' ' in item:
              item = "'%s'" % item
          output.append(item)
      
      value = '%s %s %s' % (begin, ' '.join(output), end)

      return value, args


class CompoundOption(CompoundParser, StringOption):
   """
   Compound configuration option

   Compound options are options grouped by a pair of grouping characters
   (e.g. '()', '[]', '{}', '<>').  The content between the grouping
   characters can be anything including other command line arguments.
   All content between the grouping characters will be unparsed.

   """
   REGEX = re.compile(r'^(\s*(?:\(|\[|\{|\<)\s*)(.*)(\s*(?:\)|\]|\}|\]>)\s*)$')
   synopsis = "[ ... ]"

   def cast(self, data):
      if data is None: return
      return '%s %s %s' % (self.REGEX.sub(r'\1', str(data).strip()).strip(),
                           self.REGEX.sub(r'\2', str(data).strip()),
                           self.REGEX.sub(r'\3', str(data).strip()).strip())

   def __len__(self):
      if self.data is None:
          return 0
      else:
          return len(self.data)

   def __iadd__(self, other):
      if callable(self.callback):
         other = self.callback(self.cast(other))

      if self.data is None:
         self.data = self.cast(other)
      else:
         other = self.REGEX.sub(r'\2', self.cast(other)).strip()
         self.data = self.REGEX.sub(r'\1\2 %s \3' % other, self.data)

      return self

class CompoundArgument(GenericArgument, CompoundOption):
   """ Compound command-line argument """
