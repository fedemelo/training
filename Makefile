PYTHON = venv/bin/python

venv:
	source venv/bin/activate

ingest:
	$(PYTHON) src/backend/scripts/ingest.py

prompt:
	$(PYTHON) src/backend/scripts/prompt.py

format:
	venv/bin/isort . && venv/bin/black .

lint:
	venv/bin/flake8 src/

test:
	venv/bin/pytest

reset-db:
	psql -U postgres -d training -c "DROP TABLE IF EXISTS lap, record, session, event, activity, deviceinfo, developerdataid, fileid, fitfile CASCADE;"

db:
	psql -U postgres -d training

.PHONY: ingest format lint test reset-db connect-db venv
