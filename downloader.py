import time
from random import randint

from pytube import YouTube
from my_utils.platform_vars import ROOTDIR, dir_sep
from my_utils.my_logging import  log_message as log, log_return


log_return()
log('starting app')
urls_file = "urls.txt"

with open(ROOTDIR + dir_sep + urls_file, 'r', encoding="utf-8") as file:
    raw_urls = file.read()
    raw_urls = raw_urls.split('\n')
    urls = []
    for item in raw_urls:
        urls.append("www.youtube.com" + item)

def r_wait():
    wait_len = randint(1, 6)
    print("waiting {} secs".format(wait_len))
    time.sleep(wait_len)


# todo add a feature where if you press a key it will stop after the video it's currently downloading.
# todo log the title of the video
# todo when the video is downloaded log the speed it was downloaded at
def download_urls():
        log("starting downloads")
        i = 0
        for url in urls:
            log("downloading url {} out of  {}".format(i+1, len(urls)))
            resolutions = [ '720p', '480p', '360p'] # it checks for resolutions according the order of the list
            downloaded = False
            for res in resolutions:
                if YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first() is not None:
                    log('starting download at ' + res)
                    YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first().download()
                    delete_url_from_file(raw_urls[i])
                    downloaded = True
                    break
            if not downloaded:
                log('cannot download video @ ' + url)

            log('done')
            i += 1
            r_wait()

def delete_url_from_file(url):
    # this method reads the file with the urls and deletes the one given in the argument
    # todo make it so that this method uses seeking to delete just one line instead of reading and then overwriting the whole file.
    with open(ROOTDIR + dir_sep + urls_file, 'r+', encoding="utf-8") as file:
        urls = file.read()
        urls = urls.split('\n')
        try:
            urls.remove(url)
            log('the url ' + url + ' was removed from the file')
        except ValueError:
            log('the url ' + url + ' was not in the file')
        file.seek(0)
        file.truncate()
        for i in range(len(urls)):
            file.write(urls[i])
            if i < len(urls) - 1: # if this isn't the last item in the list
                file.write('\n')


download_urls()
