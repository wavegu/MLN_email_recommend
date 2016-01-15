import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def create_dir_if_not_exist(dir_path):
    import os
    if not os.path.exists(dir_path):
        print 'creating path:', dir_path
        os.mkdir(dir_path)


def del_a_from_b(a, b):
    if a not in b:
        return b
    part_pos = b.find(a)
    if part_pos + len(a) >= len(b):
        b = b[:part_pos]
    else:
        b = b[:part_pos] + b[(part_pos+len(a)):]
    return b


def is_a_in_b(a, b):
    a = str(a)
    b = str(b)
    if a not in b:
        return False
    start_pattern = a + ' '
    end_pattern = ' ' + a
    if (' ' + a + ' ') in b:
        return True
    if start_pattern in b and b.find(start_pattern) == 0:
        return True
    if end_pattern in b and b.find(end_pattern) == (len(b) - len(end_pattern)):
        return True
    return False


# get_known_top_1000()

if __name__ == '__main__':
    get_top_citation()
    get_known_top_1000()