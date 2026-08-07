init:
	pip-compile requirements.in && pip-compile requirements-dev.in && pip-sync requirements-dev.txt

before-init:
	pip install pip-tools

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload