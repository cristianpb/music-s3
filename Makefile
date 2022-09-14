SHELL := /bin/bash

export PYTHONIOENCODING=utf-8

tmpmusic:
	@echo "Creating tmp folder"
	mkdir -p tmpmusic

copy-download: tmpmusic
	@echo "Copy download.py"
	cp download.py tmpmusic

main: copy-download
	@echo "Download main playlist"
	@cp playlists.yaml tmpmusic/playlists.yaml && cd tmpmusic && PYTHONIOENCODING=utf-8 python3 download.py main

clean:
	@echo "cleaning tmp music"
	rm -rf tmpmusic
