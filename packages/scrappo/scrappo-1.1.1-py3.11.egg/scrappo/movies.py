import os

from scrappo.downloader import Downloader
from scrappo.utils.log import show
from scrappo.video import Video


class Movies(Video):
    def __init__(self, urls, output, separate):
        super().__init__(urls, output)
        self.separate = separate

    def process_urls(self):
        # returns a flat list
        urls = [item for sublist in self.urls for item in sublist]

        for index, movie in enumerate(urls):
            url = movie['url']
            name = self.resolve_video_name(movie['name'], 'movie' + str(index + 1))
            show('Downloading ' + name + '...')

            parent_path = self.output
            if self.separate:
                parent_path = self.add_folder(name)

            path = os.path.join(parent_path, name + '.mp4')
            if self.file_exists(path):
                continue

            successful = Downloader(url, path).download_video()

            self.add_errors(successful, path, url)
