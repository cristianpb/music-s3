SHELL := /bin/bash

export PYTHONIOENCODING=utf-8

dummy		    := $(shell touch .env)
include ./.env

encrypt:
	gpg --symmetric --quiet --batch --yes --cipher-algo AES256 --passphrase ${GPG_SECRET_PASSPHRASE} --quiet playlists.yaml

decrypt:
	./decrypt_secret.sh

tmpmusic:
	@echo "Creating tmp folder"
	mkdir -p tmpmusic

download: tmpmusic
	@echo "Download $(PLAYLIST) playlist"
	@PYTHONIOENCODING=utf-8 python3 download.py $(PLAYLIST)

clean:
	@echo "cleaning tmp music"
	rm -rf tmpmusic

rclone-install:
	curl -s -O https://downloads.rclone.org/rclone-current-linux-amd64.deb;\
		sudo dpkg -i rclone-current-linux-amd64.deb; \
		rm rclone-*-linux-amd64*;
