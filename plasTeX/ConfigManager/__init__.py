#!/usr/bin/env python

"""
ConfigManager

ConfigManager is a combination command-line option parser and configuration
file.  It essentially combines ConfigParser, getopt, and a lot of
additional logic to parse the command-line the way you expect it to be
parsed.  The ConfigManager class should be backwards compatible with the
ConfigParser class, but contains much more functionality and a more natural
dictionary-style interface to sections and options.

See examples at the bottom of this file.  Try typing __init__.py
followed by a bunch of imaginary command line options and arguments.

"""

import sys, string, re, urllib, copy, types, os
from plasTeX.dictutils import ordereddict
from UserList import UserList
from UserDict import UserDict
from textwrap import wrap

__all__ = ['ConfigManager','BooleanOption','IntegerOption','CompoundOption',
           'MultiOption','GenericOption','FloatOption','StringOption',
           'InputFileOption','OutputFileOption','InputDirectoryOption',
           'OutputDirectoryOption','CountedOption',
           'BooleanArgument','IntegerArgument','CompoundArgument',
           'MultiArgument','GenericArgument','FloatArgument','StringArgument',
           'InputFileArgument','OutputFileArgument','InputDirectoryArgument',
           'OutputDirectoryArgument','CountedArgument',
           'BUILTIN','CODE','REGISTRY','CONFIG','CONFIGFILE','ENVIRON',
           'ENVIRONMENT','COMMANDLINE','ALL','DEFAULTSECT',
           'ON','OFF','TRUE','FALSE','YES','NO','CommandLineManager',
           'GetoptError','ConfigError','NoOptionError']

DEFAULTSECT = "DEFAULT"
MAX_INTERPOLATION_DEPTH = 10
ON = TRUE = YES = 1
OFF = FALSE = NO = 0

TERMINAL_WIDTH = 76   # Maximum width of terminal 
MAX_NAME_WIDTH_RATIO = 0.25  # Max fraction of terminal to use for option
PREPAD = 2   # Padding before each option name in usage
GUTTER = 4   # Space between option name and description in usage

# Possible values for `source'.
BUILTIN = 2
CODE = 4
REGISTRY = 8 
CONFIG = CONFIGFILE = 16
ENVIRON = ENVIRONMENT = 32
COMMANDLINE = 64
ALL = 0xffffff

# Exception classes
class Error(Exception):
    """ Generic exception """
    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg
    __repr__ = __str__


# Exceptions while parsing command line
class GetoptError(Error):
    """ Generic command line exception """
    def __init__(self, msg, opt):
        self.msg = msg
        self.opt = opt
        Exception.__init__(self, msg, opt)

    def __str__(self):
        return self.msg
    __repr__ = __str__

class RequiresArgument(GetoptError):
    """ Exception for a missing argument """

class MandatoryOption(GetoptError):
    """ Exception for a missing option """

class UnspecifiedArgument(GetoptError):
    """ Exception for an argument when none was expected """

class UnrecognizedArgument(GetoptError):
    """ Exception for an argument that is unrecognized """

class NonUniquePrefix(GetoptError):
    """ Exception for multiple option prefixes that match a given option """

class UnknownCompoundGroup(GetoptError):
    """ Exception for an unknown grouping character used for a compound """  
    def __init__(self, msg=''):
        GetoptError.__init__(self, msg, '')


# Exceptions while reading/parsing configuration files
class ConfigError(Error):
   """ Generic configuration file exception """

class NoSectionError(ConfigError):
    """ Exception for missing sections """
    def __init__(self, section):
        ConfigError.__init__(self, 'No section: %s' % section)
        self.section = section

class DuplicateSectionError(ConfigError):
    """ Exception for duplicate sections """
    def __init__(self, section):
        ConfigError.__init__(self, "Section %s already exists" % section)
        self.section = section

class InvalidOptionError(GetoptError, ConfigError):
    """ Exception for invalid values for a given option """
    def __init__(self, option, value, msg='', type=''):
        if type: type += ' '
        if not msg:
            msg="Invalid value for %soption `%s'" % (type, option)
        ConfigError.__init__(self, msg+': %s' % value)
        self.option = option
        self.value = value

class NoOptionError(ConfigError):
    """ Exception for missing a missing option in a section """
    def __init__(self, option, section):
        ConfigError.__init__(self, "No option `%s' in section: %s" %
                       (option, section))
        self.option = option
        self.section = section

class InterpolationError(ConfigError):
    """ Exception for message interpolation errors """
    def __init__(self, reference, option, section, rawval):
        ConfigError.__init__(self,
                       "Bad value substitution:\n"
                       "\tsection: [%s]\n"
                       "\toption : %s\n"
                       "\tkey    : %s\n"
                       "\trawval : %s\n"
                       % (section, option, reference, rawval))
        self.reference = reference
        self.option = option
        self.section = section

class InterpolationDepthError(ConfigError):
    """ Exception for excessive recursion in interpolation """
    def __init__(self, option, section, rawval):
        ConfigError.__init__(self,
                       "Value interpolation too deeply recursive:\n"
                       "\tsection: [%s]\n"
                       "\toption : %s\n"
                       "\trawval : %s\n"
                       % (section, option, rawval))
        self.option = option
        self.section = section

class ParsingError(ConfigError):
    """ Exception for errors occurring during parsing of a config file """
    def __init__(self, filename):
        ConfigError.__init__(self, 'File contains parsing errors: %s' % filename)
        self.filename = filename
        self.errors = []

    def append(self, lineno, line):
        self.errors.append((lineno, line))
        self.msg = self.msg + '\n\t[line %2d]: %s' % (lineno, line)

class TooFewValues(GetoptError):
   """ Got fewer values than expected """
   def __init__(self, msg):
      GetoptError.__init__(self, msg, '')

class TooManyValues(GetoptError):
   """ Got more values than expected """
   def __init__(self, msg):
      GetoptError.__init__(self, msg, '')

class MissingSectionHeaderError(ParsingError):
    """ Exception for options that occur before a section heading """
    def __init__(self, filename, lineno, line):
        ConfigError.__init__(
            self,
            'File contains no section headers.\nfile: %s, line: %d\n%s' %
            (filename, lineno, line))
        self.filename = filename
        self.lineno = lineno
        self.line = line


class ConfigSection(UserDict, object):
    """ Section of a configuration object """

    def __init__(self, name, data={}):
        """
        Initialize the section

        Required Arguments:
        name -- name of the section
        data -- dictionary containing the initial set of options

        """
        UserDict.__init__(self, data)
        self.name = name
        self.parent = None

    def copy(self):
        """ Make a deep copy of self """
        newcopy = self.__class__(self.name)
        for key, value in vars(self).items():
            if key == 'data': continue
            setattr(newcopy, key, value)
        for key, value in self.data.items():
            newcopy.data[key] = value.copy()
        return newcopy        

    def setParent(self, parent):
        """ Set the parent ConfigManager instance """
        self.parent = parent

    def defaults(self):
        """ Return the dictionary of defaults """
        return self.parent.defaults()

    def __getitem__(self, key):
        """ Return the value of the option, not the option itself """
        return self.get(key)

    def set(self, option, value, source=BUILTIN):
        """
        Create the appropriate option type

        If the value is already an Option instance, just plug it in.
        If the value is anything else, try to figure out which option
        type it corresponds to and create an option of that type.

        Required Arguments:
        option -- dictionary key where the option should be set
        value -- option value to store
        source -- flag to indicate source of option

        Returns: None

        """
        typemap = {str:StringOption, int:IntegerOption,
                   float:FloatOption, list:MultiOption, tuple:MultiOption}

        if self.data.has_key(option):
           if self.data[option].source <= source:
              self.data[option].source = source
              self.data[option].setValue(value)

        else:
           if isinstance(value, GenericOption):
              value.setParent(self)
              value.name = str(option)
              self.data[option] = value

           elif type(value) in typemap.keys():
              for key, opttype in typemap.items():
                 if isinstance(value, key):
                    # Handle booleans this way until support for
                    # true booleans shows up in Python.
                    if type(value) == str and \
                       str(value).lower().strip() in ['on','off','true','false','yes','no']:
                       opttype = BooleanOption
                    self.data[option] = opttype(name=option, source=source)
                    self.data[option].setParent(self)
                    self.data[option].name = str(option)
                    self.data[option].setValue(value)
                    break
           else:
              raise TypeError, \
                    'Could not find valid option type for "%s"' % value

    def __setitem__(self, key, value):
        """ Set the item in the dictionary """
        self.set(key, value, source=BUILTIN)
    
    def getint(self, option):
        """ Get the option value and cast it to an integer """
        return int(self[option])

    def getfloat(self, option):
        """ Get the option value and cast it to a float """
        return float(self[option])

    def getboolean(self, option):
        """ Get the option value and cast it to a boolean """
        v = self[option]
        val = int(v)
        if val not in (0, 1):
            raise ValueError, 'Not a boolean: %s' % v
        return val

    def get(self, option, raw=0, vars={}):
        """
        Get an option value for a given section.

        All % interpolations are expanded in the return values, based on the
        defaults passed into the constructor, unless the optional argument
        `raw' is true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        Required Arguments:
        option -- name of the option to retrieve

        Keyword Arguments:
        raw -- boolean flag that indicates whether string values should
           be returned as a raw value or as a string with all variable
           interpolation applied
        vars -- dictionary of values to use in string interpolation

        Returns:
        value of the option

        """
        value = self.getraw(option, vars)

        # Raw was specified
        if raw or value == None: return value

        # If we have a list, see if any strings need interpolation.
        if type(value) in [list, tuple]:
            strings = [s for s in value
                         if isinstance(s,str) and s.find('%(')+1]
            if not strings: return value

        # If we have a string, but no interpolation is needed, bail out.
        elif not(isinstance(value,str)) or value.find("%(") < 0:
            return value

        # otherwise needs interpolation...
        var_dict = self.defaults().data.copy()
        var_dict.update(self.data)
        var_dict.update(vars)

        # Handle lists of interpolations as well as single values.
        if type(value) in [list, tuple]:
            new_values = []
            for i in value:
                new_values.append(self.interpolate(option, var_dict, i))
            return new_values
        else:
            return self.interpolate(option, var_dict, value)

    def interpolate(self, option, vars, rawval):
        """
        Do the string interpolation

        Required Arguments:
        option -- name of the option
        vars -- dictionary of values to use in interpolation
        rawval -- raw value of the option

        Returns:
        string -- string with all variables interpolated

        """
        value = rawval
        depth = 0
        # Loop through this until it's done
        while depth < MAX_INTERPOLATION_DEPTH:
            depth = depth + 1
            if value.find("%(") >= 0:
                try:
                    value = value % vars
                except KeyError, key:
                    raise InterpolationError(key, option, self.name, rawval)
            else:
                break
        if value.find("%(") >= 0:
            raise InterpolationDepthError(option, self.name, rawval)
        return value

    def getraw(self, option, vars={}):
        """
        Return raw value of option

        Required Arguments:
        option -- name of the option to retrieve

        Keyword Arguments:
        vars -- dictionary containing additional default values

        """
        if vars.has_key(option):
            return vars[option].getValue()

        if self.has_key(option):
            return self.data[option].getValue()

        defaults = self.defaults()
        if defaults.has_key(option):
            return defaults.data[option].getValue()

        raise NoOptionError(option, self.name)

    def to_string(self, source=COMMANDLINE):
        """
        Convert the section back into INI format

        Keyword Arguments:
        source -- flag which indicates which source of information to print

        Returns:
        string -- string containing the section in INI format

        """
        s = ''
        keys = self.keys()
        keys.sort()
        for key in keys:
            if source & self.data[key].source:
               raw = self.getraw(key)
               option = self.data[key]

               # Bypass unset options
               if isinstance(option, MultiOption) and raw == []: continue
               if raw == None: continue

               # Print description or summary of the option as well
               comment = ''
               if option.summary: comment = option.summary
               if option.description: comment = option.description
               if comment:
                  comment = comment.strip() % option.names()
                  comment = comment.split('\n')
                  s += '\n; %s\n' % '\n; '.join(comment)

               value = str(option).replace('\n', '\n    ')
               if value.find('\n') + 1: value = '\n    ' + value
               s += "%s %s %s\n" % (key, ConfigManager.OPTIONSEP, value)
        return s

    def __str__(self):
        """ Return section in INI format without builtins """
        return self.to_string()

    def __repr__(self):
        """ Return section in INI format with builtins """
        return self.to_string(ALL)


class ConfigManager(UserDict, object):

    # Regular expressions for parsing section headers and options.
    SECTCRE = re.compile(
        r'\['                                 # [
        r'(?P<header>[^]]+)'                  # very permissive!
        r'\]'                                 # ]
        )

    OPTCRE = re.compile(
        r'(?P<option>[]\-[\w_.*,(){}]+)'      # a lot of stuff found by IvL
        r'[ \t]*(?P<vi>[:=])[ \t]*'           # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )

    # Option separator used in printing out INI format
    OPTIONSEP = '='

    # Set prefixes for options.  If these are the same, all options
    # are treated as long options.  You can set either one to None
    # to turn that type of option off as well.
    short_prefix = '-'
    long_prefix = '--'

    def __init__(self, defaults={}):
        """
        Initialize ConfigManager

        Keyword Arguments:
        defaults -- dictionary of default values.  These values will
           make up the section by the name DEFAULTSECT.

        """
        UserDict.__init__(self)
        self[DEFAULTSECT] = ConfigSection(DEFAULTSECT, defaults)
        self.strict = 1     # Raise exception for unknown options
        self._categories = {}  # Dictionary of option categories
        self.unrecognized = []

    def copy(self):
        """ Make a deep copy of self """
        newcopy = self.__class__()
        for key, value in vars(self).items():
            if key == 'data': continue
            setattr(newcopy, key, value)
        for key, value in self.data.items():
            newcopy.data[key] = value.copy()
        return newcopy

    def set_prefixes(cls, arg1, arg2=None):
        """
        Set the command-line option prefixes

        Arguments:
        short - prefix to use for short command-line options.  If this
           is set to 'None', then all options are treated as long options.
        long - prefix to use for long options

        """
        if arg1 == arg2 == None:
           raise ValueError, 'Short and long prefixes cannot both be None.'
        if arg2 is None:
           cls.long_prefix = arg1
           cls.short_prefix = None
        else:
           cls.long_prefix = arg2
           cls.short_prefix = arg1

    set_prefixes = classmethod(set_prefixes)

    def add_help_on_option(self, category=None):
        """
        Add a --help-on=LIST option for displaying specific option help

        The --help-on= option can be added to give the command line
        interactive help.  For example, if you had an option called
        '--debug', you could type '--help-on debug' to get the full
        description of the --debug option printed out.

        Keyword Arguments:
        category -- category to put the --help-on option in

        """
        self[DEFAULTSECT]['__help_on__'] = MultiOption(
           """ Display help on listed option names """,
           options = '%shelp-on' % self.long_prefix[0],
           category = category,
           callback = self.usage_on,
        )

    def remove_help_on_option(self):
        """ Remove the --help-on option """
        try: del self[DEFAULTSECT]['__help_on__']
        except: pass

    def add_category(self, key, title):
        """
        Add a category to the ConfigManager

        Options can be grouped by categories for display in the usage
        message.  Categories have both a key and a title.  The key is
        what is used in the 'category' parameter when instantiating an
        option.  The title is the heading to print in the usage message.

        Required Arguments:
        key -- name of the category used in instantiating an option
        title -- title of the category to print in the usage message

        Returns:
        string -- the same key given as the first argument

        """
#       if not self._categories:
#          self._categories['__categories__'] = 'Help Categories'
#       if not self.has_key('__categories__'):
#          self.add_section('__categories__')
#       self['__categories__'][key] = BooleanOption(title,
#            options='%shelp-%s' % (self.long_prefix, key),
#            category='__categories__')
        self._categories[key] = title
        return key

    def get_category(self, key):
        """ Return the title of the given category """
        if type(key) not in [list, tuple]:
           key = [key]
        if not key:
           return ''
        return self._categories[key[0]]

    def categories(self):
        """ Return the dictionary of categories """
        return self._categories

    def set_strict(self, bool=1):
        """
        Parse the command line strictly

        If you do not want to be bothered with errors due to unrecognized
        arguments, this method can be called with a boolean 'false'.
        This is very useful if your program is actually a wrapper around
        another program and you do not want to declare all of its options
        in your ConfigManager.  The ConfigManager will simply make its best
        guess as to whether the option accepts a value and what type the
        option is.

        Keyword Arguments:
        bool -- flag indicating whether parsing should be strict or not

        """
        self.strict = not(not(bool))

    def defaults(self):
        """ Return a dictionary of defaults """
        return self[DEFAULTSECT]

    def sections(self):
        """ Return a list of section names """
        return self.keys()

    def add_section(self, section):
        """
        Create a new section in the configuration.

        Do nothing if a section by the specified name already exists.

        Required Arguments:
        section -- name of the section to create

        Returns:
        instance -- a ConfigSection instance with the given name is returned

        """
        if self.has_key(section): return self[section]
        self[section] = ConfigSection(section)
        return self[section]

    def has_section(self, section):
        """ Indicate whether the named section is present """
        return section in self.keys()

    def options(self, section):
        """ Return a list of option names for the given section name """
        if self.has_key(section):
            return self[section].keys()
        else: 
            raise NoSectionError(section)

    def read(self, filenames):
        """
        Read and parse a filename or a list of filenames

        Files that cannot be opened are silently ignored; this is
        designed so that you can specify a list of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), and all existing
        configuration files in the list will be read.  A single
        filename may also be given.

        """
        if type(filenames) in [type(''), type(u'')]:
            filenames = [filenames]
        for filename in filenames:
            try:
                if filename.startswith('~'):
                    filename = os.path.expanduser(filename)
                fp = urllib.urlopen(filename)
            except (OSError, IOError):
                continue
            self.__read(fp, filename)
            fp.close()
        return self

    def readfp(self, fp, filename=None):
        """
        Like read() but the argument must be a file-like object.

        The 'fp' argument must have a 'readline' method.  Optional
        second argument is the 'filename', which if not given, is
        taken from fp.name.  If fp has no 'name' attribute, '<???>' is
        used.

        Required Arguments:
        fp -- file-type like object
        filename -- name of the file in 'fp'

        Returns:
        string -- contents of the file pointer

        """
        if filename is None:
            try:
                filename = fp.name
            except AttributeError:
                filename = '<???>'
        self.__read(fp, filename)
        return self

    def get(self, section, option, raw=0, vars={}):
        """ Get an option value for a given section """
        return self[section].get(option, raw, vars)

    def set(self, section, option, value, source=BUILTIN):
        """ Set an option value """
        if not section or section == DEFAULTSECT:
            sectdict = self[DEFAULTSECT]
        else:
            try:
                sectdict = self[section]
            except KeyError:
                raise NoSectionError(section)
        sectdict.set(option, value, source)

    def __setitem__(self, key, value):
        """ Add a section to the configuration """
        if isinstance(value, ConfigSection):
           self.data[key] = value
           self.data[key].setParent(self)
        else:
           self.data[key] = ConfigSection(str(key))
           self.data[key].setParent(self)

    def __getitem__(self, key):
        """
        Return section with given name

        Return the section or if it's not a section try to
        return an option by that name in the 'default' section.

        """
        if self.data.has_key(key):
           return self.data[key]
        if self.data[DEFAULTSECT].has_key(key):
           return self.data[DEFAULTSECT][key]
        raise NoSectionError(key)

    def getint(self, section, option):
        """ Get an option value and cast it to an integer """
        return self[section].getint(option)

    def getfloat(self, section, option):
        """ Get an option value and cast it to a float """
        return self[section].getfloat(option)

    def getboolean(self, section, option):
        """ Get an option value and cast it to a boolean """
        return self[section].get(option)

    def getraw(self, section, option):
        """ Get the raw (un-interpolated) value of an option """
        return self[section].getraw(option)

    def has_option(self, section, option):
        """ Check for the existence of a given option in a given section """
        if not section:
            section=DEFAULTSECT
        elif not self.has_key(section):
            return 0
        else:
            return self[section].has_key(option)

    def write(self, fp):
        """ Write an INI-format representation of the configuration state """
        fp.write(str(self))

    def __str__(self):
        """ Return an INI formated string with builtins removed """
        return self.to_string()

    def __repr__(self):
        """ Return an INI formated string with builtins included """
        return self.to_string(source=COMMANDLINE|CONFIGFILE|CODE|BUILTIN|REGISTRY|ENVIRONMENT)

    def to_string(self, source=COMMANDLINE|CONFIGFILE):
        """
        Build an INI formatted string based on the ConfigManager contents

        Keyword Arguments:
        source -- flag indicating which sources if information to print

        Returns:
        string -- INI formatted string

        """
        if source & BUILTIN: func = repr
        else: func = str
        s = ''
        keys = [x for x in self.keys() if x != DEFAULTSECT]
        keys.sort()
        if self[DEFAULTSECT]:
            keys.insert(0, DEFAULTSECT)
        for section in keys:
            content = func(self[section]).strip()
            if content:
               s += "[%s]\n%s\n\n" % (section, content)
        return s

    def remove_option(self, section, option):
        """ Remove an option from a section """
        if not section or section == DEFAULTSECT:
            sectdict = self[DEFAULTSECT]
        else:
            try:
                sectdict = self[section]
            except KeyError:
                raise NoSectionError(section)
        try:
            del sectdict[option]
            return 1
        except KeyError:
            return 0

    def remove_section(self, section):
        """ Remove the given section """
        if self.has_key(section):
            del self[section]
            return 1
        else:
            return 0

    def __read(self, fp, fpname):
        """
        Parse an INI formatted file

        The sections in the file contain a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name: value' format lines.
        Continuation are represented by an embedded newline then
        leading whitespace.  Blank lines, lines beginning with a '#',
        and just about everything else is ignored.

        """
        cursect = None                            # None, or a dictionary
        optname = None
        lineno = 0
        e = None                                  # None, or an exception
        while 1:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split()[0].lower() == 'rem' \
               and line[0] in "rR":      # no leading whitespace
                continue
            # continuation line?
            if line[0] in ' \t' and cursect is not None and optname:
                value = line.strip()
                if value and cursect.data[optname].source == CONFIGFILE:
                    cursect.data[optname] += "%s" % value
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if self.has_key(sectname):
                        cursect = self[sectname]
                    else:
                        cursect = ConfigSection(sectname)
                        self[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, `line`)
                # an option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if vi in ('=', ':') and ';' in optval:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = optval.find(';')
                            if pos and optval[pos-1] in string.whitespace:
                                optval = optval[:pos]
                        optval = optval.strip()
                        # allow empty values
                        if optval == '""':
                            optval = ''
                        try:
                            cursect.set(optname, optval, source=CONFIGFILE)
                            cursect.data[optname].file = fpname
                        except:
                            print "Problem occurred in section '%s' while reading file %s." % (cursect.name, fpname)
                            raise
                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, `line`)
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

    def get_default_option(self, option):
        """ Get the given option from the default section """
        try:
            return self[DEFAULTSECT][option]
        except KeyError:
            raise NoOptionError(option, DEFAULTSECT)

    def get_opt(self, section, option):
        """ Return the option with leading and trailing quotes removed """
        optionstring = self[section][option].strip()
        if (optionstring[0] == '\'' and optionstring[-1] == '\'') or \
           (optionstring[0] == '\"' and optionstring[-1] == '\"'):
            optionstring = optionstring[1:-1]
        return optionstring

    def get_optlist(self, section, option, delim=','):
        """
        Return the option split into a list

        Required Arguments:
        section -- name of the section
        option -- name of the option

        Keyword Arguments:
        delim -- delimiter to use when splitting the option

        Returns:
        list -- option value split on 'delim' with whitespace trimmed

        """
        optionstring = self.get_opt( section, option )	   
        return [x.strip() for x in optionstring.split(delim)]

    def __add__(self, other):
        """
        Merge items from another ConfigManager

        Sections in 'other' will overwrite sections in 'self'.

        """
        other = other.copy()
        for key, value in other.items():
            self[key] = value
        try:
           for key, value in other._categories.items():
               self._categories[key] = value
        except AttributeError: pass
        return self

    def __iadd__(self, other):
        """ Merge items from another ConfigManager """
        return self.__add__(other)

    def __radd__(self, other):
        """
        Merge items from another ConfigManager

        Sections already in 'self' will not be overwritten.

        """
        other = other.copy()
        for key, value in other.items():
            if not self.has_key(key):
                self[key] = value   
        try:
           for key, values in other._categories.items():
               if not self._categories.has_key(key):
                   self._categories[key] = value   
        except AttributeError: pass
        return self

    def get_options_from_config(self):
        """
        Locate all short and long options

        Returns:
        tuple -- two element tuple contain a list of short option
           instances and a list of long option instances

        """
        short_prefixes, long_prefixes = type(self).get_prefixes()

        longopts = []
        shortopts = []
        for section in self.values():
           for option in section.data.values():
              for opt in option.getPossibleOptions():
                 opt = opt.replace('!','')

                 # See if the option is a long option
                 for prefix in long_prefixes:
                    if prefix is None:
                       pass
                    elif not prefix.strip():
                       pass
                    elif opt.startswith(prefix):
                       if option not in longopts:
                          longopts.append(option)
                       continue

                 # See if the option is a short option
                 for prefix in short_prefixes:
                    if prefix is None:
                       pass
                    elif not prefix.strip():
                       pass
                    elif opt.startswith(prefix):
                       if option not in shortopts:
                          shortopts.append(option)

        return shortopts, longopts

    def getopt(self, args=None, merge=1):
        """
        Parse the command line

        Keyword Arguments:
        args -- list of strings containing the command line.  If this is
           not given, sys.argv[1:] is used.
        merge -- boolean flag indicating whether parsed options should
           be merged into the configuration or not

        Returns:
        tuple -- two element tuple where the first element is a list of 
           parsed options in the form '(option, value)' and the second
           element is a list of unparsed arguments

        """
        if args is None: args = sys.argv[1:]

        shortopts, longopts = self.get_options_from_config()

        short_prefixes, long_prefixes = type(self).get_prefixes()

        opts = []
        while args and args[0] not in short_prefixes:

            # If the argument is equal to one of the long prefixes,
            # throw it away and bail out.
            if args[0] in long_prefixes:
                args = args[1:]
                break

            # Parse long options
            if [x for x in long_prefixes if args[0].startswith(x)]:
               try:
                  opts, args = self.do_longs(opts,args[0],longopts,args[1:])
               except UnrecognizedArgument, e:
                  if self.strict: raise
                  opts, args = self.handle_unrecognized(e[1],opts,args,'long')
                  if merge: self.unrecognized.append(opts[-1])

            # Parse short options
            elif [x for x in short_prefixes if args[0].startswith(x)]:
               try:
                  opts, args = self.do_shorts(opts,args[0],shortopts,args[1:])
               except UnrecognizedArgument, e:
                  if self.strict: raise
                  opts, args = self.handle_unrecognized(e[1],opts,args,'short')
                  if merge: self.unrecognized.append(opts[-1])

            # No option found.  We're done.
            else: break

        # Merge command line options with configuration
        if merge:
           self.merge_options(opts)
           self.check_mandatory_options()

        return opts, args

    def check_mandatory_options(self):
        """
        Make sure that all mandatory options have been set

        """
        for section in self.values():
           for option in section.values():
              if not option.mandatory: continue
              if option.getValue() in [None,[]]:
                 names = ', '.join(option.getPossibleOptions())
                 if not names:
                    names = option.name
                 raise MandatoryOption, ('The %s option is mandatory, but was not given' % names, names)

    def handle_unrecognized(self, option, opts, args, type='long'):
        """
        Try to parse unrecognized options and their arguments

        Required Arguments:
        option -- the actual option parsed from the command-line
           which was not recognized
        opts -- tuples of already parsed options and their values
        args -- remaining unparsed command-line arguments

        Keyword Arguments:
        type -- flag indicating which type of argument to parse.
           This should be either "short" or "long".

        """
        if type == 'long':

           args.pop(0)

           # Explicitly specified value
           if option.find('=') + 1:
              option, value = option.split('=',1)
              opts.append((option, value))
              return opts, args

           # Implicitly specified value
           if self.has_following_argument(args):
              opts.append((option, args.pop(0)))
              return opts, args

           # No argument found
           opts.append((option, None))
           return opts, args

        elif type == 'short':

           short_prefixes, long_prefixes = self.get_prefixes()
           prefix = [x for x in short_prefixes if option.startswith(x)][0]

           start, end = args[0].split(option.replace(prefix,'',1),1)
           if end: args[0] = prefix + end
           else: args.pop(0)

           opts.append((option, ''))
           return opts, args
        
        raise ValueError, 'Expecting type of "short" or "long".'

    def merge_options(self, options):
        """ Merge options parsed from the command line into configuration """
        from Generic import GenericOption
        from Multi import MultiOption

        # Multi options that have been cleared by a command line option.
        # Lists will only be cleared on the first command line option, all
        # consecutive options will append.
        for option, value in options:

#           opts = self.getPossibleOptions()
#           negative = [x.replace('!','',1) for x in opts if x.startswith('!')]
#           positive = [x for x in opts if not x.startswith('!')]

            if isinstance(option, GenericOption):
                option.source = COMMANDLINE
                option.file = None
                if type(value) in [list, tuple]:
                    if not isinstance(option, MultiOption):
                        value = ' '.join(value)
                        option.occurrences += 1
                        option.setValue(value)
                    else:
                        if option.occurrences:
                            option.occurrences += 1
                            option += value
                        else:
                            option.occurrences += 1
                            option.setValue(value)
                else:
                    option.occurrences += 1
                    option.setValue(value)

    def get_prefixes(cls):
        """ Prepare option prefixes to make sure that they are always lists """
        long_prefixes = cls.long_prefix
        short_prefixes = cls.short_prefix
        if type(long_prefixes) not in [list, tuple]:
           long_prefixes = [long_prefixes]
        if type(short_prefixes) not in [list, tuple]:
           short_prefixes = [short_prefixes]
        return [x for x in short_prefixes if x],[x for x in long_prefixes if x]

    get_prefixes = classmethod(get_prefixes)

    def do_longs(self, opts, opt, longopts, args):
        """
        Parse a long option

        Required Arguments:
        opts -- list of parsed options
        opt -- string containing current option
        longopts -- list of long option instances
        args -- remaining argument list

        Returns:
        tuple -- two element tuple where the first argument is the
           'opts' list with the latest argument added and the second
           element is the 'args' list with the arguments from the
           current option removed

        """
        forcedarg = False
        if opt.find('=') + 1:
            forcedarg = True
            opt, arg = opt.split('=', 1)
            args.insert(0, arg)

        option = self.get_match(opt, longopts)
        option.actual = opt
        option.file = None

        # If we have an argument, but the option doesn't accept one, bail out.
        if forcedarg and not(option.acceptsArgument()):
            raise UnspecifiedArgument('option %s must not have an argument' \
                                       % opt, opt)

        elif forcedarg:
           optarg, args = option.getArgument(args, forcedarg=True)

        elif not(option.acceptsArgument()):
           pass

        # Parse the following arguments
        else:

           # See if we have a possible following argument
           if not type(self).has_following_argument(args):

              # No argument found, but we require one.
              if option.requiresArgument():
                 raise RequiresArgument('option %s requires argument' \
                                         % opt, opt)

           # Parse the argument
           optarg, args = option.getArgument(args)

        # Convert boolean options to proper value
        if not forcedarg and isinstance(option, BooleanOption):
           options = option.getPossibleOptions()
           negative = [x.replace('!','',1) for x in options
                                           if x.startswith('!')]
#          positive = [x for x in options if not x.startswith('!')]
           if opt in negative:
              optarg = 0
           else:
              optarg = 1

        opts.append((option, optarg))
        return opts, args

    def has_following_argument(cls, args):
        """
        Return boolean indicating the existence of a following argument

        Required Arguments:
        args -- command-line arguments to inspect for following argument.

        Returns:
        boolean -- true, if following argument exists

        """
        short_prefixes, long_prefixes = cls.get_prefixes()

        # No arguments at all
        if not(args):
           return 0

        # The next argument has an option prefix and it doesn't consist
        # entirely of a prefix.
        if [x for x in long_prefixes+short_prefixes if args[0].startswith(x)] \
           and args[0] not in long_prefixes+short_prefixes:
           return 0

        # All other cases fail.  This must be an argument.
        return 1

    has_following_argument = classmethod(has_following_argument)

    def get_match(self, opt, longopts):
        """
        Get possible matches for the given option

        Required Arguments:
        opt -- name of the current option
        longopts -- list of all long option instances

        Returns:
        instance -- an instance of the option which matches

        """
        possibilities = []
        for o in longopts:
           match = o.matches(opt)
           if match:
              possibilities.append((match, o))

        if not possibilities:
            raise UnrecognizedArgument('option %s not recognized' % opt, opt)

        # Is there an exact match?
        option = [x for x in possibilities if opt == x[0]]
        if option:
            return option[0][1]

        # No exact match, so better be unique.
        if len(possibilities) > 1:
            # XXX since possibilities contains all valid continuations,
            # might be nice to work them into the error msg
            raise NonUniquePrefix('option %s not a unique prefix' % opt, opt)

        assert len(possibilities) == 1

        return possibilities[0][1]

    def do_shorts(self, opts, optstring, shortopts, args):
        """
        Parse a short argument

        Required Arguments:
        opts -- list of parsed options
        optstring -- string containing current option
        shortopts -- list of short option instances
        args -- remaining argument list

        Returns:
        tuple -- two element tuple where the first argument is the
           'opts' list with the latest argument added and the second
           element is the 'args' list with the arguments from the
           current option removed

        """
        short_prefixes, long_prefixes = type(self).get_prefixes()

        optstring.strip()

        if not optstring:
           return [], args 

        prefix = optstring[0]
        optstring = optstring[1:]

        while optstring != '':
            opt, optstring = optstring[0], optstring[1:]

            option = self.get_match(prefix+opt, shortopts)
            option.actual = prefix+opt
            option.file = None

            # See if we need to check for an argument
            if option.acceptsArgument():

                if optstring == '':

                   # Are there any following arguments?
                   if not type(self).has_following_argument(args):

                      # No argument found, but we require one.
                      if option.requiresArgument():
                         raise RequiresArgument('option %s requires argument' \
                                                 % opt, opt)

                   optarg, args = option.getArgument(args)

                else:
                   optarg, args = option.getArgument([optstring]+args)

                # No argument was found
                if args and args[0] == optstring:
                   optarg = None
                   optstring = args.pop(0)
                else:
                   optstring = ''

            else:
                optarg = None

            # Convert boolean options to proper value
            if optarg is None and isinstance(option, BooleanOption):
               options = option.getPossibleOptions()
               negative = [x.replace('!','',1) for x in options
                                               if x.startswith('!')]
#              positive = [x for x in options if not x.startswith('!')]
               if prefix+opt in negative:
                  optarg = 0
               else:
                  optarg = 1

            opts.append((option, optarg))

        return opts, args

    def usage_on(self, options):
        """
        Print full help for listed options and exit

        Required Arguments:
        options -- list of strings indicating which options to list
           help on (preceding '-' and '--' should be removed)

        """
        display = []
        for sectkey, section in self.items():
           for optkey, option in section.items():
              if option.long in options or option.short in options:
                 display.append((sectkey, optkey, option))

        display.reverse()

        err = sys.stderr.write

        while display:
           sectkey, optkey, opt = display.pop()
           err('Command Line: %s\n' % self._option_usage(opt))
           err('Configuration File: [%s] %s=\n' % (sectkey, optkey))

           current = opt.names()['current']
           if current != None: err('Current Value: %s\n\n' % current)
           else: err('\n')

           err('%s\n\n' % opt.description)
           if display: err('\n')

        sys.exit(1)

    def _option_usage(self, option):
        """ Return the option the way it can be typed at the command line """
        if option.options.strip():
           short_prefixes, long_prefixes = self.get_prefixes()
           prefixes = long_prefixes + short_prefixes
           options = re.sub(r'\s+', r' ', option.options.replace('!',''))
           options = options.split()
           options = [(len(x),x) for x in options
                       if [x for p in prefixes if x.startswith(p)]]
           options.sort()
           options = [x[1] for x in options]

           # Determine argument separator
           sep = ' '
           loptions = [x for x in options
                         if [x for p in long_prefixes if x.startswith(p)]]
           if loptions:
              sep = '='

           options = ', '.join(options)
           if option.acceptsArgument() and option.requiresArgument():
              return '%s%s%s' % (options, sep, option.synopsis)
           elif option.acceptsArgument():
              return '%s[%s%s]' % (options, sep, option.synopsis)
           else:
              return options
        return ''

    def usage(self, categories=[]):
        """ Print descriptions of all command line options """
        categories = categories[:]
        options = []
        for section in self.values():
            for option in section.data.values():
                if option.options:
                    options.append(option)
        options.sort()

        if not options: return ''

        name_len = 0
        summary_len = 0
 
        # Put options into categories
        categorized = {}
        for option in options:

            catname = self.get_category(option.category).strip()
            name = self._option_usage(option)

            summary = ''
            if option.summary:
               summary = option.summary % option.names()
               default = option.defaultValue()
               if default is not None:
                   summary += ' [%s]' % default

            if not categorized.has_key(catname):
               categorized[catname] = []
            categorized[catname].append((name,summary,option))

            if summary:
               name_len = max(name_len,len(name))
               summary_len = max(summary_len,len(summary))

        name_len = min(name_len, int(TERMINAL_WIDTH*MAX_NAME_WIDTH_RATIO))
        summary_len = TERMINAL_WIDTH - PREPAD - GUTTER - name_len

        # Build the output string
        s = ''
        if categories:
           categories = [self.get_category(x) for x in categories]
        else:
           categories = categorized.keys()
           categories.sort()
        for category in categories:
           options = categorized[category]
           if not category:
              if len(categories) > 1:
                 category = 'General Options'
              else:
                 category = 'Options'
           s += '\n%s:\n' % category
           for name, summary, option in options:
              length = len(name)
              summary = wrap(summary, summary_len)
              summary = ('\n%s' % (' '*(PREPAD+name_len+GUTTER))).join(summary)
              # Be lenient on the gutter if we are really close to
              # fitting in the allocated space
              format = '%s%s%s%s\n'
              colspace = max(GUTTER + name_len - length, GUTTER)
              if summary and ((name_len + GUTTER) > length):
                 colspace = (name_len + GUTTER) - length
              elif summary and length > name_len:
                 colspace = PREPAD + name_len + GUTTER
                 format = '%s%s\n%s%s\n'
              s += format % (' '*PREPAD, name, ' '*colspace, summary)
        return s
 

class CommandLineManager(ordereddict):
   """ Command-Line Argument Manager """

   def __init__(self, data={}):
      ordereddict.__init__(self, data)
      self._associations = {}

   def usage(self):
      s = ''
      for item in self.values():
         if isinstance(item, ConfigManager):
            s += item.usage()
         else:
            break
      return s

   def requiresArgument(self):
      """ Return boolean indicating if config requires an argument """
      if not self: return 0
      for key in self:
         item = ordereddict.__getitem__(self, key)
         if isinstance(item, GenericArgument):
             if item.mandatory:
                 return 1

   def getopt(self, args=None):
      if args == None:
         args = sys.argv[1:]
      else:
         args = args[:]

      if not self: return self

      for key in self:
         item = ordereddict.__getitem__(self, key)
         association = self._associations.get(key, None)
         if isinstance(item, ConfigManager):
            if association:
               item.read(association)
            options, args = item.getopt(args)
         elif isinstance(item, GenericArgument):
            value, args = item.getArgument(args)
            item.setValue(value)
         else:
            raise ValueError, "Unrecognized argument type."

      if len(args):
         raise TooManyValues, \
               'Too many command-line arguments: %s' % ' '.join(args)

      return self

   def __setitem__(self, key, value):
      item = value
      if type(value) in [types.TupleType, types.ListType]:
         value = list(value)
         item = value.pop(0)
         self._associations[key] = value
      assert isinstance(item, ConfigManager) or \
             isinstance(item, GenericArgument), \
             'Command-line parameters must be ConfigManagers or ' + \
             'subclasses of GenericArgument'
      if hasattr(item, 'name') and item.name is None:
         item.name = key
      ordereddict.__setitem__(self, key, item)

   def __getitem__(self, key):
      if type(key) == types.SliceType:
         return self.__getslice__(key.start, key.stop)
      item = ordereddict.__getitem__(self, key)
      if isinstance(item, ConfigManager):
         return item
      else:
         return item.getValue()



# These must be loaded last because they depend on variables
# assigned in this file.
from Generic import GenericOption, GenericArgument
from String import StringOption, StringArgument
from Integer import IntegerOption, IntegerArgument
from Float import FloatOption, FloatArgument
from Multi import MultiOption, MultiArgument
from Compound import CompoundOption, CompoundArgument
from Boolean import BooleanOption, BooleanArgument
from Files import OutputFileOption, InputFileOption
from Directories import OutputDirectoryOption, InputDirectoryOption
from Files import OutputFileArgument, InputFileArgument
from Directories import OutputDirectoryArgument, InputDirectoryArgument
from Counted import CountedOption, CountedArgument



if __name__ == '__main__':

    # Instantiate a new option parser
    op = ConfigManager()
    op.set_strict(FALSE)

    # Set option prefixes for short and long options.  If the short
    # prefix is set to None, all options will act like long options.
    ConfigManager.short_prefix = '-'
    ConfigManager.long_prefix = '--'

    debugging = op.add_category('debugging','Debugging')

    # Create a new section
    logging = op.add_section('logging')

    logging['compare'] = MultiOption(
       options = '--compare',
       range = [0,2],
       delim = ',',
       environ = 'COMPARE',
#      mandatory = 1,
       template = FloatOption, 
    )

    logging['testopts'] = CompoundOption(
       options = '--testopts',
       environ = 'TESTOPTS',
    )

    logging['verbose'] = BooleanOption(
       options = '--verbose -v !-q !--quiet',
       environ = 'VERBOSE',
       default = 0,
       category = 'debugging',
    )

    # Explicitly specify an integer option
    logging['debug'] = CountedOption(
       '''
       Set the debugging level

       This option sets the verbosity of debugging messages.

       ''',
       options = '--debug -d !-u',
       default = 0,
       environ = 'DEBUG',
       category = 'debugging',
    )

    # Explicitly specify another integer option
    logging['warning'] = IntegerOption(
       '''
       Set the warning level

       This option sets the verbosity of warning messages.

       Valid Values:
       The warning level must be an integer between 0 and 10.

       ''',
       options = '--warning -w',
       values = [0,10],
       default = 1
    )

    # Implicitly declare a float option
    logging['log'] = 1.2

    # Implicitly declare a float option
    logging['note'] = 2

    files = op.add_section('files')

    files['output-file'] = OutputFileOption(
       ''' Where the results will go. This is the output file that will contain your output ''',
       options = '--output-file -o',
       synopsis = 'OUTPUT-FILENAME',
    )

    files['input-file'] = InputFileOption(
       ''' Where the input will come from ''',
       options = '--input-file -i',
    )

    files['input-dir'] = InputDirectoryOption(
       ''' Where the input will come from ''',
       options = '--input-dir -I',
    )

    files['output-dir'] = OutputDirectoryOption(
       ''' Where the output will come from.  This must be a directory or it won\'t work ''',
       options = '--output-dir -D',
    )

    # Read in configuration files
    #op.read('/home/username/.myconfrc')
    op.read('./testconfig')

    # Call the option parser to parse the command line
    opts, args = op()

    # Print out current information
    print
    print '-- Parsed Options --'
    print
#   print opts
#   print args

#   print op['logging']['debug'], op.data['logging'].data['debug'].file
#   print op['logging']['compare'], op.data['logging'].data['compare'].file
    for option, value in opts:
        # Option was recognized
        if isinstance(option, GenericOption):
            print '%s.%s: %s' % (option.parent.name, option.name, value)
        # Unrecognized options
        else:
            print '(unknown) %s: %s' % (option, value)
    print

    # Print unrecognized options
    print '-- Unrecognized options --'
    print
    print op.unrecognized
    print

    # Print remaining unparsed arguments
    print '-- Remaining Arguments --'
    print
    print args
    print

    sources = \
    [('Command-Line Options', COMMANDLINE),
     ('Config File Options', CONFIGFILE),
     ('Environment Options', ENVIRONMENT),
     ('Builtin Options', BUILTIN)]

    for title, bit in sources:
       print '-- %s --' % title
       print
       for section in op.values():
          for option in section.values():
             if option.source & bit:
                print '%s.%s: %s' % (section.name, option.name, option.getValue())
       print

    # Print out a usage message
    print '-- Usage --'
    print
    print op.usage()
    print 

    # Print out a usage message for one category
    print '-- Single Category Usage --'
    print
    print op.usage(['debugging'])
    print 

    # Print out an INI representation of the current settings
    print '-- Current Configuration --'
    print
    print repr(op)

    print '-- Command-Line Manager --'
    print
    outputfile = StringArgument("Output File", name='foo', values=('add','subtract','multiply','divide'))
    number = IntegerArgument("Number of times to iterate", name='bar')
    clm = CommandLineManager(op, outputfile, number)
    print clm()
    for item in clm:
       print '%s: %s' % (type(item), item)
