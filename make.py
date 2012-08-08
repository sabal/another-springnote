#!/usr/bin/env python3
# Tested on:
#  - Linux
#  - cmd in Windows (with git accessible in PATH)
import glob
import hashlib
import io
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError:
        pass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = sys.platform in ['win32', 'win64', 'cygwin']
TARGET_DIR = os.path.join(BASE_DIR, 'build_{}'.format(sys.platform),
    'Another Springnote' if IS_WINDOWS else 'another-springnote')


def main():
    logging.basicConfig(level=logging.DEBUG)

    file_name = os.path.join(TARGET_DIR, 'stop_server.bat')
    if os.access(file_name, os.F_OK):
        logging.info('Trying to stop possibly running server...')
        subprocess.call(file_name, stderr=subprocess.PIPE, shell=True)

    if os.access(TARGET_DIR, os.F_OK):
        shutil.rmtree(TARGET_DIR)
    makedirs(TARGET_DIR, exist_ok=True)

    if IS_WINDOWS:
        deploy_wnmp()
        deploy_dokuwiki('nginx/www')
    else:
        deploy_dokuwiki()

    for pattern in [
            'example.nginx.conf',
            'readme.txt',]:
        for path in glob.glob(os.path.join(TARGET_DIR,
                os.path.normpath(pattern))):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)

    # TODO: zip


def deploy_wnmp():
    os.chdir(os.path.join(BASE_DIR, 'wnmp'))
    tar, _ = subprocess.Popen(['git', 'archive', 'sabal'],
        stdout=subprocess.PIPE, shell=IS_WINDOWS).communicate()
    ar = tarfile.open(fileobj=io.BytesIO(tar))
    ar.extractall(TARGET_DIR)

    # PHP
    wget('http://windows.php.net/downloads/releases/'
            'php-5.4.5-Win32-VC9-x86.zip',
        sha1='028eb12e09fe011e20097c82064d6c550bf896c4')
    logging.info('Extracting PHP...')
    path = os.path.join(BASE_DIR, '_tmp', 'php')
    makedirs(path, exist_ok=True)
    ar = zipfile.ZipFile(
        os.path.join(BASE_DIR, 'php-5.4.5-Win32-VC9-x86.zip'))
    ar.extractall(path)
    shutil.rmtree(os.path.join(TARGET_DIR, 'php'))
    shutil.copytree(path, os.path.join(TARGET_DIR, 'php'))

    # nginx
    wget('http://nginx.org/download/nginx-1.2.2.zip',
        sha1='0a5dfbb766bfefa238207db25d7b64b69aa37908')
    logging.info('Extracting nginx...')
    path = os.path.join(BASE_DIR, '_tmp')
    makedirs(path, exist_ok=True)
    ar = zipfile.ZipFile(
        os.path.join(BASE_DIR, 'nginx-1.2.2.zip'))
    ar.extractall(path)
    shutil.rmtree(os.path.join(TARGET_DIR, 'nginx'))
    shutil.copytree(os.path.join(path, 'nginx-1.2.2'),
        os.path.join(TARGET_DIR, 'nginx'))
    shutil.move(os.path.join(TARGET_DIR, 'example.nginx.conf'),
        os.path.join(TARGET_DIR, 'nginx', 'conf', 'nginx.conf'))

    # cleanup
    shutil.rmtree(os.path.join(BASE_DIR, '_tmp'))


def deploy_dokuwiki(rel_path=None):
    if not rel_path:
        rel_path = '.'
    path = os.path.normpath(os.path.join(TARGET_DIR, rel_path))

    # DokuWiki
    logging.info('Extracting DokuWiki...')
    makedirs(path, exist_ok=True)
    os.chdir(os.path.join(BASE_DIR, 'wiki', 'dokuwiki'))
    tar, _ = subprocess.Popen(['git', 'archive', 'sabal'],
        stdout=subprocess.PIPE, shell=IS_WINDOWS).communicate()
    ar = tarfile.open(fileobj=io.BytesIO(tar))
    ar.extractall(path)

    # FCK
    logging.info('Extracting fckgLite plugin...')
    os.chdir(os.path.join(BASE_DIR, 'wiki', 'fckgLite'))
    tar, _ = subprocess.Popen(['git', 'archive', 'sabal'],
        stdout=subprocess.PIPE, shell=IS_WINDOWS).communicate()
    ar = tarfile.open(fileobj=io.BytesIO(tar))
    ar.extractall(os.path.join(path, 'lib', 'plugins'))

    # conf
    for file_name in ['acl.auth.php', 'local.php', 'users.auth.php']:
        shutil.copy(
            os.path.join(BASE_DIR, 'wiki', 'conf', file_name),
            '{}/conf'.format(path))

    # cleanup
    for pattern in ['{}/_*'.format(rel_path),]:
        for file_path in glob.glob(os.path.join(TARGET_DIR,
                os.path.normpath(pattern))):
            shutil.rmtree(file_path)


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
    req = urlopen(url)
    open(target_path, 'wb+').write(req.read())


main()
