"""
1835
bookcheckout.py: 384
bookrecommend.py: 373
bookreturn.py: 403
booksearch.py: 259
database.py: 278
menu.py: 138
"""

from os import listdir
from os.path import isfile, join


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


path = '.'
files = [f for f in listdir(path) if isfile(join(path, f))]
files = [f for f in files if not f.startswith('__') and f.endswith('.py')]

sum_ = 0
lens = {}
for f in files:
    try:
        lines = file_len(f)
        sum_ += lines
        lens[f] = lines
    except Exception:
        print('\t' + f)
        pass

print(sum_)
for f, l in lens.items():
    print(f'{f}: {l}')
#print(lens)
print(len(lens), len(files))
