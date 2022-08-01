doc_pipeline:
	jupyter nbconvert --to markdown --execute nbs/README.ipynb --output-dir . --output README.md && \
	jupyter nbconvert --clear-output nbs/README.ipynb
