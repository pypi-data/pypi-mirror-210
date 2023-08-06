rm -rf dist/*
echo $1
sed -i'.bak' "s/version = \"[0-9]*\.[0-9]*\.[0-9]*\"/version = \"$1\"/" pyproject.toml
python -m build
twine upload dist/* -u $PYUSR -p $PYPASS
