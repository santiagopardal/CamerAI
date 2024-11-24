install:
	mkdir -p Images
	touch camerai.log
	git submodule init
	git submodule update

	cd CamerAPI && make install

	cd CamerAPP && make install

	cd videos_processor && make install

	docker compose build


install-dev:
	mkdir -p Images
	touch camerai.log
	git submodule init
	git submodule update

	@if [ ! -f ./.env ]; then cp .env.schema .env; fi

	cd CamerAPI && make install

	cd CamerAPP && make install

	cd videos_processor && make install

	docker compose -f docker-compose.dev.yml build


clean:
	sudo rm -rf Images
	sudo rm -f camerai.log
	sudo rm -rf pgdata
	sudo rm -f node.json


fresh: clean install


fresh-dev: clean install-dev
