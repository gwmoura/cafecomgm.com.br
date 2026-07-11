.PHONY: server build deploy clean

server:
	hugo server -D

build:
	hugo

deploy: build
	hugo deploy

clean:
	rm -rf public resources/_gen
