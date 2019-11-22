# cli-tools

## Installing

```
pip3 install codemagic-cli-tools
```

## Packaging for distribution

Don't forget the version number

```
python3 setup.py sdist bdist_wheel
```

## Publishing package (test)

```
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

## Publishing package (real)

```
python3 -m twine upload dist/*
```
