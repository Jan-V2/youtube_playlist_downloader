import csv
from collections import defaultdict
import os
from my_logging import log_message as log, log_exept, get_timestamp


class Csv_Obj:
    # todo add collum methode
    # todo make this gud

    def __init__(self, header=None, data_array=None):
        if header is None:
            if data_array is None:
                log_exept('either the header data argument needs to contain data. they can\'t both be None')
                raise TypeError
            else:
                if type(data_array) is not list:
                    log_exept('data must be list type')
                    raise TypeError
        else:
            if type(header) is not list:
                log_exept('header must be list type')
                raise TypeError
            if type(data_array) is not list and data_array is not None:
                log_exept('data must be list type')
                raise TypeError

        if header is None:
            self.header = None
        else:
            self.header = defaultdict(str)
            for i in range(len(header)):
                self.header[header[i]] = i

        if data_array is None:
            self.data = []
        else:
            self.data = data_array

    def get_header_list(self):
        return self.header.keys()# todo does this work?

    def add_row_primitive(self, row):
        # todo make it so you can use col keys like in a database
        # this just adds a row to the data array
        self.data.append(row)

    def save_to_path(self, dir_path, file_name):
        writer = self.Data_Writer()
        writer.to_csv(dir_path, file_name + '.csv', self.data, self.header)

    class Data_Writer:
        def to_csv(self, dir_path, filename, data, header):
            log('writing csv to disk, at ' + dir_path + filename)
            file_existed = os.path.isfile(dir_path + filename)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(dir_path + filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=header.keys())
                if not file_existed:
                    writer.writeheader()
                for row in data:
                    self.__write_csv_line(row, header, writer)


        def __write_csv_line(self, row, header, writer):
            # todo add checking for this
            # WARNING assumes rows are list type
            row_dict = defaultdict(str)
            for key in header:
                row_dict[key] = str(row[header[key]])
            writer.writerow(row_dict)