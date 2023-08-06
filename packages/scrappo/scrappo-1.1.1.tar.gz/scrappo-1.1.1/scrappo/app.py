from scrappo.processor import Processor
from scrappo.settings.manager import Manager


def main():
    arguments = Manager().configure_arguments()

    validate_settings(arguments['Settings'])

    videos = Processor(arguments['Settings'])
    videos.process()


def validate_settings(arguments):
    if arguments.shutdown.value:
        print('The computer will be shutdown when this program is done.\n')


if __name__ == '__main__':
    main()
