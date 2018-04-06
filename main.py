import bs4
from random import randint
import time
from my_utils.platform_vars import ROOTDIR, dir_sep
from drivers import get_imagefree_driver
import traceback

url = "https://www.youtube.com/playlist?list=PLbIc1971kgPBJNmKcUBivnqFTtk8F6IDY"
driver = get_imagefree_driver(True)

def  scrape_playlist(playlist_html):
    containers = bs4.BeautifulSoup(playlist_html, 'html.parser').find_all("ytd-playlist-video-renderer")
    print(len(containers))
    with open(ROOTDIR + dir_sep + "urls.txt", mode="w") as file:
        for cont in containers:
            file.write(cont.find("a", {"class":"yt-simple-endpoint"})["href"] + "\n")
        #print(cont.find("span", {"id":"video-title"})["title"])



def scrape_titles(page_source):
    pass

def get_ajaxed_html():

    def r_wait():
        wait_len = randint(1, 6)
        print("waiting {} secs".format(wait_len))
        time.sleep(wait_len)

    try:
        driver.get(url)
        items_per_page = 100

        def get_total_vids():
            stats_str = driver.find_element_by_id("stats").text

            def get_count(_stats_str, ret =""):
                if _stats_str[0].isdigit():
                    ret += _stats_str[0]
                    return get_count(_stats_str[1:], ret)
                else:
                    return int(ret)
            return get_count(stats_str)

        def do_pagedown_cycle():
            item_height_px = 100
            print("doing scroll...")
            driver.execute_script("window.scrollBy(0, {})".format(item_height_px * items_per_page + 100))


        num_vids = get_total_vids()
        if num_vids > items_per_page:
            got_items = items_per_page
            r_wait()
            while got_items < num_vids:
                do_pagedown_cycle()
                got_items += items_per_page
                r_wait()

        return driver.page_source

    except Exception:
        traceback.print_exc()
    finally:
        driver.close()  # YOU NEED TO HAVE A TRY EXECPT AROUND ALL OF THE CODE BECAUSE IS THIS FUNCION ISN'T CALLED FIREFOX WILL STAY RUNNING


def main():
    html = get_ajaxed_html()
    scrape_playlist(html)


if __name__ == '__main__':
    print("starting up...")
    main()