#!/usr/bin/env python

import string

class category(int): pass

CC_ESCAPE = category(0)
CC_BGROUP = category(1)
CC_EGROUP = category(2)
CC_MATHSHIFT = category(3)
CC_ALIGNMENT = category(4)
CC_EOL = category(5)
CC_PARAMETER = category(6)
CC_SUPER = category(7)
CC_SUB = category(8)
CC_IGNORED = category(9)
CC_SPACE = category(10)
CC_LETTER = category(11)
CC_OTHER = category(12)
CC_ACTIVE = category(13)
CC_COMMENT = category(14)
CC_INVALID = category(15)

# Special category codes for internal use
CC_EXPANDED = category(100)
CC_ENDTOKENS = category(101)

# Default TeX category codes
CATEGORIES = [
   '\\',  # 0  - Escape character
   '{',   # 1  - Beginning of group
   '}',   # 2  - End of group
   '$',   # 3  - Math shift
   '&',   # 4  - Alignment tab
   '\n',  # 5  - End of line
   '#',   # 6  - Parameter
   '^',   # 7  - Superscript
   '_',   # 8  - Subscript
   '\x00',# 9  - Ignored character
   ' \t\r\f', # 10 - Space
   string.letters + '@', # - Letter
   '',    # 12 - Other character - This isn't explicitly defined.  If it
          #                        isn't any of the other categories, then
          #                        it's an "other" character.
   '~',   # 13 - Active character
   '%',   # 14 - Comment character
   ''     # 15 - Invalid character
]
