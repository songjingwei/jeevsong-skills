.PHONY: validate setup-local-test check-local-test clean-local-test test

validate:
	python3 scripts/validate.py

setup-local-test:
	python3 scripts/manage_local_skills.py setup

check-local-test:
	python3 scripts/manage_local_skills.py check

clean-local-test:
	python3 scripts/manage_local_skills.py clean

test: validate
	python3 -m unittest discover -s tests -p 'test_*.py'
