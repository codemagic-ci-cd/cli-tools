# Codemagic CLI Tools

Codemagic CLI Tools are a set of command-line utilities for managing Android and iOS app builds,
code signing, and deployment. The tools are used to power mobile app builds at [codemagic.io](https://codemagic.io) but can be also used in other virtual environments or locally.

# Installing

Codemagic CLI Tools are available on [PyPI](https://pypi.org/project/codemagic-cli-tools/)
and can be installed and updated using [pip](https://pip.pypa.io/en/stable/getting-started/).

```
python -m pip install codemagic-cli-tools
```

The package requires Python version 3.7+.

# Command line usage

Installing the package adds the following executables to your path:

- [`android-app-bundle`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/android-app-bundle/README.md)
- [`android-keystore`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/android-keystore/README.md)
- [`app-store-connect`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/app-store-connect/README.md)
- [`codemagic-cli-tools`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/codemagic-cli-tools/README.md)
- [`git-changelog`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/git-changelog/README.md)
- [`google-play`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/google-play/README.md)
- [`keychain`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/keychain/README.md)
- [`universal-apk`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/universal-apk/README.md)
- [`xcode-project`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/xcode-project/README.md)

Online documentation for all installed executables can be found under
[`docs`](https://github.com/codemagic-ci-cd/cli-tools/tree/master/docs#cli-tools).

Alternatively, you could see the documentation by using `--help` option from command line:

```bash
<command> --help
```
to see general description and subcommands for the tool, or

```bash
<command> <subcommand> --help
```
to get detailed information of the subcommand.

**For example:**

```
$ keychain create --help
usage: keychain create [-h] [--log-stream {stderr,stdout}] [--no-color] [--version] [-s] [-v] [-pw PASSWORD] [-p PATH]

Create a macOS keychain, add it to the search list

optional arguments:
  -h, --help            show this help message and exit

Optional arguments for command create:
  -pw PASSWORD, --password PASSWORD
                        Keychain password. Alternatively to entering PASSWORD in plaintext, it may also be specified using the "@env:" prefix followed by an environment variable name, or the "@file:" prefix followed by a path to the file containing the value. Example: "@env:<variable>" uses the value in the environment variable named "<variable>", and "@file:<file_path>" uses the value from the file at "<file_path>". [Default: '']

Options:
  --log-stream {stderr,stdout}
                        Log output stream. [Default: stderr]
  --no-color            Do not use ANSI colors to format terminal output
  --version             Show tool version and exit
  -s, --silent          Disable log output for commands
  -v, --verbose         Enable verbose logging for commands

Optional arguments for keychain:
  -p PATH, --path PATH  Keychain path. If not provided, the system default keychain will be used instead
```

# Usage from Python

In addition to the command line interface, the package also provides a mirroring Python API.
All utilities that are available as CLI tools are accessible from Python in package
[`codemagic.tools`](https://github.com/codemagic-ci-cd/cli-tools/blob/v0.28.0/src/codemagic/tools/__init__.py).
The CLI actions are instance methods that are decorated by the [`action`](https://github.com/codemagic-ci-cd/cli-tools/blob/v0.28.0/src/codemagic/cli/cli_app.py#L385)
decorator. For example, you can use the [`Keychain`](https://github.com/codemagic-ci-cd/cli-tools/blob/v0.28.0/src/codemagic/tools/keychain.py#L111)
tool from Python source as follows:

```python
In [1]: from pathlib import Path

In [2]: from codemagic.tools import Keychain

In [3]: Keychain().get_default()
Out[3]: PosixPath('/Users/priit/Library/Keychains/login.keychain-db')

In [4]: keychain = Keychain(Path("/tmp/new.keychain"))

In [5]: keychain.create()
Out[5]: PosixPath('/tmp/new.keychain')

In [6]: keychain.make_default()

In [7]: Keychain().get_default()
Out[7]: PosixPath('/private/tmp/new.keychain')
```

# Development

This project uses [Poetry](https://python-poetry.org/) to manage dependencies. Before starting development, please ensure that your
machine has Poetry available. Installation instructions can be found from their
[docs](https://python-poetry.org/docs/#installation).

Assuming you've already cloned the [repository](https://github.com/codemagic-ci-cd/cli-tools/)
itself, or a fork of it, you can get started by running

```shell
poetry install
```

This will install all required dependencies specified in the `poetry.lock` file.

The source code of the project lives inside the `src` directory and tests are
implemented in the `tests` directory.

### Code formatting and linting rules

Automatic code formatting is done with [Black](https://github.com/psf/black).
Invoke Black checks from repository root directory with

```shell
poetry run black --check .
```

Linting rules are enforced using [Ruff](https://beta.ruff.rs).
Checks can be started from repository root with

```shell
poetry run ruff check .
```

### Static type checks

A huge portion of the Python source code has type hints, and all public methods or functions
are expected to have type hints. Static type checks of the source code are performed using
[Mypy](http://mypy-lang.org/) from the repository root by running

```shell
poetry run mypy .
```

### Running tests

[Pytest](https://docs.pytest.org/en/stable/) is used as the framework. As mentioned above,
tests are stored in the `tests` directory, separated from package source code. Test code layout
mirrors the structure of the `codemagic` package in the source directory.

Tests can be started by running the following command from the repository root:

```shell
poetry run pytest
```

Note that tests that target [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi) or
[Google Play Developer API](https://developers.google.com/android-publisher) live endpoints
are skipped by default for obvious reasons. They can be enabled (either for TDD or other reasons)
by setting the environment variable `RUN_LIVE_API_TESTS` to any non-empty value.

Note that for the tests to run successfully, you'd have to define the following environment variables:
- For App Store Connect:
    ```shell
    export TEST_APPLE_KEY_IDENTIFIER=...  # Key ID
    export TEST_APPLE_ISSUER_ID=...  # Issued ID
    ```
    And either of the two:
    ```bash
    export TEST_APPLE_PRIVATE_KEY_PATH=...  # Path to private key in .p8 format
    export TEST_APPLE_PRIVATE_KEY_CONTENT=...  # Content of .p8 private key
    ```
  Those can be obtained from [App Store Connect -> Users and Access -> Keys](https://appstoreconnect.apple.com/access/api).
  For more information follow Apple's official documentation about [Creating API Keys for App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api).

- For Google Play:
    ```shell
    export TEST_GCLOUD_PACKAGE_NAME=... # Package name (Ex: com.google.example)'
    ```
    And either of the two:
    ```shell
    export TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_PATH=... # Path to gcloud service account creedentials with `JSON` key type
    export TEST_GCLOUD_SERVICE_ACCOUNT_CREDENTIALS_CONTENT=... # Content of gcloud service account creedentials with `JSON` key type
    ```

- For Firebase:
    Either of the two:
    ```shell
    export TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_PATH=... # Path to gcloud service account creedentials with `JSON` key type
    export TEST_FIREBASE_SERVICE_ACCOUNT_CREDENTIALS_CONTENT=... # Content of gcloud service account creedentials with `JSON` key type
    ```

### Pre-commit hooks

Optionally, the [pre-commit](https://pre-commit.com/) framework can be used to ensure that
the source code updates are compliant with all the rules mentioned above.

Installation instructions are available in their [docs](https://pre-commit.com/#installation).

The repository already contains pre-configured `.pre-commit-config.yaml`, so to enable
the hooks, just run

```shell
pre-commit install
```
