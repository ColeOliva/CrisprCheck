test:
	pytest -q

lint:
	flake8

run-demo:
	python -m crispr_check.cli search --guide GAGTCCGAGCAGAAGAAGA --pam NGG --fasta tests/data/small.fa --out results.csv
