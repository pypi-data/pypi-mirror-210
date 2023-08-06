
from argparse import ArgumentParser, Namespace
from sys import exit as sys_exit

from .cfg_dict import CfgDict


class ParserTree(dict):
    def __init__(self, argparser: ArgumentParser):
        super().__init__()
        self.parser = argparser
        self.update(ParserTree.parser_to_tree(argparser))

    @staticmethod
    def parser_to_tree(argparser: ArgumentParser):
        new = {'parent': argparser}

        if argparser._actions:
            # make a new key dict that represents the parser's arguments
            new.update({
                'actions': {
                    action.dest: action
                    for action in
                    argparser._actions
                    if not action.default == '==SUPPRESS=='
                }
            })

        subparser = ParserTree.get_subparsers(argparser)
        if subparser:
            # make a new key dict that represents the parser's subparser and choices in a sub-ParserTree
            new['subparsers'] = {
                'group': subparser,
                'choices': {dest: ParserTree(parser) for dest, parser in subparser.choices.items()},
            }

        return new

    def get_defaults(self):
        return ParserTree.defaults_from_tree(self)

    def update_from_flattened(self, flattened):
        ParserTree.update_from_flattened_recurs(self, flattened)

    def disable_required(self):
        # returns a partial tree representing all of the actions that don't have a default
        return ParserTree._disable_required_with_defaults(self)

    def parse(self):
        # Main issue is that it doesn't take in account bad arguments
        known, _ = self['parent'].parse_known_args()

        if 'subparsers' in self:
            subparser = self['subparsers']['group']
            if subparser.default and subparser.default in self['subparsers']['choices']:
                return self.combine_namespaces(known, self['subparsers']['choices'][subparser.default].parse())
        return known

    @staticmethod
    def combine_namespaces(*namespaces: Namespace):
        dct = {}
        for namespace in namespaces:
            dct.update(namespace.__dict__)
        return Namespace(**dct)

    @staticmethod
    def get_subparsers(argparser: ArgumentParser):
        subparser = argparser._subparsers
        if subparser:
            return subparser._group_actions[0]

    @staticmethod
    def flatten(argdict: dict, sep='.'):
        out_dict = {}
        for key, value in argdict.items():
            if isinstance(value, dict):
                for subkey, subvalue in ParserTree.flatten(value, sep).items():
                    out_dict[f"{key}{sep}{subkey}"] = subvalue
            else:
                out_dict[key] = value
        return out_dict

    @staticmethod
    def defaults_from_tree(parser_tree):
        out = {}
        if 'actions' in parser_tree:
            out.update({
                dest: action.default
                for dest, action in parser_tree['actions'].items()
                if action.default != '==SUPPRESS=='
            })
        if 'subparsers' in parser_tree:
            out.update({
                dest: subparser.get_defaults()
                for dest, subparser in parser_tree['subparsers']['choices'].items()
            })
        return out

    @staticmethod
    def update_from_flattened_recurs(original, flattened):
        for key, item in flattened.items():
            if '.' in key:
                key, future = key.split(".", 1)
                if 'subparsers' in original and key in original['subparsers']['choices']:
                    ParserTree.update_from_flattened_recurs(original['subparsers']['choices'][key], {future: item})
            else:
                if 'actions' in original and key in original['actions']:
                    original['actions'][key].default = item

    @staticmethod
    def _disable_required_with_defaults(subtree):
        still_required = {}
        if 'actions' in subtree:
            for dest, action in subtree['actions'].items():
                if action.required:
                    if action.default:
                        action.required = False
                    else:
                        if 'actions' not in still_required:
                            still_required['actions'] = {}
                        still_required['actions'][dest] = action
                        action.required = False
        if 'subparsers' in subtree:
            still_required['subparsers'] = {'choices': {}}
            for dest, subtree in subtree['subparsers']['choices'].items():
                out = subtree.disable_required()
                if out:
                    still_required['subparsers']['choices'].update({dest: out})

        return still_required

    @staticmethod
    def reenable_required(required):
        if 'actions' in required:
            for dest, action in required['actions'].items():
                if not action.default:
                    action.required = True
        if 'subparsers' in required:
            for dest, subparser in required['subparsers']['choices'].items():
                ParserTree.reenable_required(subparser)

    # def __getitem__(self, key):
    #     if not isinstance(key, tuple):
    #         return super().__getitem__(key)
    #     else:
    #         return self.subparsers[key[0]][key[1:]]


def update_from_flattened(original, flattened):
    for key, value in flattened.items():
        if '.' in key:
            key, future = key.split('.', 1)
            if key not in original:
                original[key] = {}
            update_from_flattened(original[key], {future: value})
        else:
            original[key] = value


class ConfigArgParser:
    '''an easy argparse config utility. It saves given args to a json, and returns them when args are parsed again.'''

    def __init__(self,
                 parser: ArgumentParser,
                 config_path: str,
                 cfgObject: CfgDict = None,
                 exit_on_change: bool = False,
                 argument_group_name: str = "Config options"):
        """Constructs a parser wrapper.

        Parameters
        ----------
        parser : ArgumentParser
            parser to wrap.
        config_path : str
            the path to the json file.
        cfgObject : CfgDict, optional
            if desired, update an existing CfgDict object, by default None
        exit_on_change : bool, optional
            exits when set, reset, or reset_all is called, by default False
        argument_group_name : str, optional
            name of the argument group, by default "Config options"

        """

        # parent parser
        self.parser = parser
        self.default_prefix = self.parser.prefix_chars[0]
        self.exit_on_change = exit_on_change
        self.file = cfgObject or CfgDict(config_path)

        # Add config options
        self.config_option_group = self.parser.add_argument_group(argument_group_name)
        self.config_options = self.config_option_group.add_mutually_exclusive_group()
        self.config_options.add_argument(self.default_prefix * 2 + "set", nargs=2, metavar=('KEY', 'VAL'),
                                         help="change a default argument's options")
        self.config_options.add_argument(self.default_prefix * 2 + "reset", metavar='VALUE', nargs="*",
                                         help="removes a changed option.")
        self.config_options.add_argument(self.default_prefix * 2 + "reset_all", action="store_true",
                                         help="resets every option.")

        # get defaults from the actions
        # self.parser_tree = get_parser_tree(self._parent)
        self.parser_tree = ParserTree(self.parser)

    def parse_args(self, **kwargs) -> Namespace:
        '''args.set, reset, reset_all logic. Also a passthrough for parser.parse_args.'''

        self.file.load()

        # Add subparsers to the dict so it can be configured
        self.parser_tree.update_from_flattened(ParserTree.flatten(self.file))

        self.kwargs = ParserTree.flatten(self.parser_tree.get_defaults())

        # disable every required item that wasn in the file
        still_required = self.parser_tree.disable_required()

        self.parsed_args, _ = self.parser.parse_known_args(**kwargs)

        # TODO: make set, reset, and reset_all work for subparsers
        # set defaults
        if self.parsed_args.set or self.parsed_args.reset or self.parsed_args.reset_all:
            if self.parsed_args.set:
                potential_args = self.parsed_args.set
                # convert potential_args to respective types
                potential_args = self._convert_type(potential_args)
                if not potential_args[0] in self.kwargs:
                    sys_exit("Given key not found")

                update_from_flattened(self.file, {potential_args[0]: potential_args[1]})

            elif self.parsed_args.reset:
                for arg in self.parsed_args.reset:
                    self._pop_from_flattened(self.file, arg)

            elif self.parsed_args.reset_all:
                self.file.clear()
            self.file.save().load()

            if self.exit_on_change:
                sys_exit()

        # edit defaults
        self.parser_tree.update_from_flattened(ParserTree.flatten(self.file))

        # reenable every required item except for the ones with defaults
        ParserTree.reenable_required(still_required)

        # sys_exit()
        self.parser.parse_args()

        return self.parser_tree.parse()

    @staticmethod
    def _convert_type(potential_args: list) -> list:
        arg_replacements = {"true": True, "false": False,
                            "none": None, "null": None}
        potential_args[1] = arg_replacements.get(
            potential_args[1].lower(), potential_args[1])
        if str(potential_args[1]).isdigit():
            potential_args[1] = int(potential_args[1])
        return potential_args
