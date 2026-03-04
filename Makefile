.PHONY: lint test

lint:
\truff check .

test:
\tpytest
