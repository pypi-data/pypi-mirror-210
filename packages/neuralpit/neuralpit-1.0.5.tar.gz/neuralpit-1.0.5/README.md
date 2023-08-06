# Update version
python -m pip install pip-tools
pip install bumpver
pip-compile --extra dev pyproject.toml
bumpver update --minor

# Install package locally
python -m pip install -e .