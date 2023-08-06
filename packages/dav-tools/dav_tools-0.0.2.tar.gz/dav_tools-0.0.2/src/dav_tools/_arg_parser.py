import argparse
from . import text_color

class ArgumentAction:
    STORE = 'store'
    STORE_CONST = 'store_const'
    STORE_TRUE = 'store_true'
    STORE_FALSE = 'store_false'
    APPEND = 'append'
    APPEND_CONST = 'append_const'
    COUNT = 'count'
    EXTEND = 'extend'
    BOOLEAN_OPTIONAL = argparse.BooleanOptionalAction


class ArgumentParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            epilog = text_color.get_colored_text('--Developed by Davide Ponzini (davide.ponzini95@gmail.com)', text_color.TextFormat.Style.ITALIC)
        )

        self.__groups = {}


    def set_version(self, version: str):
        self.parser.add_argument('--version', action='version', version=f'%(prog)s {version}')

    def set_description(self, description) -> None:
        self.parser.description = description

    @property
    def args(self) -> argparse.Namespace:
        return self.parser.parse_args()
    

    def __group(self, name: str, description: str = None) -> argparse._ArgumentGroup:
        if name in self.__groups:
            return self.__groups[name] 

        if description is None:
            group = self.parser.add_argument_group(name)
        else:
            group = self.parser.add_argument_group(name, text_color.get_colored_text(description, text_color.TextFormat.Style.ITALIC))

        self.__groups[name] = group
        return group

    def add_mutually_exclusive_group(self, parent: argparse._ArgumentGroup=None) -> argparse._MutuallyExclusiveGroup:
        if parent is None:
            parent = self.parser

        return parent.add_mutually_exclusive_group()

    def add_argument(self,
                     *name_or_flags,
                     group: argparse.ArgumentParser | argparse._ArgumentGroup | argparse._MutuallyExclusiveGroup | str=None,
                     **kwargs):
        if group is None:
            group = self.parser
        elif type(group) == str:
            group = self.__group(group)

        group.add_argument(*name_or_flags, **kwargs)

    def add_quiet_mode(self) -> None:
        self.add_argument('--quiet', group=self.__group('verbosity'), help='Suppresses all non-critical messages', action=ArgumentAction.STORE_TRUE)

    def add_verbose_mode(self) -> None:
        self.add_argument('--verbose', group=self.__group('verbosity'), help='Prints additional debug messages', action=ArgumentAction.STORE_TRUE)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.set_description('This module provides an easy-to-use way to handle command line arguments')
    argparser.set_version('1.0')

    argparser.add_argument('input_file', group='files', help='first input file', nargs='?')
    argparser.add_argument('input_file_2', group='files', help='second input file', nargs='*')
    argparser.add_argument('-o', '--output', group='files', help='output files', nargs='+')
    
    argparser.add_quiet_mode()
    argparser.add_verbose_mode()

    print(argparser.args)
