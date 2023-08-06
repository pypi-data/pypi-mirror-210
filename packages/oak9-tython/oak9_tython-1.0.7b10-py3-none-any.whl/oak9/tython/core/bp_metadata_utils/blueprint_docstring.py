import re
from core.bp_metadata_utils.policy_implementation_docstring import PolicyImplementationDocstring

# implements_pattern = re.compile('^\s+Implements:\s*[\r\n](?P<desc>[\S\s]+)Returns', re.MULTILINE)
# desc_pattern = re.compile('^\s+Desc:\s*[\r\n](?P<desc>[\S\s]+)Implements', re.MULTILINE)

author_pattern = re.compile('(Author:\n\s+((((?P<author>.+(?:\n.*?|\Z)+(\s*)))(Name:|Desc:|\Z))))', re.MULTILINE)
desc_pattern = re.compile('(Desc:\n\s+((((?P<desc>.+(?:\n.*?|\Z)+(\s*)))(Name:|Author:|\Z))))', re.MULTILINE)
no_desc_pattern = re.compile('(((((?P<nodesc>.+(?:\n.*?|\Z)+(\s*)))(Name:|Author:|\Z))))', re.MULTILINE)
name_pattern = re.compile('(Name:\n\s+((?P<name>.+(?:\n.*?|\Z)+(\s*))(Desc:|Author:|\Z)))', re.MULTILINE)


class BlueprintDocstring(PolicyImplementationDocstring):
    """Representation of a docstring for a customer blueprint.

    Author:
        ashah@oak9.io

    Name:
        Aakash's Blueprint

    """

    @property
    def name(self) -> str:
        """
        Returns blueprint name
        """
        name = self._get_str_field(name_pattern, 'name', "Blueprint name was not provided in docstring")
        return name

    @property
    def desc(self) -> str:
        """
        Returns blueprint name
        """
        empty_msg = "No description provided in docstring"
        desc = self._get_str_field(desc_pattern, 'desc', empty_msg)
        if desc == empty_msg:
            desc = self._get_str_field(no_desc_pattern, 'nodesc', empty_msg)


        return desc

    @property
    def author(self) -> str:
        """
        Returns blueprint name
        """
        author = self._get_str_field(author_pattern, 'author', "No description provided in docstring")
        return author


