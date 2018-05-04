import time
from os import listdir
from random import randint
import os
from os.path import isfile, join

import re
from pytube import YouTube, exceptions
from my_utils.platform_vars import ROOTDIR, dir_sep
from my_utils.my_logging import  log_message as log, log_return


log_return()
log('starting app')
urls_file = "Best_of_Steam_Greenlight_Trailer.yt"
path = "H:\\media\\youtube\\Jim_Sterling\\Best_of_Steam_Greenlight_Trailers\\" # can be none

with open(ROOTDIR + dir_sep + urls_file, 'r', encoding="utf-8") as file:
    raw_urls = file.read()
    raw_urls = raw_urls.split('\n')
    urls = []
    for item in raw_urls:
        urls.append("www.youtube.com" + item)




# todo add a feature where if you press a key it will stop after the video it's currently downloading.
# todo log the title of the video
# todo when the video is downloaded log the speed it was downloaded at
def download_urls():
        log("starting downloads")

        def r_wait():
            wait_len = randint(20, 30)
            print("waiting {} secs".format(wait_len))
            time.sleep(wait_len)

        i = 0
        for url in urls:
            log("downloading url {} out of  {}".format(i+1, len(urls)))
            resolutions = [ '720p', '480p', '360p'] # it checks for resolutions according the order of the list
            downloaded = False
            try:
                for res in resolutions:
                    if YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first() is not None:
                        log('starting download at ' + res)
                        YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first().download(output_path=path, )
                        delete_url_from_file(raw_urls[i])
                        downloaded = True
                        break
                if not downloaded:
                    log('cannot download video @ {} can\'t find stream'.format(url))
            except (exceptions.RegexMatchError, KeyError):
                log('cannot download video @ {}. the video has likely been deleted or privated.'.format(url))

            log('done')
            i += 1
            r_wait()

def delete_url_from_file(url):
    # this method reads the file with the urls and deletes the one given in the argument
    # todo make it so that this method uses seeking to delete just one line instead of reading and then overwriting the whole file.
    with open(ROOTDIR + dir_sep + urls_file, 'r+', encoding="utf-8") as _file:
        _urls = _file.read()
        _urls = _urls.split('\n')
        try:
            _urls.remove(url)
            log('the url ' + url + ' was removed from the queue')
        except ValueError:
            log('the url ' + url + ' was not in the file')
        _file.seek(0)
        _file.truncate()
        for i in range(len(_urls)):
            _file.write(_urls[i])
            if i < len(_urls) - 1: # if this isn't the last item in the list
                _file.write('\n')

def rename_files(_path, reverse):
    files = [f for f in listdir(_path) if isfile(join(_path, f))]

    def file_filter(file_name):
        regex = re.compile(".*\.mp4$")
        res = regex.match(file_name) is not None
        return res

    files = list(filter(file_filter, files))
    abs_p = lambda name: _path + dir_sep + name

    paths = sorted(files, key=lambda file_name: os.stat(abs_p(file_name)).st_mtime)
    if reverse:
        paths = reversed(paths)
    files = list(paths)

    for i in range(len(files)):
        num = str(i+1)
        if len(num) < 3:
            for f in range(3 - len(num)):
                num = "0" + num
        new_fname = num + " " + files[i]
        os.rename(abs_p(files[i]), abs_p(new_fname))


download_urls()
rename_files(path, True)
