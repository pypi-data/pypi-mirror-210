from flask import Flask
from flask import render_template
from flask import request, make_response
from onepasswd import crypto
from onepasswd import ltlog
from onepasswd.onepasswd import DB
import datetime
import os
from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_v1_5

log = ltlog.getLogger('onepasswd.web')

_key = RSA.generate(2048)
_public_key = _key.public_key().export_key(format='PEM').decode()
_db_path = ''
_web_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask("onepasswd", template_folder=_web_path,
            static_folder=os.path.join(_web_path, 'static'))


def init(cfg):
    global _db_path
    _db_path = cfg['db']


@app.route("/")
def index():
    _db = DB(_db_path)
    items = []
    for entry in _db.getkeys():
        v = _db.get_item(entry)
        items.append(v)
    items = sorted(items, key=lambda v: float(v['time']), reverse=True)
    for i, v in enumerate(items):
        items[i] = {
            'time': str(datetime.datetime.fromtimestamp(int(float(v['time'])))),
            'entry': v['entries'],
            'data': v['passwd']
        }
    return render_template('index.html', items=items, pubkey=_public_key)


@app.post("/decrypt")
def decrypt():
    resp_500 = make_response()
    resp_500.status_code = 500

    data = request.json['data']
    passwd = request.json['passwd']
    log.debug(request.json)
    decryptor = PKCS1_v1_5.new(_key)
    passwd = decryptor.decrypt(base64.b64decode(passwd.encode()), None).decode()
    if not passwd:
        return resp_500
    try:
        text = crypto.decrypt_passwd(data, passwd)
    except:
        return resp_500
    return {'data': text}
