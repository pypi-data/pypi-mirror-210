.DEFAULT_GOAL := all
sources = vector_pipelines tests

.PHONY: install
install: 
	pip install -e .[dev,grpc,sentence-transformers]

.PHONY: format
format:
	black --preview $(sources)
	ruff --fix $(sources)

.PHONY: lint
lint:
	black --preview --check $(sources)
	ruff $(sources)

.PHONY: mypy
mypy:
	mypy $(sources)

.PHONY: test
test:
	coverage run -m pytest

.PHONY: compile-proto
compile-proto:
	python -m grpc_tools.protoc -I vector_pipelines/grpc=vector_pipelines/proto --python_out=. --pyi_out=. --grpc_python_out=. vector_pipelines/proto/*.proto

.PHONY: all
all: format lint mypy test
