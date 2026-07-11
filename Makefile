.PHONY: server build deploy clean

server:
	hugo server -D

build:
	hugo

clean:
	rm -rf public resources/_gen
