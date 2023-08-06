import onepasswd
from onepasswd.onepasswd import PasswdGen
from onepasswd.config import Config
from onepasswd import crypto
from onepasswd.onepasswd import DB
from onepasswd.onepasswd import GitDB
from onepasswd.tools import jmerge, jdiff
from onepasswd import ltlog
import pyperclip
from pathlib import Path
import os
import json
import shlex
import time
import tempfile
import click
import logging

log = ltlog.getLogger('onepasswd.client')

DEF_CONFIG_PATH = os.path.join(Path.home(), ".onepasswd", "onepasswd.json")
DEF_DB_PATH = os.path.join(Path.home(), ".onepasswd", "db")
DEF_BACKUP_PATH = os.path.join(Path.home(), ".onepasswd", "backup")


@click.group()
@click.option('-d', '--debug', 'debug', default='INFO', help='log level')
@click.option('-c', '--config', 'config', default=DEF_CONFIG_PATH, help='config path')
@click.option('-p', '--print_passwd', 'print_passwd', is_flag=True,
              help='print password (do not copy from clipboard)')
@click.pass_context
def cli(ctx: click.Context, debug, config, print_passwd):
    ctx.ensure_object(dict)
    logging.getLogger().setLevel(debug)
    ctx.obj['config_path'] = config
    if os.path.exists(config):
        ctx.obj['config'] = Config(config)
    if not is_clipboard_available():
        log.warn('clipboard is not available')
    ctx.obj['print_passwd'] = print_passwd


@cli.command('version')
@click.pass_context
def version(ctx: click.Context):
    click.echo(onepasswd.get_version())


@cli.command('init')
@click.option('-r', '--repo', 'repo', help='github repo (owner/name), used to upload database to github')
@click.option('-t', '--token', 'token', help='github token ("github_xxx")')
@click.option('-t', '--encrypted-token', 'encrypted_token', help='github token (encrypted)')
@click.option('--input-token', 'input_token', is_flag=True, help='get token from stdin')
@click.option('--db', 'db', default=DEF_DB_PATH, show_default=True, help='local database path')
@click.option('--backup', 'backup', default=DEF_BACKUP_PATH, show_default=True, help='database backup path')
@click.pass_context
def init(ctx: click.Context, repo, token, db, backup, input_token, encrypted_token):
    cfg_path = from_ctx(ctx, 'config_path')
    if os.path.exists(cfg_path):
        click.echo(f'already initialized. if you want to re-init, please remove {cfg_path}')
        exit(0)
    prepare_dir(cfg_path)
    prepare_dir(db)
    prepare_dir(backup)
    cfg = {
        'db': db,
        'backup': backup
    }
    # init auth info
    passwd = get_passwd(ctx, promt='master password', confirm=True,
                        from_clipboard=False, key='passwd')
    auth = crypto.generate_auth_info(passwd)
    cfg['auth_info'] = auth
    if repo and (token or input_token or encrypted_token):
        # init github
        cfg['repo'] = repo
        if input_token:
            token = get_passwd(ctx, promt='token')
        if not encrypted_token:
            encrypted_token = crypto.encrypt_passwd(token, passwd)
        cfg['token'] = encrypted_token
        # sync from github
        if click.confirm('sync from github'):
            # todo: sync
            ctx.obj['config'] = cfg
            ctx.invoke(sync)
    else:
        click.echo('github sync not enabled')
    # write config
    with open(cfg_path, "w") as fp:
        json.dump(cfg, fp, indent=2)
    click.echo("init finish!")


@cli.command('sync')
@click.pass_context
def sync(ctx: click.Context):
    cfg = from_ctx(ctx, 'config')
    assert cfg is not None
    passwd = get_passwd(ctx, promt='master password', from_clipboard=False, key='passwd')
    token = crypto.decrypt_passwd(cfg['token'], passwd)
    git = GitDB(cfg['repo'], token)
    remote_sha = git.get_remote_hash('db')
    if git.hashfile(cfg['db']) == remote_sha:
        click.echo("local db is already updated")
        return
    # download and merge
    remote_db = git.pull('db')
    log.debug('get remote db +++ ' + str(remote_db))
    with tempfile.TemporaryDirectory(prefix='onepasswd') as dir:
        tmp_file = os.path.join(dir, 'db')
        with open(tmp_file, 'wb') as fp:
            fp.write(remote_db)
        click.echo("> diff >>>")
        jdiff.diff(cfg['db'], tmp_file)
        click.echo("> merge >>>")
        jmerge.merge(cfg['db'], tmp_file)
    # push
    git.push(cfg['db'], 'db', remote_sha)
    click.echo("sync success")


@cli.command('get')
@click.argument('keywords', nargs=-1)
@click.pass_context
def get(ctx: click.Context, keywords: tuple):
    if len(keywords) == 0:
        keywords = ('',)
    cfg = from_ctx(ctx, 'config')
    db = get_db(ctx)

    def process_passwd(passwd_enc):
        passwd = get_passwd(ctx, promt='master password', from_clipboard=False, key='passwd')
        if not crypto.auth(cfg['auth_info'], passwd):
            click.echo("password wrong")
            exit(1)
        give_passwd(ctx, crypto.decrypt_passwd(passwd_enc, passwd))

    # accurate match
    if keywords in db:
        item = db.get_item(keywords)
        click.echo(passwd_item_str(item))
        process_passwd(item['passwd'])
        return

    for v in db.find(keywords):
        if click.confirm(passwd_item_str(v)):
            process_passwd(v['passwd'])
            break


@cli.command('list')
@click.argument('keywords', nargs=-1)
@click.pass_context
def list(ctx: click.Context, keywords: tuple):
    if len(keywords) == 0:
        keywords = ('',)
    db = get_db(ctx)
    for v in db.find(keywords):
        click.echo(passwd_item_str(v))


@cli.command('add')
@click.argument('entries', nargs=-1)
@click.option('-l', '--len', 'length', default=12, show_default=True, help='password length')
@click.option('-s', '--strength', 'strength', default='aA0$', show_default=True,
              help='password strength')
@click.pass_context
def add(ctx: click.Context, entries: tuple, length, strength):
    d = {}

    def getpass():
        passwd = PasswdGen.generate(length, pre_process_strength(strength))
        d['passwd'] = passwd
        return passwd
    if save_passwd(ctx, entries, getpass):
        give_passwd(ctx, d['passwd'])
        if click.confirm('sync ?'):
            ctx.invoke(sync)


@cli.command('save')
@click.argument('entries', nargs=-1)
@click.pass_context
def save(ctx: click.Context, entries: tuple):
    def getpass():
        return get_passwd(ctx, promt='new password', confirm=True)
    if save_passwd(ctx, entries, getpass):
        if click.confirm('sync ?'):
            ctx.invoke(sync)


@cli.command('del')
@click.argument('keywords', nargs=-1)
@click.pass_context
def delete(ctx: click.Context, keywords: tuple):
    if len(keywords) == 0:
        keywords = ('',)
    db = get_db(ctx)
    for v in db.find(keywords):
        if click.confirm(passwd_item_str(v)):
            input = click.prompt('input entries to confirm delete')
            entries = shlex.split(input)
            if entries == v['entries']:
                del db[entries]
                click.echo(f'{passwd_item_str(v)} deleted')
                break


@cli.command('dec')
@click.argument('cipher')
@click.pass_context
def dec(ctx: click.Context, cipher):
    passwd = get_passwd(ctx, from_clipboard=False)
    text = crypto.decrypt_passwd(cipher, passwd)
    give_passwd(ctx, text)


@cli.command('enc')
@click.option('-d', '--data', 'data')
@click.pass_context
def enc(ctx: click.Context, data):
    passwd = get_passwd(ctx, from_clipboard=False)
    if not data:
        data = get_passwd(ctx, promt='content to encrypt')
    cipher = crypto.encrypt_passwd(data, passwd)
    give_passwd(ctx, cipher)


@cli.command('web')
@click.option('-h', '--host', 'host', default='0.0.0.0')
@click.option('-p', '--port', 'port', default=10066)
@click.option('-d', '--debug', 'debug', is_flag=True, default=False)
@click.pass_context
def web(ctx, host, port, debug):
    try:
        from onepasswd import web
    except ImportError:
        click.echo('you must install flask if you want to use onepasswd web')
        click.echo('try: pip install flask')
        exit(1)
    web.init(from_ctx(ctx, 'config'))
    web.app.run(host=host, port=port, debug=debug)


def save_passwd(ctx, entries, getpass):
    assert len(entries) >= 1
    db = get_db(ctx)
    if entries in db:
        item = db.get_item(entries)
        if not click.confirm(
                f'{passwd_item_str(item)} already in database, update ?'):
            return False
        cfg = from_ctx(ctx, 'config')
        db.backup(cfg['backup'])
    passwd = get_passwd(ctx, promt='master password', from_clipboard=False, key='passwd')
    passwd_dec = getpass()
    passwd_enc = crypto.encrypt_passwd(passwd_dec, passwd)
    db[entries] = passwd_enc
    return True


def pre_process_strength(s):
    strength = set()
    for x in s:
        for i, t in enumerate(PasswdGen.passwd_table):
            if x in t:
                strength.add(i)
                break
    return strength


def passwd_item_str(item):
    t = time.ctime(float(item['time']))
    entries = ' '.join(['"' + x.replace('"', '\\"') + '"' for x in item['entries']])
    return f'[{t}] {entries}'


def get_db(ctx: click.Context):
    config = from_ctx(ctx, 'config')
    return DB(config['db'])


def from_ctx(ctx: click.Context, name, default=None):
    return ctx.obj.get(name, default)


def check_config(cfg: dict):
    keys = ['db', 'backup']
    for key in keys:
        if key not in cfg:
            return False
    return True


def prepare_dir(filepath):
    dir = os.path.dirname(filepath)
    if not os.path.exists(dir):
        os.makedirs(dir)


def get_passwd(ctx: click.Context = None, promt="password", from_clipboard=None, confirm=False, key=None):
    def ret_password(passwd):
        if ctx and key and key not in ctx.obj:
            ctx.obj[key] = passwd
        return passwd
    if ctx and key and key in ctx.obj:
        return from_ctx(ctx, key)
    if (from_clipboard is None and click.confirm(f'[{promt}] use input from clipboard ?')) \
            or from_clipboard:
        passwd = pyperclip.paste().strip()
        if len(passwd) == 0:
            click.echo('your clipboard contains northing')
        else:
            return ret_password(passwd)
    passwd = click.prompt(f'please input {promt}', hide_input=True)
    passwd = passwd.strip()
    if confirm:
        confirm = click.prompt(f'confirm {promt}', hide_input=True)
        confirm = confirm.strip()
        if confirm != passwd:
            return get_passwd(ctx, promt=promt, from_clipboard=False, confirm=True, key=key)
    return ret_password(passwd)


def give_passwd(ctx: click.Context, passwd, no_echo=False):
    if not from_ctx(ctx, 'print_passwd') and is_clipboard_available():
        pyperclip.copy(passwd)
    else:
        if not no_echo:
            click.echo(passwd)


def is_clipboard_available():
    try:
        pyperclip.paste()
        return True
    except Exception as e:
        log.error(e)
        return False


def main():
    cli()


if __name__ == "__main__":
    main()
