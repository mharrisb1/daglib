doc_pipeline:
	jupyter nbconvert --to markdown --execute nbs/README.ipynb --output-dir . --output README.md && \
	jupyter nbconvert --clear-output nbs/README.ipynb && \
	jupyter nbconvert --to markdown --execute nbs/* --output-dir docs/source && \
    jupyter nbconvert --clear-output nbs/* && \
	sphinx-build -b html docs/source docs/
