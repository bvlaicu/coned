.PHONY: docs release clean build

clean:
	rm -rf coned_env

build:
	virtualenv -p /usr/local/bin/python3 coned_env && source coned_env/bin/activate && \
		pip install -r requirements.txt

test: clean build
		source coned_env/bin/activate && \
		coverage run --source=coned setup.py test && \
		coverage html && \
		coverage report

release: test
	vim coned/__init__.py
