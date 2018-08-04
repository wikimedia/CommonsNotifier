.PHONY: test lint
.DEFAULT: all

all: test lint

test:
	python3 -m unittest discover

lint:
	pycodestyle .
