import inspect
import os

def raise_custom_except(except_, message):
    try:
        raise except_
    except except_ as e:
        raise except_(str(message)).with_traceback(e.__traceback__)

def listmerger(lists):
    # takes an array of lists and merges them into 1 multidimentional list csv style
    for k in lists:
        if not type(k) is list:
            print("not all arguments are lists")
            raise TypeError
    length = -2
    for l in lists:
        if not length == -2:
            if len(l) != length:
                print("not all items given in argument are lists")
                raise ValueError
        else:
            length = len(l)

        ret = []
        for i in range(0, length):
            temp = []
            for lis in lists:
                temp.append(lis[i])
            ret.append(temp)
        return ret


def list_demerger(list_of_lists, index):
    # takes a list of lists and returns a list containing all the items in that index
    ret = []
    for line in list_of_lists:
        ret.append(line[index])
    return ret

def get_subdir_list(dir):
    # gets the names for all the subdirs one layer deep
    # (so only the dirs in the rootdir)
    for root, dirs, files in os.walk(dir, topdown=True):
        return dirs


def get_methods_from_class(class_arg):
    return inspect.getmembers(class_arg, predicate=inspect.ismethod)
		
def get_functions_from_class(class_arg):
    return inspect.getmembers(class_arg, predicate=inspect.isfunction)

def timestamp_to_datatime(timestamp_str):
    timestamp_str = timestamp_str.replace("]", '')
    timestamp_str = timestamp_str.replace("[", '')
    stamp_ints = []
    for i in timestamp_str.split('-'):
        for j in i.split('_'):
            stamp_ints.append(int(j))
    return datetime.datetime(year=stamp_ints[0], month=stamp_ints[1],day=stamp_ints[2],
                             hour=stamp_ints[3], minute=stamp_ints[4], second=stamp_ints[5])


def escape_string(string):
    escaped = string.translate(str.maketrans({"-":  r"\-",
                                              "]":  r"\]",
                                              "\\": r"\\",
                                              "^":  r"\^",
                                              "$":  r"\$",
                                              "*":  r"\*",
                                              ".":  r"\.",
                                              ",":  r"\,",
                                              "\n": r"\\n"}))
    return escaped




if __name__ == '__main__':
    pass
