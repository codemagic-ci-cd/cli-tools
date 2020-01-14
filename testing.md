## Install development depencencies

To run the tests or type checks, you'd first have to install the development
dependencies. This can be done with
[`pipenv`](https://pipenv.kennethreitz.org/en/latest/):

```bash
pipenv install --development
```

## Tests

Tests are invoked using [`pytest`](https://docs.pytest.org/en/latest/) framework:

```bash
pytest
```

Note that for the tests to run successfully, you'd have to define the following environment variables:
```bash
export TEST_APPLE_KEY_IDENTIFIER=...  # Key ID
export TEST_APPLE_ISSUER_ID=...  # Issued ID
```
And one of either
```bash
export TEST_APPLE_PRIVATE_KEY_PATH=...  # Path to private key in .p8 format
export TEST_APPLE_PRIVATE_KEY_CONTENT=...  # Content of .p8 private key
```

Those can be obtained from
[App Store Connect -> Users and Access -> Keys](https://appstoreconnect.apple.com/access/api).
For more information follow Apple's official documentation:
[Creating API Keys for App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api).

# Type checks

Static type checks are done using [`mypy`](http://mypy-lang.org/):

```bash
MYPYPATH=stubs mypy src/codemagic
```

