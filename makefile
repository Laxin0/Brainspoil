.PHONY: test
test: build/test.bs
	python3 src/main.py build/test.bs


