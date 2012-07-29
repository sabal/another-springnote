import glob
import hashlib
import logging
import os
import subprocess
import urllib.request

BASE_DIR = os.path.dirname(__file__)  # XXX abspath
TARGET_DIR = os.path.join(BASE_DIR, 'build', 'Another Springnote')
# GNU cp doesn't recognize forward slash
BASE_DIR_ = BASE_DIR.replace('\\', '/')
TARGET_DIR_ = TARGET_DIR.replace('\\', '/')


def main():
    logging.basicConfig(level=logging.DEBUG)

    file_name = os.path.join(TARGET_DIR, 'stop_server.bat')
    if os.access(file_name, os.F_OK):
        logging.info('Stopping (possibly running) server...')
        subprocess.call(file_name, shell=True)

    if os.access(TARGET_DIR, os.F_OK):
        cmd(['rm', '-rf', TARGET_DIR])
    os.makedirs(TARGET_DIR, exist_ok=True)

    logging.info('Exporting git repositories...')

    # WNMP
    git_pipe = subprocess.Popen(['git',
            '--git-dir={}'.format(os.path.join(BASE_DIR, 'wnmp', '.git')),
            '--work-tree={}'.format(os.path.join(BASE_DIR, 'wnmp')),
            'archive', 'sabal'],
        stdout=subprocess.PIPE)
    subprocess.Popen(['tar', '-x', '-C', TARGET_DIR],
        stdin=git_pipe.stdout).communicate()

    # DokuWiki
    os.makedirs(os.path.join(TARGET_DIR, 'nginx', 'www'), exist_ok=True)
    git_pipe = subprocess.Popen(['git',
            '--git-dir={}'.format(os.path.join(BASE_DIR, 'dokuwiki', '.git')),
            '--work-tree={}'.format(os.path.join(BASE_DIR, 'dokuwiki')),
            'archive', 'sabal'],
        stdout=subprocess.PIPE)
    subprocess.Popen(['tar', '-x', '-C', '{}/nginx/www'.format(TARGET_DIR_)],
        stdin=git_pipe.stdout).communicate()

    # FCK
    git_pipe = subprocess.Popen(['git',
            '--git-dir={}'.format(os.path.join(BASE_DIR, 'fckgLite', '.git')),
            '--work-tree={}'.format(os.path.join(BASE_DIR, 'fckgLite')),
            'archive', 'sabal'],
        stdout=subprocess.PIPE)
    subprocess.Popen(['tar', '-x',
            '-C', '{}/nginx/www/lib/plugins'.format(TARGET_DIR_)],
        stdin=git_pipe.stdout).communicate()

    # PHP
    wget('http://windows.php.net/downloads/releases/'
            'php-5.4.5-Win32-VC9-x86.zip',
        sha1='028eb12e09fe011e20097c82064d6c550bf896c4')
    os.makedirs(os.path.join('tmp', 'php'), exist_ok=True)
    cmd(['unzip', '-oq', '-d', os.path.join('tmp', 'php'),
        'php-5.4.5-Win32-VC9-x86.zip'])
    cmd(['bash', '-c', "cp -r tmp/php/* '{}/php/'".format(TARGET_DIR_)])

    # nginx
    wget('http://nginx.org/download/nginx-1.2.2.zip',
        sha1='0a5dfbb766bfefa238207db25d7b64b69aa37908')
    os.makedirs(os.path.join('tmp', 'nginx'), exist_ok=True)
    cmd(['unzip', '-oq', '-d', os.path.join('tmp', 'nginx'),
        'nginx-1.2.2.zip'])
    cmd(['bash', '-c',
        "cp -r tmp/nginx/nginx-1.2.2/* '{}/nginx/'".format(TARGET_DIR_)])

    cmd(['cp', '{}/example.nginx.conf'.format(TARGET_DIR_),
        '{}/nginx/conf/nginx.conf'.format(TARGET_DIR_)])
    for file_name in ['acl.auth.php', 'local.php', 'users.auth.php']:
        cmd(['cp',
            os.path.join(BASE_DIR_, 'build', file_name).replace('\\', '/'),
            # XXX
            '{}/nginx/www/conf'.format(TARGET_DIR_)])

    for pattern in [
            'example.nginx.conf',
            'readme.txt',
            'nginx/www/_*',
            'www/',]:
        for file_path in glob.glob(os.path.join(TARGET_DIR,
                os.path.normpath(pattern))):
            cmd(['rm', '-rf', file_path.replace('\\', '/')])

    # TODO: zip


def cmd(tokens):
    logging.info(' '.join(tokens))
    subprocess.call(tokens)


def wget(url, sha1):
    _, _, file_name = url.rpartition('/')
    target_path = os.path.join(BASE_DIR, file_name)
    if os.access(target_path, os.F_OK):
        if hashlib.sha1(open(target_path, 'rb').read()).hexdigest() == sha1:
            return
    logging.info('Downloading {}'.format(url))
    req = urllib.request.urlopen(url)
    open(target_path, 'wb+').write(req.read())


main()
