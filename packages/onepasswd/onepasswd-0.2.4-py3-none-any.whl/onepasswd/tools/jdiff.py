#!/usr/bin/python3

import json
import sys
import colored


def diff(fa, fb):
    fpa = open(fa)
    fpb = open(fb)

    ja = json.load(fpa)
    jb = json.load(fpb)

    for keya, vala in ja.items():
        if keya not in jb:
            print("%s [A] {%s: %s} %s"
                  % (colored.fg('red'),
                     keya, json.dumps(vala, indent=4),
                     colored.attr('reset')))
        elif jb[keya] != vala:
            print("%s [A] {%s: %s} %s"
                  % (colored.fg('red'),
                     keya, json.dumps(jb[keya], indent=4),
                     colored.attr('reset')))
            print("%s [B] {%s: %s} %s"
                  % (colored.fg('green'),
                     keya, json.dumps(vala, indent=4),
                     colored.attr('reset')))

    for keyb, valb in jb.items():
        if keyb not in ja:
            print("%s [B] {%s: %s} %s"
                  % (colored.fg('green'),
                     keyb, json.dumps(valb),
                     colored.attr('reset')))
    fpa.close()
    fpb.close()


def main():
    assert len(sys.argv) == 3
    diff(*sys.argv[1:])


if __name__ == "__main__":
    main()
