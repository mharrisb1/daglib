readme:
	jupyter nbconvert --to markdown --execute nbs/index.ipynb --output-dir . --output README.md && \
	jupyter nbconvert --clear-output nbs/index.ipynb

documentation:
	jupyter nbconvert --to markdown --execute nbs/index.ipynb nbs/*/* --output-dir docs/ && \
    jupyter nbconvert --clear-output nbs/index.ipynb nbs/*/*
