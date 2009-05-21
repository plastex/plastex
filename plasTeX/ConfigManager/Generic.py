#!/usr/bin/env python

import re, os, copy
from plasTeX.ConfigManager import BUILTIN, CODE, ENVIRON, ENVIRONMENT
from plasTeX.ConfigManager import CODE, REGISTRY, COMMANDLINE, InvalidOptionError
from plasTeX.ConfigManager import ConfigManager, TooManyValues, TooFewValues

DEFAULTS = \
{
   'docstring': '',
   'options': None,
   'default': None,
   'optional': None,
   'values': None,
   'category': None,
   'name': None,
   'source': BUILTIN,
   'callback': None,
   'synopsis': None,
   'environ': None,
   'registry': None,
   'mandatory': None,
}

RegexType = type(re.compile(r''))


class GenericParser:

   def getOptionalArgument(self, args):
      return self.getArgument(args, range=[0,1])

   def _hasFollowingArgument(self, args, delim):
      """ Return boolean indicating the existence of another argument """
      if not ConfigManager.has_following_argument(args):
         return 0
      
      # No arguments left
      if not args:
         return 0

      # The current argument ends with the proper delimiter
      if args[0].strip()[-1] == delim:
         return 1

      # The next argument begins with the proper delimiter
      if len(args) > 1 and args[1].strip()[0] == delim:
         return 1

      return 0

   def getArgument(self, args, range=[1,1], delim=',', forcedarg=False):
      """ Parse argument """

      range = self.validateRange(range[:])

      # If we have an optional default, make sure that the range reflects that
      if range[0] < 2 and self.optional not in [None, [], ()]:
         range[0] = 0

      # No arguments left
      if not args:
         # Arguments that aren't mandatory can bail out now.
         if isinstance(self, GenericArgument) and not(self.mandatory):
            return None, args

         if range[0] > 0:
            name = self.name
            if self.actual: name = self.actual
            if range[0] != range[1]:
               raise TooFewValues, "Expecting at least %s value(s) for '%s'." % (range[0], name)
            elif range[0] == 1:
               raise TooFewValues, "Expecting a value for '%s'." % name
            else:
               raise TooFewValues, "Expecting %s values for '%s'." % (range[0], name)
         if self.optional:
            return self.optional, args
         else:
            return None, args

      # If delimiter is whitespace...
      if not delim or not str(delim).strip():
         new_args, args = self._getSpaceDelimitedArguments(args, range)
         delim = ' '

      else:
         new_args = []
         while self._hasFollowingArgument(args, delim):
            forcedarg = False

            # If the current argument ends with a delimiter
            if args[0].strip()[-1] == delim:
               new_args.append(args.pop(0).strip()[:-1])
   
            # If next argument is an isolated delimiter character
            elif len(args) > 1 and args[1].strip() == delim:
               new_args.append(args.pop(0).strip())
               args.pop(0)

            # If next argument begins with a delimiter
            else:
               if args[0].startswith(delim):
                   new_args.append(args.pop(0).strip()[1:])
               else:
                   new_args.append(args.pop(0).strip())
   
               # If this argument ends with a delimiter, rip it off
               # and put it back into the stream.
               if new_args[-1].endswith(delim):
                  args.insert(0, delim)
                  new_args[-1] = new_args[-1][:-1]

         # The following argument is always part of the list
         # unless the user accidentally put a trailing delimiter.
         if forcedarg or ConfigManager.has_following_argument(args):
            new_args.append(args.pop(0).strip())

         if new_args and new_args[-1].startswith(delim):
            new_args[-1] = new_args[-1][1:]

      if len(range) == 2 and range[0] == 1 and range[1] == 1:
          pass
      else:
          _args = []
          for i in new_args:
             _args += i.split(delim)
          new_args = _args

      # Check number of values
      name = self.name
      if self.actual: name = self.actual
      if len(new_args) < range[0]:
         plural = 's'
         if range[0] == 1:
            plural = ''
         raise TooFewValues, "Expecting at least %s value%s for '%s'." % (range[0], plural, name)
      elif len(new_args) > range[1]:
         raise TooManyValues, "Expecting at most %s values for '%s'." % (range[1], name)

      # Collapse argument list to a value if possible
      if len(new_args) < 1:
         if self.optional is not None:
            new_args = self.optional
         else:
            new_args = None
      elif len(new_args) < 2:
         new_args = new_args[0]

      return new_args, args 

   def _getSpaceDelimitedArguments(self, args, range=[1,'*']):
      """ Slurp up any following arguments that don't begin with '-' """
      minimum, maximum = self.validateRange(range)
      arg_len = len(args)
      new_args = []
      while ConfigManager.has_following_argument(args):
          new_args.append(args.pop(0))

      # If all of the remaining command line components are arguments as
      # opposed to options, don't return them as arguments to the
      # last option.
      if isinstance(self, GenericArgument):
          return new_args, args
      else:
          if len(new_args) == arg_len:
              minimum = min(len(new_args), minimum) 
              return new_args[:minimum], new_args[minimum:]
          else:
              return new_args, args

   def validateRange(self, range):
      # Verify that ranges are valid
      if range[0] == '*': range[0] = 10000
      if range[1] == '*': range[1] = 10000
      range[0] = max(range[0], 0)
      if range[0] > range[1]:
         range[0] = range[1]
      range[0] = int(range[0])
      range[1] = int(range[1])
      return range
 

class GenericOption(object):
   """
   Base class for configuration option classes

   All command line options must subclass from this one.  In addition,
   this is an abstract class.  It cannot be instantiated directly.

   """

   sort_order = ['category', 'options']
   synopsis = ''

   def __init__(self, docstring=DEFAULTS['docstring'],
                      options=DEFAULTS['options'],
                      default=DEFAULTS['default'],
                      optional=DEFAULTS['optional'],
                      values=DEFAULTS['values'],
                      category=DEFAULTS['category'],
                      callback=DEFAULTS['callback'],
                      synopsis=DEFAULTS['synopsis'],
                      environ=DEFAULTS['environ'],
                      registry=DEFAULTS['registry'],
                      mandatory=None,
                      name=DEFAULTS['name'],
                      source=DEFAULTS['source']):
      """
      Declare a command line option

      Instances of subclasses of CommandLineOption must be placed in
      a ConfigManager instance to be used.  See the documentation in
      ConfigManager for more details.

      Keyword Arguments:
      docstring -- a string in the format of Python documentation
         strings that describes the option and its usage.  The first
         line is assumed to be a one-line summary for the option.
         The following paragraphs are assumed to be a complete description
         of the option.  You can give a paragraph with the label
         'Valid Values:' that contains a short description of the
         values that are valid for the current option.  If this
         paragraph exists and an error is encountered while validating
         the option, this paragraph will be printed instead of the
         somewhat generic error message for that option type.

      options -- a string containing all possible variants of the
         option.  All variants should contain the '-', '--', etc. at
         the beginning.  For boolean options, the option can be preceded
         by a '!' to mean that the option should be turned OFF rather
         than ON which is the default.

      default -- value for the option to take if it isn't specified
         on the command line

      optional -- value for the option if it is given without a value.
         This is only used for options that normally take a value,
         but you also want a default that indicates that the option
         was given without a value.

      values -- valid values for the option.  This argument can take
         the following forms:
        
         single value -- for StringOption this this is a string, for
            IntegerOption this is an integer, for FloatOption this is
            a float.  The single value mode is most useful when the 
            value is a regular expression.  For example, to specify
            that a StringOption must be a string of characters followed
            by a digit, 'values' would be set to re.compile(r'\w+\d').

         range of values -- a two element list can be given to specify
            the endpoints of a range of valid values.  This is probably
            most useful on IntegerOption and FloatOption.  For example,
            to specify that an IntegerOption can only take the values
            from 0 to 10, 'values' would be set to [0,10]. 

            NOTE: This mode must *always* use a Python list since using
                  a tuple means something else entirely.

         tuple of values -- a tuple of values can be used to specify 
            a complete list of valid values.  For example, to specify
            that an IntegerOption can take the values 1, 2, or 3, 'values'
            would be set to (1,2,3).  If a string value can only take 
            the values, 'hi', 'bye', and any string of characters beginning
            with the letter 'z', 'values' would be set to 
            ('hi','bye',re.compile(r'z.*?')).

            NOTE: This mode must *always* use a Python tuple since using
                  a list means something else entirely.

      category -- a category key which specifies which category the
         option belongs to (see Option.add_category())
      
      callback -- a function to call after the value of the option has
         been validated.  This function will be called with the validated
         option value as its only argument.

      environ -- environment variable to use as default value instead
         of specified value.  If the environment variable exists, it
         will be used for the default value instead of the specified value.

      registry -- registry key to use as default value instead of
         specified value.  If the registry key exists, it will be used
         for the default value instead of the specified value.  A
         specified environment variable takes precedence over this value.

      name -- key used to get the option from its corresponding section.
         You do not need to specify this.  It will be set automatically
         when you put the option into the ConfigManager instance.

      mandatory -- flag used to determine if the option itself is
         required to be present.  The idea of a "mandatory option" is
         a little strange, but I have seen it done.

      source -- flag used to determine whether the option was set
         directly in the ConfigManager instance through Python,
         by a configuration file/command line option, etc.  You do not need
         to specify this, it will be set automatically during parsing.
         This flag should have the value of BUILTIN, COMMANDLINE,
         CONFIGFILE, ENVIRONMENT, REGISTRY, or CODE.


      Examples::
         BooleanOption(
            ''' Display help message ''',
            options = '--help -h',
            callback = usage,  # usage() function must exist prior to this
         )

         BooleanOption(
            ''' Set verbosity ''',
            options = '-v --verbose !-q !--quiet',
         )

         StringOption(
            '''
            IP address option

            This option accepts an IP address to connect to.

            Valid Values:
            '#.#.#.#' where # is a number from 1 to 255

            ''',
            options = '--ip-address',
            values = re.compile(r'\d{1,3}(\.\d{1,3}){3}'),
            default = '127.0.0.0',
            synopsis = '#.#.#.#',
            category = 'network',  # Assumes 'network' category exists
         )

         IntegerOption(
            '''
            Number of seconds to wait before timing out

            Valid Values:
            positive integer

            ''',
            options = '--timeout -t',
            default = 300,
            values = [0,1e9],
            category = 'network',
         )

         IntegerOption(
            '''
            Number of tries to connect to the host before giving up

            Valid Values:
            accepts 1, 2, or 3 retries

            ''',
            options = '--tries',
            default = 1,
            values = (1,2,3),
            category = 'network',
         )

         StringOption(
            '''
            Nonsense option for example purposes only

            Valid Values:
            accepts 'hi', 'bye', or any string beginning with the letter 'z'

            ''',
            options = '--nonsense -n',
            default = 'hi',
            values = ('hi', 'bye', re.compile(r'z.*?')),
         )

      """
      if type(self.__class__) is GenericOption:
         raise ValueError, 'GenericOption cannot be instantiated ' + \
                           'directly, you must use a subclass.'
      self.parent = None
      self.initialize(locals())
      self.data = None

   def initialize(self, vars):
      """ Initialize all instance variables """
      docstring = vars.get('docstring', DEFAULTS['docstring'])
      options = vars.get('options', DEFAULTS['options'])
      default = vars.get('default', DEFAULTS['default'])
      optional = vars.get('optional', DEFAULTS['optional'])
      values = vars.get('values', DEFAULTS['values'])
      category = vars.get('category', DEFAULTS['category'])
      name = vars.get('name', DEFAULTS['name'])
      source = vars.get('source', DEFAULTS['source'])
      callback = vars.get('callback', DEFAULTS['callback'])
      synopsis = vars.get('synopsis', DEFAULTS['synopsis'])
      environ = vars.get('environ', DEFAULTS['environ'])
      mandatory = vars.get('mandatory')
      if mandatory is None:
         mandatory = isinstance(self, GenericArgument)
      registry = vars.get('registry', DEFAULTS['registry'])
      
      self.actual = None  # Actual option used on the command-line
      self.name = name
      self.options = options
      if category is None:
         self.category = []
      elif type(category) in [type(list), type(tuple)]:
         self.category = list(category)
      else:
         self.category = [category]
      self.values = values
      if synopsis is not None:
         self.synopsis = synopsis
      self.environ = environ
      self.registry = registry
      self.optional = self.cast(optional)
      self.callback = callback
      self.mandatory = mandatory
      self.source = source   # Flag to indicate where the option came from
      self.occurrences = 0 # Number of times the command-line option was used

      self.summary, self.description, self.error = \
                    self._splitDocString(docstring)

      self.file = None # Variable to hold filename of config file where
                       # the option came from.  This should only be
                       # set if self.source == CONFIGFILE.

      if source <= ENVIRONMENT:
         if self.environ and os.environ.has_key(str(self.environ)):
            self.default = self.cast(os.environ[str(self.environ)])
            self.source = ENVIRONMENT
         else:
            self.default = self.cast(default)
      else:
         self.default = None

      self.setValue(self.default)

   def defaultValue(self):
      return self.default

   def getValue(self, value=None):
      """ Return value for option """
      # If specified on the commond-line, always return it.
      if self.data is not None and self.source & COMMANDLINE:
         return self.data

      # See if it was set in the environment
      if self.environ and os.environ.has_key(str(self.environ)):
         self.source = ENVIRONMENT
         self.file = None
         return self.cast(os.environ[str(self.environ)])

      # If the option was populated in any other way, return it.
      if self.data is not None:
         return self.data

      # Look for a default
      if self.default is not None:
         self.source = BUILTIN
         self.file = None
         return self.default

      if value is not None:
         self.source = CODE
         self.file = None

      return value

   def matches(self, opt):
      """ Return boolean indicating a match to the given option """
      possibilities = [x.replace('!','') for x in self.getPossibleOptions()]
      for i in possibilities:
         if i.startswith(opt):
            return i
      return 0

   def copy(self):
      """ Make a deep copy of self """
      newcopy = self.__class__()
      for key, value in vars(self).copy().items():
         if key == 'data':
            setattr(newcopy, key, copy.copy(value))
         else:
            setattr(newcopy, key, value)
      return newcopy

   def _splitDocString(self, doc):
      """
      Split documentation string into summary, description, and error

      Required Arguments:
      doc -- a string resembling a Python documentation string

      Returns:
      tuple -- a three element tuple containing the summary, description,
         and error message parsed from the documentation string.

      """
      summary = None
      description = None
      error = None

      if doc.strip():
         parts = doc.strip().split('\n')
         if len(parts) > 2:
            # If there is a blank line after the first line,
            # there is a summary.
            if not(parts[1].strip()):
               summary = parts[0].strip()
               description = '\n'.join(parts[2:])
            else:
               summary = None
               description = doc

         elif len(parts) == 2:
            summary = None
            description = doc

         else:
            summary = doc
            description = None

      if summary: summary = summary.strip()

      if description:
         # Look for error message
         m = re.compile(r'^\s*Valid\s+Values\s*:+\s*(.+)(?:\n\s*\n|\s*$)',
                        re.I|re.S|re.MULTILINE).search(description)
         if m: error = m.group(1).strip()

         # Remove extra space from the front of each line
         spaces = re.compile(r'^\n*(\s*)', re.MULTILINE).findall(description)
         spaces = len(min(spaces))
         lines = description.split('\n')
         for i in range(len(lines)):
            if lines[i].strip():
               lines[i] = lines[i][spaces:]
            else:
               lines[i] = ''
         description = '\n'.join(lines).strip()

      if description and summary:
         description = '%s\n\n%s' % (summary, description)
      elif summary:
         description = summary

      return summary, description, error

   def setParent(self, parent):
       """ Set the parent section """
       self.parent = parent

   def names(self):
      """
      Build a dictionary of common variables needed in message strings

      Returns:
      dictionary -- with common variables populated (see return value)

      """
      return {}
      return {'name': self.name, 'default': self.default, 
              'option': self.actual, 'synopsis': self.synopsis}

   def __lt__(self, other): return self.compare(other) < 0
   def __gt__(self, other): return self.compare(other) > 0
   def __le__(self, other): return self.compare(other) <= 0
   def __ge__(self, other): return self.compare(other) >= 0
   def __eq__(self, other): return self.compare(other) == 0
   def __cmp__(self, other): return self.compare(other)

   def compare(self, other):
      """ Compare option to another using the specified sort order """
      for attr in self.sort_order:
          sattr = getattr(self, attr)
          oattr = getattr(other, attr)

          if sattr == None: sattr = ''
          if oattr == None: oattr = ''

          if type(sattr) is str and type(oattr) is str:
              sattr = re.sub(r'\W', '', sattr)
              oattr = re.sub(r'\W', '', oattr)

          if sattr < oattr:
              return -1
          elif sattr > oattr:
              return 1
      return 0

   def clearValue(self):
      """ Reset the option value to None """
      self.data = None

   def setValue(self, value):
      """
      Set the value of the option to the given value

      Once the value is set to the new value and validated, the
      specified callback function is called with that value as its
      only argument.

      """
      if value is None:
         self.clearValue()
      else:
         if callable(self.callback):
            value = self.callback(self.cast(value))
         self.data = self.validate(value)

   def __str__(self):
      """ Return string representation of the current option value """
      value = self.getValue()
      if value is not None:
         return str(value)
      return ''

   def __repr__(self):
      """
      Build a string comparable to what may have been given on the command line

      """
      value = self.getValue()
      if value is not None:
         option = self.actual
         if not option:
            args = self.getPossibleOptions()
            if args: option = args[0]
         if option:
            return str('%s %s' % (option, value)).strip()
      return ''

   def acceptsArgument(self):
      """ Return a boolean indicating if the option accepts an argument """
      return 1

   def requiresArgument(self):
      """ Return a boolean indicating if the option requires an argument """
      if self.optional is None:
         return 1
      else:
         return 0

   def getPossibleOptions(self):
      """ Return a list of all possible command line options """
      if self.options:
         return [x.strip() for x in re.sub(r'!\s+', r'!', self.options).split()
                           if x.replace('!','').strip()]
      return []

   def validate(self, value):
      """ Validate the value of the option """
      return self.checkValues(self.cast(value))

   def cast(self, value):
      return value

   def checkValues(self, value):
      """ Check the value against the possible valid values """
      # All values are valid
      if self.values is None: return value

      name = self.name
      if self.actual: name = self.actual

      # Check to see if the value is within the valid range
      if isinstance(self.values, list):
         if not self.values:
            pass
         elif value >= self.values[0] and value <= self.values[-1]:
            return value

         if self.error:
            raise InvalidOptionError(name, value, 
                                     msg=self.error % self.names())
         else:
            raise InvalidOptionError(name, value,
                  msg='Given value is not within the valid range (%s, %s)' %
                      (self.values[0], self.values[-1]))

      # Check to see if the value is within the list of valid values
      elif isinstance(self.values, tuple):
         # Look for literal values
         for option in [x for x in self.values
                                if not(isinstance(x, RegexType))]:
            if isinstance(option, str) and option.lower() == value.lower():
               return value
            elif option == value:
               return value

         # Look for regular expressions in the list
         for regex in [x for x in self.values if isinstance(x, RegexType)]:
            if regex.search(value): 
               return value
            
         if self.error:
            raise InvalidOptionError(name, value, 
                                     msg=self.error % self.names())
         else:
            raise InvalidOptionError(name, value,
                  msg='Given value is not a valid value. Expecting (%s)' % \
                      (', '.join(map(str, self.values))))

      # Check to see if the value is equal to the only valid value
      elif isinstance(self.values, str) or isinstance(self.values, int) \
           or isinstance(self.values, float):
         if value == self.values:
            return value

         if self.error:
            raise InvalidOptionError(name, value, 
                                     msg=self.error % self.names())
         else:
            raise InvalidOptionError(name, value,
                  msg='Given value is not a valid value. Expecting (%s)' % \
                       self.values)

      # Check to see if the value is valid using a regex
      elif isinstance(self.values, RegexType):
         if not isinstance(value, str):
            pass
         elif self.values.search(value):
            return value

         if self.error:
            raise InvalidOptionError(name, value, 
                                     msg=self.error % self.names())
         else:
            raise InvalidOptionError(name, value,
                                     msg='Given value is not a valid value')

      # Use the user defined validation function
      elif callable(self.values):
         if self.values(value):
            return value

         if self.error:
            raise InvalidOptionError(name, value, 
                                     msg=self.error % self.names())
         else:
            raise InvalidOptionError(name, value,
                                     msg='Given value is not a valid value')

      # Bail out if we don't know what this is
      raise ValueError, 'Unknown valid values type'


class GenericArgument(GenericOption):
   """
   Base class for command-line arguments

   All command line arguments must subclass from this one.  In addition,
   this is an abstract class.  It cannot be instantiated directly.

   """
#  def __init__(self, docstring=DEFAULTS['docstring'],
#                     default=DEFAULTS['default'],
#                     optional=DEFAULTS['optional'],
#                     values=DEFAULTS['values'],
#                     callback=DEFAULTS['callback'],
#                     synopsis=DEFAULTS['synopsis'],
#                     environ=DEFAULTS['environ'],
#                     registry=DEFAULTS['registry'],
#                     name=DEFAULTS['name'],
#                     source=DEFAULTS['source']):
#     if type(self.__class__) is GenericArgument:
#        raise ValueError, 'GenericArgument cannot be instantiated ' + \
#                          'directly, you must use a subclass.'
#     self.parent = None
#     self.initialize(locals())
#     self.data = None

   def __repr__(self):
      """
      Build a string comparable to what may have been given on the command line

      """
      return str(self)
