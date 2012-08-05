#!/usr/bin/env python3
# Tested on:
#  - Linux
#  - Git Bash for Windows
import glob
import hashlib
import logging
import os
import subprocess
import sys
import urllib.request

def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError:
        pass


os.chdir(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = ''  #os.path.dirname(__file__)
TARGET_DIR = os.path.join(BASE_DIR, 'build_{}'.format(sys.platform),
    'Another Springnote')
# GNU cp for Windows doesn't recognize backward slash
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
    makedirs(TARGET_DIR, exist_ok=True)

    if sys.platform in ['win32', 'win64', 'cygwin']:
        deploy_wnmp()
        deploy_dokuwiki('nginx/www')
    else:
        deploy_dokuwiki('')

    for pattern in [
            'example.nginx.conf',
            'readme.txt',]:
        for file_path in glob.glob(os.path.join(TARGET_DIR,
                os.path.normpath(pattern))):
            cmd(['rm', '-rf', file_path.replace('\\', '/')])

    # TODO: zip


def deploy_wnmp():
    git_pipe = subprocess.Popen(['git',
            '--git-dir={}'.format(os.path.join(BASE_DIR, 'wnmp', '.git')),
            '--work-tree={}'.format(os.path.join(BASE_DIR, 'wnmp')),
            'archive', 'sabal'],
        stdout=subprocess.PIPE)
    subprocess.Popen(['tar', '-x', '-C', TARGET_DIR],
        stdin=git_pipe.stdout).communicate()

    # PHP
    wget('http://windows.php.net/downloads/releases/'
            'php-5.4.5-Win32-VC9-x86.zip',
        sha1='028eb12e09fe011e20097c82064d6c550bf896c4')
    makedirs(os.path.join('tmp', 'php'), exist_ok=True)
    cmd(['unzip', '-oq', '-d', os.path.join('tmp', 'php'),
        'php-5.4.5-Win32-VC9-x86.zip'])
    cmd(['bash', '-c', "cp -r tmp/php/* '{}/php/'".format(TARGET_DIR_)])

    # nginx
    wget('http://nginx.org/download/nginx-1.2.2.zip',
        sha1='0a5dfbb766bfefa238207db25d7b64b69aa37908')
    makedirs(os.path.join('tmp', 'nginx'), exist_ok=True)
    cmd(['unzip', '-oq', '-d', os.path.join('tmp', 'nginx'),
        'nginx-1.2.2.zip'])
    cmd(['bash', '-c',
        "cp -r tmp/nginx/nginx-1.2.2/* '{}/nginx/'".format(TARGET_DIR_)])

    cmd(['cp', '{}/example.nginx.conf'.format(TARGET_DIR_),
        '{}/nginx/conf/nginx.conf'.format(TARGET_DIR_)])


def deploy_dokuwiki(rel_path):
    # DokuWiki
    if not rel_path:
        path = TARGET_DIR
    else:
        path = os.path.normpath(os.path.join(TARGET_DIR, rel_path))
    path_ = path.replace('\\', '/')
    makedirs(path, exist_ok=True)
    git_pipe = subprocess.Popen(['git',
            '--git-dir={}'.format(os.path.join(BASE_DIR, 'dokuwiki', '.git')),
            '--work-tree={}'.format(os.path.join(BASE_DIR, 'dokuwiki')),
            'archive', 'sabal'],
        stdout=subprocess.PIPE)
    subprocess.Popen(['tar', '-x', '-C', path_],
        stdin=git_pipe.stdout).communicate()

    # FCK
    git_pipe = subprocess.Popen(['git',
            '--git-dir={}'.format(os.path.join(BASE_DIR, 'fckgLite', '.git')),
            '--work-tree={}'.format(os.path.join(BASE_DIR, 'fckgLite')),
            'archive', 'sabal'],
        stdout=subprocess.PIPE)
    subprocess.Popen(['tar', '-x', '-C', '{}/lib/plugins'.format(path_)],
        stdin=git_pipe.stdout).communicate()

    # conf
    for file_name in ['acl.auth.php', 'local.php', 'users.auth.php']:
        cmd(['cp',
            os.path.join(BASE_DIR_, 'build', file_name).replace('\\', '/'),
            # XXX
            '{}/conf'.format(path_)])

    # cleanup
    for pattern in ['{}/_*'.format(rel_path),]:
        for file_path in glob.glob(os.path.join(TARGET_DIR,
                os.path.normpath(pattern))):
            cmd(['rm', '-rf', file_path.replace('\\', '/')])


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
