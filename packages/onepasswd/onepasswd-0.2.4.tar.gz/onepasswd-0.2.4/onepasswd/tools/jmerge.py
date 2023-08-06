import json
import os
import sys
import colored
import time
import shutil
import tempfile
from onepasswd import ltlog

log = ltlog.getLogger('onepasswd.tools.jmerge')


def log_diff(tag, op, color, key, v):
    print("%s [%s] [%s] {%s: %s} %s"
          % (colored.fg(color),
             tag,
             op,
             key,
             json.dumps(v),
             colored.attr('reset')))


def log_local_add(key, v):
    log_diff("L", "+", "green", key, v)


def log_local_del(key, v):
    log_diff("L", "-", "red", key, v)


def log_remote_add(key, v):
    log_diff("R", "+", "blue", key, v)


def log_remote_del(key, v):
    log_diff("R", "-", "yellow", key, v)


def merge(fa, fb):
    log.debug(fa + ' ' + fb)
    tmp_bck_file = os.path.join(tempfile.gettempdir(), os.path.basename(
        fa) + '.' + str(time.time()) + '.bck')
    print("you can find backup file here:", tmp_bck_file)
    shutil.copyfile(fa, tmp_bck_file)
    ja, jb = {}, {}
    with open(fa, "r") as fpa:
        ja = json.load(fpa)
    with open(fb, "r") as fpb:
        jb = json.load(fpb)

    for keya, vala in ja.items():
        if keya not in jb:
            log_remote_add(keya, vala)
        elif jb[keya] != vala:
            at = float(vala['time'])
            bt = float(jb[keya]['time'])
            if at < bt:
                log_local_del(keya, vala)
                log_local_add(keya, jb[keya])
                ja[keya] = jb[keya]
            else:
                log_remote_del(keya, jb[keya])
                log_remote_add(keya, vala)
    for keyb, valb in jb.items():
        if keyb not in ja:
            log_local_add(keyb, valb)
            ja[keyb] = valb
    with open(fa, "w") as fpa:
        json.dump(ja, fpa, indent=2)


def main():
    assert len(sys.argv) == 3
    merge(*sys.argv[1:])


if __name__ == "__main__":
    main()
