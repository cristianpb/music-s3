SHELL := /bin/bash

export PYTHONIOENCODING=utf-8

tmpmusic:
	@echo "Creating tmp folder"
	mkdir -p tmpmusic

main: tmpmusic
	@echo "Download main playlist"
	@PYTHONIOENCODING=utf-8 python3 download.py main

clean:
	@echo "cleaning tmp music"
	rm -rf tmpmusic
