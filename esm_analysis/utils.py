# @Author: Paul Gierz <pgierz>
# @Date:   2020-02-18T07:26:10+01:00
# @Email:  pgierz@awi.de
# @Filename: utils.py
# @Last modified by:   pgierz
# @Last modified time: 2020-02-18T07:32:33+01:00


def sizeof_fmt(num, suffix="B"):
    """ Formats a size in bytes to human readable """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, "Y", suffix)


def full_size_of_filelist(flist):
    """ Given a list of files, gets the full size (in bytes) """
    total_size = 0
    for f in flist:
        total_size += os.stat(f).st_size
    return total_size
