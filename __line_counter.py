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
    except:
        print('\t' + f)
        pass

print(sum_)
print(lens)
print(len(lens), len(files))
