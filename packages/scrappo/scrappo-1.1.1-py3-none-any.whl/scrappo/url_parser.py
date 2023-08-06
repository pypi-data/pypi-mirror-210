import os

from scrappo.utils.file import File
from scrappo.utils.log import throw


class UrlParser:
    def __init__(self, urls):
        self.urls = urls
        self.file_name = ''

    def parse(self):
        if os.path.isdir(os.path.dirname(self.urls[0])):
            try:
                urls_file = File(self.urls[0])

                # resolve file name without extension
                name = os.path.basename(self.urls[0]).split('.')
                name.pop()
                self.file_name = '.'.join(name)

                return self.parse_urls(urls_file.get_lines())

            except FileNotFoundError:
                throw(self.urls[0] + ' was not found.')

        return self.parse_urls(self.urls)

    @staticmethod
    def split_url(url):
        info = url.split(':::')
        if len(info) > 1:
            url = {'name': info[0], 'url': info[1]}
        else:
            url = {'name': '', 'url': info[0]}
        return url

    def parse_urls(self, urls_list):
        urls = []
        urls_found = []

        for url in urls_list:
            # remove '\n' from the string
            url = url.rstrip()

            # if it's a blank line it will append a new list
            if not url:
                urls.append(urls_found)
                urls_found = []
                continue

            urls_found.append(self.split_url(url))

        if len(urls_found) != 0:
            urls.append(urls_found)

        # just returns lists that are not empty
        urls = [list_not_empty for list_not_empty in urls if len(list_not_empty) > 0]

        return urls
