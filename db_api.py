import sqlite3
import traceback
from my_utils.util_funcs import safe_filename
from pytube.__main__ import YouTube
from pytube.contrib.playlist import Playlist
from pytube import exceptions as pytube_excepts
from my_utils.my_logging import log_error, log_message as log

conn = sqlite3.connect('playlists.db')
cur = conn.cursor()

class VIDEO_STATUSES:
    def __init__(self):
        self.failed = "failed"
        self.failed = "error"
        self.queued = "in queue"
        self.finished = "finished"
        self.ignored = "ignored"
        self.unavailable = "unavailable"# can mean it's age restricted

STATUSES = VIDEO_STATUSES()

def init_db():
    cur.execute("CREATE TABLE IF NOT EXISTS Playlists(id integer primary key autoincrement NOT NULL,"
                " url TEXT NOT NULL , path TEXT NOT NULL, name TEXT, info TEXT  );")

    cur.execute("CREATE TABLE IF NOT EXISTS Videos(id integer primary key autoincrement NOT NULL,"
                "file_name TEXT NOT NULL, url TEXT NOT NULL, playlist_id INTEGER NOT NULL, status TEXT NOT NULL, title TEXT,"
                "length_in_secs INTEGER, description TEXT, download_time DATETIME, stacktrace TEXT,"
                "    FOREIGN KEY (playlist_id) REFERENCES Playlists(id))")

    cur.execute("CREATE TABLE IF NOT EXISTS Sync_Attempts(id integer primary key autoincrement NOT NULL, "
                "playlist_id INTEGER NOT NULL, time DATETIME NOT NULL, success BOOLEAN NOT NULL, stacktrace TEXT, "
                "    FOREIGN KEY (playlist_id) REFERENCES Playlists(id))")


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
                            (file_name, url, playlist_id, STATUSES.queued, title, description, length))
            except Exception as e:
                if e.__class__ is pytube_excepts.VideoUnavailable:
                    log("video at " + url + " is unavailable")
                    cur.execute("INSERT INTO Videos(file_name, url, playlist_id, status) VALUES(?, ?, ?, ?)",
                                ("Na", url, playlist_id, STATUSES.unavailable))
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
    cur.execute("SELECT url FROM Videos WHERE status = ?", status)
    return cur.fetchall()

if __name__ == '__main__':
    init_db()
    pl_urls = ["https://www.youtube.com/playlist?list=PLJ_TJFLc25JQaIKha3sduCHUXkFcNMMDS","https://www.youtube.com/playlist?list=UUu6mSoMNzHQiBIOCkHUa2Aw"]
    insert_playlist(pl_urls[0], "/home/john/test", "RLM trailers")
    insert_playlist(pl_urls[1], "/home/john/test2", "cody's lab channel playlist")

    for pl_url in pl_urls:
        pl = Playlist(pl_url)
        pl.populate_video_urls()
        insert_video_list(pl.video_urls, pl_url)