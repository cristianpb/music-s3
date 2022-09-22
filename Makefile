SHELL := /bin/bash

export PYTHONIOENCODING=utf-8

encrypt:
	gpg --symmetric --cipher-algo AES256 playlists.yaml

tmpmusic:
	@echo "Creating tmp folder"
	mkdir -p tmpmusic

main: tmpmusic
	@echo "Download main playlist"
	@PYTHONIOENCODING=utf-8 python3 download.py main

clean:
	@echo "cleaning tmp music"
	rm -rf tmpmusic

rclone-install:
	curl -s -O https://downloads.rclone.org/rclone-current-linux-amd64.deb;\
		sudo dpkg -i rclone-current-linux-amd64.deb; \
		rm rclone-*-linux-amd64*;
