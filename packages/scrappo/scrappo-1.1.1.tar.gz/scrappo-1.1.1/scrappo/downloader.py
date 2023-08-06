import requests
from progress.bar import Bar
from progress.spinner import Spinner

from scrappo.utils.log import show


class Downloader:
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.is_done = False

    def download_video(self):
        try:
            chunk_size = 1024 * 1024
            headers = requests.get(self.url, stream=True).headers
            if 'Content-length' in headers:
                size = headers['Content-length']
                max_size = int(size) / chunk_size
                self.download_with_file_size(max_size, chunk_size)
            else:
                self.download_without_file_size(chunk_size)

        except (requests.exceptions.RequestException, OSError, IOError):
            show('Something wrong happened while opening/downloading the following URL:\n\t' + self.url + '(SKIPPED)')
            return False

        show(self.path + ' successfully downloaded!\n')
        return True

    def iterate_request(self, chunk_size, progress):
        request = requests.get(self.url, stream=True)
        video_file = open(self.path, 'wb')
        self.is_done = False

        for chunk in request.iter_content(chunk_size=chunk_size):
            video_file.write(chunk)
            progress.next()

        self.is_done = True
        video_file.close()
        request.close()

    def download_with_file_size(self, max_size, chunk_size):
        with Bar('Processing... ', max=max_size, suffix='%(percent)d%% - %(elapsed_td)s') as bar:
            self.iterate_request(chunk_size, bar)

    def download_without_file_size(self, chunk_size):
        spinner = Spinner('Processing... ')
        while not self.is_done:
            self.iterate_request(chunk_size, spinner)
