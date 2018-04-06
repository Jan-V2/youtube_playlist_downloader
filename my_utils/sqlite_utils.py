import sqlite3
import threading
from multiprocessing import cpu_count
from queue import Queue
import time
from multiprocess.pool import Pool

from my_utils.my_logging import set_logfile_name, log_message as log

set_logfile_name("sqlite utils")


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        print("connected to " + db_file)
        return conn
    except sqlite3.Error as e:
        print(e)


class DB_Getter:
    # todo make this a generator?
    def __init__(self, db_path, query, max_fetch):
        self.cursor = create_connection(db_path).cursor()
        self.cursor.execute(query)
        self.maxfetch = max_fetch

    def get(self):
        ret = self.cursor.fetchmany(self.maxfetch)
        if len(ret) < 1:
            return None
        return ret

    async def get_async(self):
        return self.get()


class DB_Putter:
    def __init__(self, db_path, query, clear):
        self.db = create_connection(db_path)
        self.cursor = self.db.cursor()
        self.query = query

    def put(self, data):
        self.cursor.executemany(self.query, data)
        self.db.commit()

    async def put_async(self, data):
        self.put(data)


class DB_Filter:
    # todo there is a problem where if the filter thread crashes the others don't stop
    def __init__(self, db_from_path, db_to_path, pull_query, put_query, max_fetch, filter, logging_func, clear_input):
        self.db_getter_args = (db_from_path, pull_query, max_fetch)
        self.db_putter_args = (db_to_path, put_query, clear_input)
        self.filter = filter
        self.input_q = Queue(3)
        self.output_q = Queue(3)
        self.log = logging_func

    def perform_filter(self):
        self.log("starting")
        run_funcs_in_threads([self.__filter_loop, self.__db_getter_loop, self.__db_putter_loop])

    def __filter_loop(self):
        t_pool = Pool(cpu_count() - 1)
        while True:
            data = self.__pull_from_q(self.input_q)
            if data is not None:
                self.log("filtering data")
                self.__push_to_q(t_pool.map(self.filter, data), self.output_q)
            else:
                self.__push_to_q(None, self.output_q)
                t_pool.close()
                self.log("filter done")
                break

    def __db_getter_loop(self):
        args = self.db_getter_args
        db_getter = DB_Getter(args[0], args[1], args[2])
        put_in_input = lambda data: self.__push_to_q(data, self.input_q)
        self.__q_db_transport_loop(db_getter.get, put_in_input, "getter")

    def __db_putter_loop(self):
        args = self.db_putter_args
        db_putter = DB_Putter(args[0], args[1], args[2])
        def db_putter_wrapper(data):
            if data is not None:
                db_putter.put(data)
        pull_from_output = lambda: self.__pull_from_q(self.output_q)
        self.__q_db_transport_loop(pull_from_output, db_putter_wrapper, "putter")

    def __q_db_transport_loop(self, data_getter, dest_func, name):
        while True:
            data = data_getter()
            if data is None:
                dest_func(None)
                self.log(name + " done")
                break
            self.log(name + " got data")
            dest_func(data)

    def __pull_from_q(self, q):
        while True:
            if not q.empty():
                return q.get()
            else:
                time.sleep(1)

    def __push_to_q(self, item, q):
        while True:
            if not q.full():
                q.put(item)
                break
            else:
                time.sleep(1)

def run_funcs_in_threads(funcs):
    threads = []
    for func in funcs:
        thread = threading.Thread(target=func)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
