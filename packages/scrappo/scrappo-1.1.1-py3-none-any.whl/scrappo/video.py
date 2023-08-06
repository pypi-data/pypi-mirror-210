import os

from scrappo.utils.log import show


class Video:
    def __init__(self, urls, output):
        self.urls = urls
        self.output = output
        self.errors = []

    def download(self):
        self.errors = []

        self.process_urls()

        return self.errors

    def process_urls(self):
        raise NotImplementedError('To be implemented')

    def add_folder(self, name, root=''):
        if not root:
            root = self.output

        parent_path = os.path.join(root, name)
        if not os.path.isdir(parent_path):
            os.mkdir(parent_path)
        return parent_path

    @staticmethod
    def file_exists(path):
        if os.path.isfile(path):
            show('Skipping existing video...\n')
            return True
        return False

    def add_errors(self, successful, path, url):
        if not successful:
            error = {'path': path, 'url': url}
            self.errors.append(error)

    @staticmethod
    def resolve_video_name(name, alt_name):
        if not name:
            name = alt_name
        return name
