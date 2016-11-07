fixture:

	python manage.py dumpdata inventory.SpareType inventory.Property --indent 2 --format yaml -o inventory/fixtures/SpareType.yaml
	python manage.py dumpdata inventory.Container --indent 2 --format yaml -o inventory/fixtures/Container.yaml
	python manage.py dumpdata inventory.Store --indent 2 --format yaml -o inventory/fixtures/Store.yaml

heroku migrate:
	heroku run python manage.py migrate