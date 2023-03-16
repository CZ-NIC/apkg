# setuptools read this version through setup.py.
# poetry updates this from git using poetry-dynamic-versioning / dunamai
#   also works during `python -m build`.
# scripts/make-archive.sh updates this using dunamai for `apkg make-archive`
__version__ = "0.0.0"
