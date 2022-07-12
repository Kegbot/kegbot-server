all: python

python:
	protoc -Iproto/ --python_out=python/kegbot/api proto/*proto

clean:
	rm -rf build dist
	find . -name "*.pyc" | xargs rm -f

.PHONY: clean all python


# vim: noet
