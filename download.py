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


def parse_commandargs():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-c", "--category", nargs="?", type=str, default=None)
    parser.add_argument("-o", "--output", nargs="?", type=str, default=None)
    parser.add_argument("-u", "--url", nargs="?", type=str, default=None)
    parser.add_argument("-un", "--url-name", nargs="?", type=str, default=None)
    args = parser.parse_args()
    config = vars(args)
    print("Conf", config)
    return config


def create_folders(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(os.path.join(output_folder, "playlists")):
        os.makedirs(os.path.join(output_folder, "playlists"))

    if not os.path.exists(os.path.join(output_folder, "music")):
        os.makedirs(os.path.join(output_folder, "music"))

    if not os.path.exists(os.path.join(output_folder, "sync_files")):
        os.makedirs(os.path.join(output_folder, "sync_files"))


def sync(key, url, output_folder):
    if os.path.exists(os.path.join(output_folder, "sync_files", key + ".spotdl")):
        cmd = (
            f"docker run --rm -v {output_folder}:/music spotdl/spotify-downloader "
            f"sync /music/sync_files/{key}.spotdl --output /music/music/{key} "
            f"--dont-filter-results"
        )
    else:
        cmd = (
            f"docker run --rm -v {output_folder}:/music spotdl/spotify-downloader "
            f"sync {url.strip()} --output /music/music/{key} --save-file /music/sync_files/{key}.spotdl "
            f"--dont-filter-results"
        )
        # --m3u /music/playlists/{key}.m3u8
    print(cmd)
    p = subprocess.Popen(
        cmd.split(" "), stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    for line in iter(p.stdout.readline, b""):
        print(f">>> {line.rstrip().decode('utf-8')}")

    # create m3u from mp3 files
    music_files = [
        os.path.basename(f) for f in glob.glob(f"{output_folder}/music/{key}/*.mp3")
    ]
    text = "".join(
        [
            "../music/"
            + key
            + "/"
            + line.strip().encode("utf-8", "replace").decode()
            + "\n"
            for line in music_files
        ]
    )
    with open(
        os.path.join(output_folder, "playlists", key + ".m3u8"), "w", encoding="utf-8"
    ) as fnw:
        fnw.write(text)


def download(key, url, DEST_FOLDER):
    CWD = os.getcwd()
    cmd = f"docker run --rm -v {CWD}/tmpmusic:/music spotdl/spotify-downloader download {url.strip()} --m3u {key}.m3u8 --dont-filter-results --audio youtube"
    print(cmd)
    p = subprocess.Popen(
        cmd.split(" "), stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    for line in iter(p.stdout.readline, b""):
        print(f">>> {line.rstrip().decode('utf-8')}")

    playlist_folder = key
    playlist_file = playlist_folder + ".m3u8"
    sync_file = playlist_folder + ".spotdl"

    if not os.path.exists(playlist_folder):
        os.makedirs(playlist_folder)
    for my_file in glob.glob(r"tmpmusic/*.mp3"):
        shutil.move(my_file, playlist_folder)

    if os.path.exists(os.path.join("tmpmusic", playlist_folder + ".m3u8")):
        # if m3u created by spotdl
        with open(
            os.path.join("tmpmusic", playlist_folder + ".m3u8"), "r", encoding="utf-8"
        ) as fnr:
            text = fnr.readlines()

        text = "".join(
            ["../music/" + playlist_folder + "/" + line.strip() + "\n" for line in text]
        )
    else:
        # create m3u from mp3 files
        music_files = [
            os.path.basename(f) for f in glob.glob(f"{playlist_folder}/*.mp3")
        ]
        text = "".join(
            [
                "../music/"
                + playlist_folder
                + "/"
                + line.strip().encode("utf-8", "replace").decode()
                + "\n"
                for line in music_files
            ]
        )

    with open(playlist_file, "w", encoding="utf-8") as fnw:
        fnw.write(text)

    # TO DEST
    shutil.move(
        os.path.join(CWD, playlist_file), DEST_FOLDER + "/playlists/" + playlist_file
    )
    shutil.move(os.path.join(CWD, sync_file), DEST_FOLDER + "/playlists/" + sync_file)
    if os.path.exists(DEST_FOLDER + "/music/" + playlist_folder):
        shutil.rmtree(DEST_FOLDER + "/music/" + playlist_folder)
    shutil.move(os.path.join(CWD, playlist_folder), DEST_FOLDER + "/music/")
    print()


if __name__ == "__main__":
    config = parse_commandargs()
    output_folder = (
        os.path.join(os.getcwd(), "output")
        if config["output"] is None
        else config["output"]
    )
    create_folders(output_folder)
    if config["category"] is not None:
        with open("playlists.yaml", "r") as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            category = data[0][config["category"]]
            for key, url in category.items():
                # download(key, url, DEST_FOLDER)
                sync(key, url, output_folder)
    elif config["url_name"] is not None and config["url"] is not None:
        # download(config['url_name'], config['url'], DEST_FOLDER)
        sync(config["url_name"], config["url"], output_folder)
