import os

from scrappo.downloader import Downloader
from scrappo.utils.log import show
from scrappo.video import Video


class Series(Video):
    def __init__(self, urls, output, file_name):
        super().__init__(urls, output)
        self.file_name = file_name

    def process_urls(self):
        parent_folder = self.add_folder(self.file_name)

        for i, season in enumerate(self.urls):
            show('Downloading season ' + str(i+1) + '...')
            season_folder = self.add_folder('season' + str(i+1), root=parent_folder)

            for j, episode in enumerate(season):
                url = episode['url']
                name = self.resolve_video_name(episode['name'], 'episode' + str(j + 1))
                show('Downloading ' + name + '...')

                path = os.path.join(season_folder, name + '.mp4')
                if self.file_exists(path):
                    continue

                successful = Downloader(url, path).download_video()

                self.add_errors(successful, path, url)
