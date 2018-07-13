from my_utils.platform_vars import ROOTDIR, dir_sep

path = ROOTDIR + dir_sep + "demodisk.yt"


with open(path, 'r', encoding="utf-8") as file:
    raw_urls = file.read()
    raw_urls = raw_urls.split('\n')
    urls = []
    for item in raw_urls:
        print("https://www.youtube.com" + item)