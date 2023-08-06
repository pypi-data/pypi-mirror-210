import argparse

from margument.argument import Argument
from margument.arguments import Arguments

from scrappo.utils.directory import Directory
from scrappo.utils.log import throw


class Settings(Arguments):
    def __init__(self):
        self.urls = Argument(name='urls',
                             abbreviation_name='-u',
                             full_name='--urls',
                             help_message='A list of URLs of the videos to download or the path of a .txt file containing a list of URLs. More '
                                          'details on creating the file in the README.md',
                             metavar="",
                             default=[])

        self.output = Argument(name='output',
                               abbreviation_name='-o',
                               full_name='--output',
                               help_message='The output folder path in which the videos will be downloaded.',
                               metavar="",
                               default='')

        self.type = Argument(name='type',
                             abbreviation_name='-t',
                             full_name='--type',
                             help_message='The type of the videos to download. Choices are "movies" or "series". The difference between the two '
                                          'is that a series expects to have seasons and these will be separated in different folders. Default is '
                                          '"movies".',
                             metavar="",
                             choices=['movies', 'series'],
                             default='movies')

        self.separate = Argument(name='separate',
                                 abbreviation_name='',
                                 full_name='--separate',
                                 help_message='If enabled, it will separate every movie into his own folder. Default is disabled. True: --separate | '
                                              'False: --no-separate',
                                 metavar="",
                                 default=False)

        self.shutdown = Argument(name='shutdown',
                                 abbreviation_name='',
                                 full_name='--shutdown',
                                 help_message='Enable/disable if computer will shutdown when the program has ended. Default is disabled.'
                                              'True: --shutdown | False: --no-shutdown',
                                 metavar="",
                                 default=False)

    def add_arguments(self, args_parser):
        args_parser.add_argument(self.urls.abbreviation_name, self.urls.full_name,
                                 nargs='*',
                                 required=True,
                                 help=self.urls.help_message,
                                 default=argparse.SUPPRESS)

        args_parser.add_argument(self.output.abbreviation_name, self.output.full_name,
                                 type=str,
                                 required=True,
                                 help=self.output.help_message,
                                 default=argparse.SUPPRESS)

        args_parser.add_argument(self.type.abbreviation_name, self.type.full_name,
                                 type=str,
                                 required=True,
                                 choices=self.type.choices,
                                 help=self.type.help_message,
                                 default=argparse.SUPPRESS)

        args_parser.add_argument(self.separate.full_name,
                                 action=argparse.BooleanOptionalAction,
                                 help=self.separate.help_message,
                                 default=argparse.SUPPRESS)

        args_parser.add_argument(self.shutdown.full_name,
                                 action=argparse.BooleanOptionalAction,
                                 help=self.shutdown.help_message,
                                 default=argparse.SUPPRESS)

    def process_arguments(self, settings):
        self.validate_path(settings[0].user_arguments)

    def validate_path(self, user_args):
        if self.output.name in user_args:
            argument_path = Directory(user_args.output)
            if not argument_path.exists():
                throw(user_args.output + ' path does not exist.')
