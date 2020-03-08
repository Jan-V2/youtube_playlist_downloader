import datetime
import hashlib
import sqlite3
import time
import traceback
from random import randint

from my_utils.util_funcs import safe_filename
from pytube.__main__ import YouTube
from pytube.contrib.playlist import Playlist
from pytube import exceptions as pytube_excepts
from enum import Enum
from my_utils.my_logging import log_error, log_message as log, log_return


conn = sqlite3.connect('playlists.db')
cur = conn.cursor()

class STATUSES(Enum):
    failed = "failed"
    error = "error"
    queued = "in queue"
    downloaded = "downloaded"
    ignored = "ignored"
    unavailable = "unavailable"  # could mean it's age restricted, unlisted, ect.


def init_db():
    cur.execute("CREATE TABLE IF NOT EXISTS Playlists(id integer primary key autoincrement NOT NULL,"
                " url TEXT NOT NULL , path TEXT NOT NULL, name TEXT, info TEXT  );")

    cur.execute("CREATE TABLE IF NOT EXISTS Videos(id integer primary key autoincrement NOT NULL,"
                "file_name TEXT NOT NULL, url TEXT NOT NULL, playlist_id INTEGER NOT NULL, status TEXT NOT NULL, title TEXT,"
                "length_in_secs INTEGER, description TEXT, time_downloaded DATETIME, stacktrace TEXT, md5_hash TEXT,"
                "    FOREIGN KEY (playlist_id) REFERENCES Playlists(id))")

    cur.execute("CREATE TABLE IF NOT EXISTS Sync_Attempts(id integer primary key autoincrement NOT NULL, "
                "playlist_id INTEGER NOT NULL, time DATETIME NOT NULL, success BOOLEAN NOT NULL, stacktrace TEXT, "
                "    FOREIGN KEY (playlist_id) REFERENCES Playlists(id))")
    conn.commit()


def insert_playlist(url, path, name, info=""):
    # inserts playlist url into playlists table
    cur.execute("SELECT * FROM Playlists WHERE url = ?", [url])
    if cur.fetchone() is None:
        cur.execute("INSERT INTO Playlists(url, path, name, info) VALUES(?, ?, ?, ?)", (url, path, name, info))
        conn.commit()


def insert_video_list(video_urls, playlist_url, number_videos=False, reverse_numbering=False):
    # inserts a list of url into the db making sure there are no duplicates

    def _path_num_prefix_generator(_video_urls, min_digits=3, reverse=False):  # pragma: no cover
        """Generate number prefixes for the items in the playlist.

        If the number of digits required to name a file,is less than is
        required to name the last file,it prepends 0s.
        So if you have a playlist of 100 videos it will number them like:
        001, 002, 003 ect, up to 100.
        It also adds a space after the number.
        :return: prefix string generator : generator
        """
        digits = len(str(len(_video_urls)))
        if digits < min_digits:
            digits = min_digits
        if reverse:
            start, stop, step = (len(_video_urls), 0, -1)
        else:
            start, stop, step = (1, len(_video_urls) + 1, 1)
        return (str(i).zfill(digits) for i in range(start, stop, step) )

    cur.execute("SELECT id FROM Playlists WHERE url = ?", [playlist_url])
    prefix_gen = _path_num_prefix_generator(video_urls, reverse=reverse_numbering)
    try:
        playlist_id = cur.fetchone()[0]
    except Exception as e:
        if e.__class__ is TypeError:
            log_error("playlist not in db url:" + playlist_url)
            return
        raise e
    i = 1
    for url in video_urls:
        cur.execute("SELECT * FROM Videos WHERE url = ?", [url])
        vid_num = next(prefix_gen)
        if cur.fetchone() is None:
            # if the urls is not in the database
            try:
                print("inserting " + str(i) + " out of " + str(len(video_urls)))
                yt = YouTube(url)
                description = yt.description
                if description is None:
                    description = ""
                title = yt.title
                length = yt.length
                file_name = safe_filename(title)
                if number_videos:
                    file_name = vid_num + " " + file_name
                cur.execute("INSERT INTO Videos(file_name, url, playlist_id, status, title, description, length_in_secs) VALUES(?, ?, ?, ?, ?, ?, ?)",
                            (file_name, url, playlist_id, str(STATUSES.queued), title, description, length))
            except Exception as e:
                if e.__class__ is pytube_excepts.VideoUnavailable:
                    log("video at " + url + " is unavailable")
                    cur.execute("INSERT INTO Videos(file_name, url, playlist_id, status) VALUES(?, ?, ?, ?)",
                                ("Na", url, playlist_id, str(STATUSES.unavailable)))
                else:
                    log("failed to insert video into video table")
                    log("url: " + url)
                    traceback.print_exc()
            i += 1
    conn.commit()


def download_playlist(playlist_id):
    try:
        cur.execute("SELECT path FROM Playlists WHERE id = ?", [playlist_id])
        path = cur.fetchone()[0]
        cur.execute("SELECT url, file_name, status FROM Videos WHERE playlist_id = ?", [playlist_id])
        videos = cur.fetchall()
        videos = list(filter(lambda row: row[2].find("downloaded") is -1, videos))
    except Exception as e:
        log_error("error while fetching playlist from dbt")
        if e.__class__ is TypeError:
            log_error("playlist not in db :" + playlist_id)
            log_return()
            return
        log_error(traceback.format_exc())
        log_return()
        raise e

    def random_wait():
        # waits a random amount of time so the spam protection doesn't trigger as easily
        wait_len = randint(3, 16)
        print("waiting {} secs".format(wait_len))
        time.sleep(wait_len)

    log("starting downloads")
    i = 0
    for video in videos:
        url = video[0]
        file_name = video[1]
        log("downloading url {} out of  {}".format(i + 1, len(videos)))
        resolutions = ['720p', '480p', '360p']  # it checks for resolutions according the order of the list
        downloaded = False
        for res in resolutions:
            try:
                if YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first() is not None:
                    log('starting download at ' + res)
                    YouTube(url).streams.filter(res=res, progressive=True, mime_type="video/mp4").first().download(
                        output_path=path, filename=safe_filename(file_name))
                    __update_video_status(url, STATUSES.downloaded)
                    downloaded = True
                    break
            except Exception as e:
                log_error('error downloading video @ ' + url)
                __update_video_status(url, STATUSES.error, stacktrace=traceback.format_exc())
        if not downloaded:
            log('cannot download video @ ' + url)

        log('done')
        i += 1
        random_wait()




def md5_from_file(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_queued_urls():
    return __get_video_with_status(STATUSES.queued)


def get_failed_urls():
    return __get_video_with_status(STATUSES.failed)


def __get_video_with_status(status):
    cur.execute("SELECT url FROM Videos WHERE status = ?", status)
    return cur.fetchall()


def __list_of_collom(_list, idx=0):
    return list(map(lambda item: item[idx], _list))


def __update_video_status(url, status, stacktrace=None, md5=None):
    # todo other statuses
    if status is STATUSES.downloaded:
        cur.execute("UPDATE Videos SET status = ?, time_downloaded = ? where url == ?", [str(status), datetime.datetime.now(), url])
    elif status is STATUSES.error:
        cur.execute("UPDATE Videos SET status = ?, time_downloaded = ?, stacktrace = ? where url == ?", [str(status), datetime.datetime.now(), stacktrace, url])
    conn.commit()
    log("updated db")


if __name__ == '__main__':
    init_db()
    pl_urls = ["https://www.youtube.com/playlist?list=PLJ_TJFLc25JQaIKha3sduCHUXkFcNMMDS","https://www.youtube.com/playlist?list=UUu6mSoMNzHQiBIOCkHUa2Aw"]
    insert_playlist(pl_urls[0], "H:\\media\\youtube\\test", "RLM trailers")
    #insert_playlist(pl_urls[1], "/home/john/test2", "cody's lab channel playlist")

    for pl_url in pl_urls:
        pl = Playlist(pl_url)
        pl.populate_video_urls()
        insert_video_list(pl.video_urls, pl_url)
