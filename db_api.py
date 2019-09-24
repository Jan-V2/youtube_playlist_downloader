import sqlite3
import traceback
from my_utils.util_funcs import safe_filename
from pytube.__main__ import YouTube
from pytube.contrib.playlist import Playlist
from pytube import exceptions as pytube_excepts
from my_utils.my_logging import log_error, log_message as log
from enum import Enum
from collections import namedtuple

conn = sqlite3.connect('playlists.db')
cur = conn.cursor()

class STATUSES(Enum):
    failed = "failed"
    error = "error"
    queued = "in queue"
    downloaded = "finished"
    ignored = "ignored"
    unavailable = "unavailable"  # could mean it's age restricted



def init_db():
    cur.execute("CREATE TABLE IF NOT EXISTS Playlists(id integer primary key autoincrement NOT NULL,"
                " url TEXT NOT NULL , path TEXT NOT NULL, name TEXT, info TEXT  );")

    cur.execute("CREATE TABLE IF NOT EXISTS Videos(id integer primary key autoincrement NOT NULL,"
                "file_name TEXT NOT NULL, url TEXT NOT NULL, playlist_id INTEGER NOT NULL, status TEXT NOT NULL, title TEXT,"
                "length_in_secs INTEGER, description TEXT, time_downloaded DATETIME, stacktrace TEXT, md5_hash TEXT,"
                "    FOREIGN KEY (playlist_id) REFERENCES Playlists(id))")

    cur.execute("CREATE TABLE IF NOT EXISTS Sync_Attempts(id integer primary key autoincrement NOT NULL, "
                "playlist_id INTEGER NOT NULL, time DATETIME NOT NULL, success BOOLEAN NOT NULL, stacktrace TEXT,"
                "    FOREIGN KEY(playlist_id) REFERENCES Playlists(id))")


def insert_playlist(url, path, name, info=""):
    cur.execute("SELECT * FROM Playlists WHERE url = ?", [url])
    if cur.fetchone() is None:
        cur.execute("INSERT INTO Playlists(url, path, name, info) VALUES(?, ?, ?, ?)", (url, path, name, info))
        conn.commit()


def insert_video_list(video_urls, playlist_url):
    cur.execute("SELECT id FROM Playlists WHERE url = ?", [playlist_url])
    playlist_id = cur.fetchone()[0]
    i = 1
    for url in video_urls:
        cur.execute("SELECT * FROM Videos WHERE url = ?", [url])
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


def get_queued_urls():
    return __get_video_with_status(STATUSES.queued)


def get_failed_urls():
    return __get_video_with_status(STATUSES.failed)


def __get_video_with_status(status):
    cur.execute("SELECT url FROM Videos WHERE status = ?", [str(status)])
    return __list_of_collom(cur.fetchall())


def get_video_with_status_in_pl(status, pl_id):
    cur.execute("SELECT url FROM Videos WHERE status = ? AND  playlist_id = ?", [str(status), pl_id])
    return __list_of_collom(cur.fetchall())


def __list_of_collom(_list, idx=0):
    return list(map(lambda item: item[idx], _list))


def write_video_download_result(url, status, stacktrace=None):
    status = str(status)
    if stacktrace is None:
        cur.execute("UPDATE Videos SET status=?,time_downloaded=CURRENT_TIMESTAMP WHERE url=?", [status, url])
    else:
        cur.execute("UPDATE Videos SET status=?,time_downloaded=CURRENT_TIMESTAMP,stacktrace=? WHERE url=?", [status, url,  stacktrace])


