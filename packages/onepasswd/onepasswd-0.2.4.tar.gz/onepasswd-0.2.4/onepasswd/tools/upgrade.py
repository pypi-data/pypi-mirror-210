import sys
import json
import shutil
import time
from onepasswd.onepasswd import DB


def upgrade(file):
    shutil.copyfile(file, '.' + file + '.' + str(time.time()) + '.bck.db')
    db = {}
    with open(file, "r") as fp:
        db = json.load(fp)
    new_db = {}
    for k, v in db.items():
        entry = [k]
        new_db[DB.cal_key(entry)] = {
            "entries": entry,
            "passwd": v['passwd'],
            "time": v['time']
        }
    with open(file, "w") as fp:
        json.dump(new_db, fp, indent=2)


def main():
    upgrade(sys.argv[1])


if __name__ == "__main__":
    main()
