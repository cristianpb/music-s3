#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import re
import sys
import glob
import shutil
import argparse
import subprocess
import yaml
from yaml.loader import SafeLoader

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-c", "--category",  nargs='?', type=str, default=None)
parser.add_argument("-u", "--url", nargs="?", type=str, default=None)
parser.add_argument("-un", "--url-name", nargs="?", type=str, default=None)
args = parser.parse_args()
config = vars(args)

CWD = os.getcwd()
DEST_FOLDER = os.path.join(CWD, 'output')
if not os.path.exists(DEST_FOLDER):
    os.makedirs(DEST_FOLDER)

if not os.path.exists(os.path.join(DEST_FOLDER, 'playlists')):
    os.makedirs(os.path.join(DEST_FOLDER, 'playlists'))

if not os.path.exists(os.path.join(DEST_FOLDER, 'music')):
    os.makedirs(os.path.join(DEST_FOLDER, 'music'))

print("Conf", config)


def download(key, url):
    cmd=f"docker run --rm -v {CWD}/tmpmusic:/music spotdl/spotify-downloader download {url.strip()} --m3u {key}.m3u8 --dont-filter-results --cookie-file cookies.txt"
    p=subprocess.Popen(cmd.split(" "),
                             stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        print(f">>> {line.rstrip().decode('utf-8')}")

    playlist_folder = key
    playlist_file = playlist_folder + ".m3u8"

    if not os.path.exists(playlist_folder):
        os.makedirs(playlist_folder)
    for my_file in glob.glob(r'tmpmusic/*.mp3'):
        shutil.move(my_file, playlist_folder)

    if os.path.exists(os.path.join("tmpmusic", playlist_folder + ".m3u8")):
        # if m3u created by spotdl
        with open(os.path.join("tmpmusic", playlist_folder + ".m3u8"),'r', encoding="utf-8") as fnr:
            text = fnr.readlines()

        text = "".join(['../music/' + playlist_folder + '/' + line.strip() + '\n' for line in text])

        with open(playlist_file,'w', encoding="utf-8") as fnw:
            fnw.write(text)
    else:
        # create m3u from mp3 files
        music_files = [os.path.basename(f) for f in glob.glob(f"{playlist_folder}/*.mp3")]
        text = "".join(['../music/' + playlist_folder + '/' + line.strip().encode("utf-8", 'replace').decode() + '\n' for line in music_files])

        with open(playlist_file,'w', encoding="utf-8") as fnw:
            fnw.write(text)

    # TO DEST
    shutil.move(os.path.join(CWD, playlist_file), DEST_FOLDER + '/playlists/' + playlist_file)
    if os.path.exists(DEST_FOLDER + '/music/' + playlist_folder):
        shutil.rmtree(DEST_FOLDER + '/music/' + playlist_folder)
    shutil.move(os.path.join(CWD, playlist_folder), DEST_FOLDER + '/music/')

    print();

if config['category'] is not None:
    with open('playlists.yaml', 'r') as f:
        data = list(yaml.load_all(f, Loader=SafeLoader))
        category = data[0][config['category']]
        for key, url in category.items():
            download(key,url)
elif config['url_name'] is not None and config['url'] is not None:
    download(config['url_name'] ,config['url'])
