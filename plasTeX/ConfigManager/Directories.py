#!/usr/bin/env python

import os
from String import StringOption
from Generic import InvalidOptionError, GenericArgument

class InputDirectoryOption(StringOption):
   """ Input directory configuration option """

   def validate(self, value):
      """ Make sure that the directory exists and is readable """
      value = StringOption.validate(self, value)
      name = self.name
      if self.actual: name = self.actual
      if not os.path.isdir(value):
         raise InvalidOptionError(name, value,
                                  "Directory does not exist")
      elif not os.access(value, os.R_OK):
         raise InvalidOptionError(name, value,
               "Directory is not readable, please check permissions")
      return value


class InputDirectoryArgument(GenericArgument, InputDirectoryOption):
   """ Input directory command-line argument """


class OutputDirectoryOption(StringOption):
   """ Output directory configuration option """

   def validate(self, value):
      """ Make sure that the directory can be written """
      value = StringOption.validate(self, value)
      name = self.name
      if self.actual: name = self.actual
      if os.path.isfile(value):
         raise InvalidOptionError(name, value,
                                  "Argument is a file, not a directory")
      elif os.path.isdir(value):
         if not os.access(value, os.W_OK):
            raise InvalidOptionError(name, value,
                  "Directory is not writable, please check the permissions")
      elif not os.path.isdir(value):
         try: os.makedirs(value, 0755)
         except OSError:
            raise InvalidOptionError(name, value,
                  "Could not create output directory")
      return value


class OutputDirectoryArgument(GenericArgument, OutputDirectoryOption):
   """ Output directory command-line argument """

