#!/usr/bin/env python

import os
from String import StringOption
from Generic import InvalidOptionError, GenericArgument

class InputFileOption(StringOption):
   """ Input file configuration option """

   def validate(self, value):
      """ Make sure that the file exists and is readable """
      value = StringOption.validate(self, value)
      name = self.name
      if self.actual: name = self.actual
      # Check for special code for STDIN
      if value == '-':
         pass
      elif not os.path.isfile(value):
         raise InvalidOptionError(name, value, "File does not exist")
      elif not os.access(value, os.R_OK):
         raise InvalidOptionError(name, value,
               "File is not readable, please check permissions")
      return value


class InputFileArgument(GenericArgument, InputFileOption):
   """ Input file command-line argument """


class OutputFileOption(StringOption):
   """ Output file configuration option """

   def validate(self, value):
      """ Make sure that the file can be written """
      value = StringOption.validate(self, value)
      value = StringOption.validate(self, value)
      name = self.name
      # Check for special code for STDOUT
      if value == '-':
         pass
      elif os.path.isdir(value):
         raise InvalidOptionError(name, value,
                                  "Argument is a directory, not a file")
      elif os.path.isfile(value):
         if not os.access(value, os.W_OK):
            raise InvalidOptionError(name, value,
                  "File is not writable, please check the permissions")
      elif not os.path.dirname(value):
         pass
      elif not os.path.isdir(os.path.dirname(value)):
         try: os.makedirs(os.path.dirname(value), 0755)
         except OSError:
            raise InvalidOptionError(name, value,
                  "Could not create output directory for file")
      return value


class OutputFileArgument(GenericArgument, OutputFileOption):
   """ Output file command-line argument """
