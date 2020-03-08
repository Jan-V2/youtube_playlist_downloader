from db_api import *
import db_api

def download_playlist(id):
    urls = download_playlist( id)
    pass

if __name__ == '__main__':
    init_db()
    #download_playlist(1)
    pl_urls = ["https://www.youtube.com/playlist?list=PLJ_TJFLc25JQaIKha3sduCHUXkFcNMMDS", "https://www.youtube.com/playlist?list=UUu6mSoMNzHQiBIOCkHUa2Aw"]
    #insert_playlist(pl_urls[0], "/home/john/test", "RLM trailers")
    #insert_playlist(pl_urls[1], "/home/john/test2", "cody's lab channel playlist")

    for pl_url in pl_urls:
         pl = Playlist(pl_url)
         pl.populate_video_urls()
         insert_video_list(pl.video_urls, pl_url)

