import traceback
from pprint import pprint

import bs4
import time
from pip._vendor import urllib3
from selenium.common.exceptions import NoSuchElementException
from drivers import get_imagefree_driver
from my_utils.platform_vars import ROOTDIR, dir_sep
from my_utils.my_logging import log_message as log, log_return
from main import r_wait

playlist_file = ROOTDIR + dir_sep + "demodisk.yt"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scrape_descriptions(urls):
    try:
        driver = get_imagefree_driver(False)
        descriptions = []
        failed = []

        def scrape_description_and_title(_url):
            driver.get(_url)
            r_wait(6, 10)

            return [
                str(driver.find_element_by_id("description").text),
                str(driver.find_element_by_xpath("/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch/div[2]/div[2]/div/div[6]/div[2]/ytd-video-primary-info-renderer/div/h1/yt-formatted-string").text)
            ]

        def clean_descriptions(text):
            return text[:text.index("Follow us")]

        i = 1
        for url in urls:
            # url = urls[0]
            try:
                item = scrape_description_and_title(url)
                item[0] = clean_descriptions(item[0])
                descriptions.append(item)
            except (ValueError, NoSuchElementException) :
                print("failed to clean text")
                failed.append(url)

            print("did item {}/{}".format(i, len(urls)))
            i += 1
        return descriptions, failed
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        driver.close()  # YOU NEED TO HAVE A TRY EXECPT AROUND ALL OF THE CODE BECAUSE IF THIS FUNCION ISN'T CALLED FIREFOX WILL STAY RUNNING


def get_urls(path):
    with open(path, 'r', encoding="utf-8") as file:
        raw_urls = file.read()
        raw_urls = raw_urls.split('\n')
        urls = []
        for item in raw_urls[:-1]:
            urls.append("https://www.youtube.com" + item)
        return urls


if __name__ == '__main__':
    descriptions, failed = scrape_descriptions(get_urls(playlist_file))

    with open(ROOTDIR + dir_sep + "descriptons.html", "a", encoding="utf-8") as file:
        i = 1
        for item in descriptions:
            file.write("<h3>Episode {0}: {1} </h3>".format(i, item[1]))
            file.write("<p>")
            file.write(item[0])
            file.write("</p>")
            i += 1

    with open(ROOTDIR + dir_sep + "todo.txt", "w", encoding="utf-8") as file:
        for item in failed:
            file.write(item + "\n")
