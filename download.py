#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import re
import sys
import glob
import shutil
import subprocess
import yaml
from yaml.loader import SafeLoader

CWD = os.getcwd()
DEST_FOLDER = os.path.join(CWD, 'output')
if not os.path.exists(DEST_FOLDER):
    os.makedirs(DEST_FOLDER)

if not os.path.exists(os.path.join(DEST_FOLDER, 'playlists')):
    os.makedirs(os.path.join(DEST_FOLDER, 'playlists'))

if not os.path.exists(os.path.join(DEST_FOLDER, 'music')):
    os.makedirs(os.path.join(DEST_FOLDER, 'music'))

with open('playlists.yaml', 'r') as f:
    data = list(yaml.load_all(f, Loader=SafeLoader))
    category = data[0][sys.argv[1]]
    for idx, (key, url) in enumerate(category.items()):
        print(f"{key} -> {url.strip()}")
        cmd="docker run --rm -v ${PWD}/tmpmusic:/music  spotdl/spotify-downloader download "f" {url.strip()} --m3u {key}.m3u8"
        process=subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        output = process.stdout.read().decode('utf-8')
        print("OUT: "+output)

        playlist_folder = key
        playlist_file = playlist_folder + ".m3u8"

        if not os.path.exists(playlist_folder):
            os.makedirs(playlist_folder)
        for my_file in glob.glob(r'tmpmusic/*.mp3'):
            shutil.move(my_file, playlist_folder)

        t = [f for f in glob.glob("tmpmusic/*.m3u8")]
        if len(t) > 0:
            # if m3u created by spotdl
            with open(t[idx],'r', encoding="utf-8") as fnr:
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
