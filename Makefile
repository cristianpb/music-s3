SHELL := /bin/bash

export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1

dummy		    := $(shell touch .env)
include ./.env

encrypt:
	gpg --symmetric --quiet --batch --yes --cipher-algo AES256 --passphrase ${GPG_SECRET_PASSPHRASE} --quiet playlists.yaml

decrypt:
	./decrypt_secret.sh

tmpmusic:
	@echo "Creating tmpmusic folder"
	@mkdir -p tmpmusic

download: tmpmusic
	@if [ ! -z "${PLAYLIST}" ];then\
		echo "Download $(PLAYLIST) playlist";\
		PYTHONIOENCODING=utf-8 python3 download.py -c $(PLAYLIST);\
	fi;
	@if [ ! -z "${URL_NAME}" -o ! -z "${URL}" ];then\
		echo "Download $(URL_NAME) ($(URL))";\
		PYTHONIOENCODING=utf-8 python3 download.py -u $(URL) -un $(URL_NAME);\
	fi;

clean:
	@echo "Cleaning tmpmusic and output"
	@rm -rf tmpmusic output

rclone-install:
	curl -s -O https://downloads.rclone.org/rclone-current-linux-amd64.deb;\
		sudo dpkg -i rclone-current-linux-amd64.deb; \
		rm rclone-*-linux-amd64*;

rclone-delete:
	@rclone delete --rmdirs s3:$$BUCKET/

rclone-purge:
	@rclone purge s3:$$BUCKET

rclone-push:
	@rclone sync output/ s3:$$BUCKET/

rclone-ls:
	@rclone ls s3:$$BUCKET/
