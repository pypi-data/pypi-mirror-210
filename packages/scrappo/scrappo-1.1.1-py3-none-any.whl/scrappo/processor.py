import os

from scrappo.movies import Movies
from scrappo.series import Series
from scrappo.url_parser import UrlParser
from scrappo.utils.log import show


class Processor:

    def __init__(self, arguments):
        self.urls = arguments.urls.value
        self.output = arguments.output.value
        self.type = arguments.type.value
        self.separate = arguments.separate.value

    def process(self):
        parser = UrlParser(self.urls)
        urls = parser.parse()

        path_main = self.output
        if not os.path.isdir(path_main):
            os.mkdir(path_main)

        videos = None
        if self.type == 'series':
            videos = Series(urls, path_main, parser.file_name)
        elif self.type == 'movies':
            videos = Movies(urls, path_main, self.separate)

        errors = videos.download()

        if len(errors) != 0:
            show('Following videos were not downloaded:')
            for error in errors:
                show('\t- ' + error['path'] + ': ' + error['url'], with_date=False)
