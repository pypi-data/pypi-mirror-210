import os
from pathlib import Path
import json
from onepasswd import ltlog

log = ltlog.getLogger('onepasswd.config')


class Config(object):
    CONF_PATH = os.path.join(Path.home(), '.onepasswd', 'onepasswd.conf')

    def __init__(self, conf_path=CONF_PATH):
        self.conf_path = conf_path
        if not os.path.exists(conf_path):
            with open(conf_path, "w") as fp:
                fp.write("{}")
        fp = open(conf_path, "r")
        self.conf = json.load(fp)
        fp.close()

    def __getitem__(self, x):
        return self.conf[x]

    def __setitem__(self, k, v):
        if k not in self.conf or (k in self.conf and v != self.conf[k]):
            self.conf[k] = v
            self._write_to_disk()

    def _write_to_disk(self):
        with open(self.conf_path, "w") as fp:
            log.debug(self.conf)
            json.dump(self.conf, fp, indent=4)
