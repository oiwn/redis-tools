.PHONY: tags test tests coverage covreport

tags:
	ctags -R .

test:
	py.test -s tests/test_$(tname).py -W "ignore"

tests:
	py.test -v tests/ -W "ignore"

coverage:
	pytest --cov=rdt tests/ -W "ignore"

covreport:
	pytest --cov=rdt tests/ -W "ignore" && coverage html


