
from pytube import YouTube
from my_utils.platform_vars import ROOTDIR, dir_sep
from my_utils.my_logging import  log, log_return

log_return()
log('starting app')
urls_file = "urls.txt"

with open(ROOTDIR + dir_sep + urls_file, 'r', encoding="utf-8") as file:
    urls = file.read()
    urls = urls.split('\n')
    for i in range(len(urls)):
        urls[i] = "www.youtube.com" + urls[i]


# todo add a feature where if you press a key it will stop after the video it's currently downloading.
# todo log the title of the video
# todo when the video is downloaded log the speed it was downloaded at
def download_urls(url_list):
        log("starting downloads")
        i = 1
        #for url in urls:
        url = urls[0]
        log('downloading url ' + str(i) + " out of " + str(len(urls)))
        resolutions = ['720p', '480p', '360p'] # it checks for resolutions according the order of the list
        downloaded = False
        for res in resolutions:
            if YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first() is not None:
                log('starting download at ' + res)
                YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first().download()
                delete_url_from_file(url)
                downloaded = True
                break
        if not downloaded:
            log('cannot download video @ ' + url)

        log('done')
        i += 1

def delete_url_from_file(url):
    # this method reads the file with the urls and deletes the one given in the argument
    # todo make it so that this method uses seeking to delete just one line instead of reading and then overwriting the whole file.
    with open(ROOTDIR + dir_sep + urls_file, 'r+', encoding="utf-8") as file:
        urls = file.read()
        urls = urls.split('\n')
        try:
            urls.remove(url)
        except ValueError:
            log('the url' + url + ' was not in the file')
        file.seek(0)
        file.truncate()
        for i in range(len(urls)):
            file.write(urls[i])
            if i < len(urls) - 1: # if this isn't the last item in the list
                file.write('\n')


download_urls(urls)
