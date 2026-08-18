init:
	pip-compile requirements.in && pip-compile requirements-dev.in && pip-sync requirements-dev.txt

before-init:
	pip install pip-tools

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

terra-init:
	cd ./terraform && terraform init

.PHONY: proto clean rebuild

# สั่งคอมไพล์ proto และ fix import อัตโนมัติ
proto:
	python scripts/compile_proto.py

# สั่ง Clean
clean:
	python scripts/compile_proto.py --clean

# สั่ง Clean แล้ว Compile ใหม่ทันที
rebuild: clean proto

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down -v