from Crypto.Cipher import AES
import binascii
from onepasswd import ltlog
from Crypto.PublicKey import ECC
from hashlib import sha256

log = ltlog.getLogger('onepasswd.crypto')


class WrongPasswordException(Exception):
    pass


def hash_key(key):
    return sha256(sha256(key.encode()).hexdigest().encode()).hexdigest()


def decrypt_passwd(passwd_enc, key):
    key = binascii.unhexlify(hash_key(key))
    passwd_enc = binascii.unhexlify(passwd_enc)
    cipher = AES.new(key, AES.MODE_ECB)
    passwd = cipher.decrypt(passwd_enc)
    return passwd.decode().strip()


def encrypt_passwd(passwd, key):
    key = binascii.unhexlify(hash_key(key))
    passwd = passwd.encode()
    passwd = passwd.ljust(16 * (((len(passwd) - 1) // 16) + 1), b' ')
    cipher = AES.new(key, AES.MODE_ECB)
    passwd_enc = cipher.encrypt(passwd)
    return binascii.hexlify(passwd_enc).decode()


def generate_auth_info(passwd):
    key = ECC.generate(curve='P-256')
    auth_info = {
        'pub': key.public_key().export_key(format='PEM'),
        'priv': key.export_key(passphrase=passwd,
                               protection='PBKDF2WithHMAC-SHA1AndAES128-CBC',
                               format='PEM')
    }
    log.debug(auth_info)
    return auth_info


def auth(auth_info, passwd):
    try:
        priv = ECC.import_key(auth_info['priv'], passphrase=passwd)
    except Exception:
        return False
    pub = ECC.import_key(auth_info['pub'])
    result = priv.public_key() == pub
    log.debug(result)
    return result
