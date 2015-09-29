# -*- svndumpfixit: extension -*-
# -*- coding: utf-8 -*-
__version__ = "0.1"
__author__ = "Alexander Thomas"
__author_email__ = "alexander@collab.net"
__home_page_url__ = ""
__bug_report_url__ = ""

# license if optional, if not specified assumes to be parent license.
__license__ = "GPLv3"

# If license text is optional, if plugin in under same license as the parent license.
__license_text__ = """

"""



class SampleExtension(ExtensionProvider):
#'command', case-insensitive alias for the command. which should be
# a single word build with [A-Z,a-z,0-9,_], and first char should
# be a letter, Any char outside this character set will be
# replaced with '_'.
    command = "sample"

#'alias', case-insensitive alias for the command. which should be
# a single word build with [A-Z,a-z,0-9,_], and first char should
# be a letter, Any char outside this character set will be
# replaced with '_'.
    alias   = "" # Optional

#'priority', set priority for command. When a command is implemented
# by multiple extensions, this will decided the priority and order in
# the execution chain. Accepts values in the range 1-10, if not set
# defaults to 10. 0 special priority.
    priority = 1 # Optional

    __description__ = ""
    __long_description__ = """   """


    def __init__(self):
        """ SampleExtension.__init__()"
        pass
