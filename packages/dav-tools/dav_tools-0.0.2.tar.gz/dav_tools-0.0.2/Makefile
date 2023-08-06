NAME=dav-tools

build:
	sudo rm -rf dist/
	python3 -m pip install build
	python3 -m build

upload-test: build
	python3 -m pip install --upgrade twine
	python3 -m twine upload --repository testpypi dist/*

upload: build
	python3 -m pip install --upgrade twine
	python3 -m twine upload --verbose dist/*

install-local: uninstall build
	sudo python3 -m pip install ./dist/*.whl

download: uninstall
	sudo python3 -m pip install $(NAME)

download-test: uninstall
	python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps $(NAME)

uninstall:
	sudo python3 -m pip uninstall -y $(NAME)
	