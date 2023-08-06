#!/usr/bin/python3

import json
import random
import time
import os
import socket
from onepasswd import ltlog
from hashlib import sha256, sha1
from github import Github

log = ltlog.getLogger('onepasswd.onepasswd')

g_req_kwarg = {
    # 'verify': False
}


class GitDB(object):
    def __init__(self, repo, token):
        super().__init__()
        self.github = Github(token)
        self.token = token
        log.debug(f'get_repo {repo}')
        self.repo = self.github.get_repo(repo)

    def _gen_commit_msg(self):
        localname = socket.gethostname()
        create_time = time.ctime()
        return "[{time:}] @ {name}".format(time=create_time, name=localname)

    def pull(self, path):
        file = self.repo.get_contents(path)
        return file.decoded_content

    def push(self, local_path, remote_path, sha=None):
        with open(local_path) as fp:
            buf = fp.read()
        msg = self._gen_commit_msg()
        if sha:
            self.repo.update_file(remote_path, msg, buf, sha)
        else:
            self.repo.create_file(remote_path, msg, buf)

    def get_remote_hash(self, path):
        dir, name = os.path.split(path)
        files = self.repo.get_dir_contents(dir)
        sha = None
        for f in files:
            if f.name == name:
                sha = f.sha
        return sha

    @staticmethod
    def hashfile(file):
        res = None
        with open(file, "rb") as fp:
            length = fp.seek(0, os.SEEK_END)
            fp.seek(0, os.SEEK_SET)
            header = b'blob ' + str(length).encode() + b'\x00'
            res = sha1(header + fp.read()).hexdigest().lower()
        return res


class PasswdGen(object):
    passwd_table = ["abcdefghijklmnopqrstuvwxyz",
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    "0123456789",
                    "@_-~,.#$"]

    @staticmethod
    def check_strength(passwd, strength):
        vis = set()
        for x in passwd:
            for i, t in enumerate(PasswdGen.passwd_table):
                if x in t:
                    vis.add(i)
        if vis != strength:
            return False
        return True

    @staticmethod
    def generate(length=12, strength=set(range(0, len(passwd_table)))):
        table = ''.join([PasswdGen.passwd_table[i] for i in strength])
        passwd = ''
        for i in range(length):
            passwd += random.choice(table)

        if PasswdGen.check_strength(passwd, strength):
            return passwd
        else:
            return PasswdGen.generate(length, strength)


class DB(dict):
    def __init__(self, path, default={}):
        self.path = path
        self.db = default
        self._load_from_disk()

    def __getitem__(self, entries):
        key = DB.cal_key(entries)
        return self.db[key]['passwd']

    @staticmethod
    def cal_key(entries):
        return sha256(json.dumps(entries).replace('\n', '').replace('\t', '').encode('utf-8')).hexdigest()

    def __setitem__(self, entries, val):
        key = DB.cal_key(entries)
        if key in self.db and self.db[key]['passwd'] == val:
            return
        self.db[key] = {'entries': entries,
                        'passwd': val, 'time': str(time.time())}
        self._write_to_disk()

    def __delitem__(self, entries):
        key = DB.cal_key(entries)
        if key not in self.db:
            return
        self.db.__delitem__(key)
        self._write_to_disk()

    def __contains__(self, entries):
        return self.db.__contains__(DB.cal_key(entries))

    def _write_to_disk(self, path=None):
        path = path if path else self.path
        with open(path, 'w') as fp:
            json.dump(self.db, fp, indent=2)

    def _load_from_disk(self, path=None, default={}):
        path = path if path else self.path
        if not os.path.exists(path):
            self._write_to_disk(path)
        with open(path) as fp:
            self.db = json.load(fp)

    def backup(self, backup_path):
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        bck_file = os.path.join(backup_path, str(time.time()) + '.db')
        self._write_to_disk(bck_file)

    def rollback(self, timestamp, backup_path):
        timestamp = str(timestamp)
        bck_file = os.path.join(backup_path, timestamp + '.db')
        if not os.path.exists(bck_file):
            print("[Abort] '{}' not found".format(bck_file))
            return
        # do backup
        self.backup()
        self._load_from_disk(bck_file)

    def getkeys(self):
        return [x['entries'] for k, x in self.db.items()]

    def _find(self, keyword):
        s = set()
        for h, v in self.db.items():
            for e in v['entries']:
                if keyword in e:
                    s.add(h)
                    break
        return s

    def find(self, keywords):
        r = []
        for key in keywords:
            s = self._find(key)
            if len(r) == 0:
                r = s
            else:
                r.intersection_update(s)
            if len(r) == 0:
                return []
        return [self.db[x] for x in r]

    def get_item(self, entries):
        key = DB.cal_key(entries)
        return self.db[key]