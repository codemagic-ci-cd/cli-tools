# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Commands

Dependencies are managed with `uv` (`uv sync` to set up). CI (`.github/workflows/run-checks.yml`) runs these on Python 3.8–3.14, and all of them must pass:

```shell
uv run ruff format --check .   # formatting
uv run ruff check .            # lint (isort uses force-single-line imports)
uv run mypy .                  # type checks (tests/ and doc.py are excluded)
uv run pytest                  # tests
```

Run a single test with `uv run pytest tests/tools/test_firebase_app_distribution.py::test_name`. Tests mirror the `src/codemagic` package layout.

Tests that hit the live App Store Connect, Google Play or Firebase APIs are skipped unless `RUN_LIVE_API_TESTS` is set, and they also need `TEST_APPLE_*`, `TEST_GCLOUD_*` or `TEST_FIREBASE_*` credentials (see README.md).

Regenerate the Markdown docs under `docs/` with `uv run python doc.py`. The docs are generated from the `CliApp` subclasses, so don't edit them by hand. Regenerate them whenever an action, argument or description changes.

## Compatibility constraints

- The package supports Python 3.8 (`ruff target-version = "py38"`). Use `from __future__ import annotations` and `typing.List`/`Optional`/etc. Avoid 3.9+ runtime syntax such as `list[str]` outside annotations, `X | Y` at runtime, or `match`.
- `mypy_path = "stubs"` provides local type stubs for `googleapiclient`, `httplib2`, `oauth2client` and `OpenSSL`.

## Release conventions for changes

Each user-facing PR bumps the version and records the change:
- `version` in `pyproject.toml`.
- `__version__` in `src/codemagic/__version__.py`, using the `X.Y.Z.dev` form. The release pipeline in `codemagic.yaml` rewrites it.
- The `codemagic-cli-tools` version in `uv.lock` (`uv lock`).
- A new entry at the top of `CHANGELOG.md` in the existing `Version X.Y.Z` / `-------------` format, with `**Features**`, `**Bugfixes**`, `**Docs**` and `**Development**` sections. Mark breaking Python API changes as `**Breaking**`. The release workflow uses the top entry as the GitHub release notes.

## Architecture

### CLI framework (`src/codemagic/cli/`)

Every executable listed in `[project.scripts]` is a `cli.CliApp` subclass exported from `codemagic.tools`, with `invoke_cli` as its entry point. The same classes are also the public Python API, so actions return values as well as printing them.

- The executable name comes from the class name (`AppStoreConnect` → `app-store-connect`).
- `@cli.action("name", *arguments, action_group=...)` turns a method into a CLI subcommand. Actions grouped under a `cli.ActionGroup` become nested subcommands, such as `app-store-connect builds list`. Both the method and the class must have a docstring, because it becomes the help text and is checked at runtime. `deprecation_info=ActionDeprecationInfo(alias, version)` keeps an old action name working as a hidden alias.
- Arguments are members of `cli.Argument` enums, defined in each tool's `arguments.py`. Their values are `cli.ArgumentProperties`, and `key` must match the method's keyword parameter name. Default values are read back via `SomeArgument.X.get_default()` in method signatures.
- `@cli.common_arguments(...)` declares class-level arguments that are passed to `__init__`. Tools with non-trivial construction override `from_cli_args` and forward framework options with `cls._parent_class_kwargs(cli_args)`.
- Typed argument values (`cli.TypedCliArgument` / `cli.EnvironmentArgumentValue`) handle parsing and validation. They support the `@env:VAR` and `@file:path` prefixes and can fall back to an environment variable (`environment_variable_key`).
- Raise the tool's `CLI_EXCEPTION_TYPE` (a `CliAppException` subclass) for expected failures; the CLI logs the message and exits with code 1. Any other exception exits with code 9 and writes the traceback to the log file.
- Run subprocesses through `CliApp.execute(...)`. It supports dry-run mode and obfuscates secrets in logged commands through `obfuscate_patterns`.

### Tool package layout (`src/codemagic/tools/`)

Small tools are single modules, for example `keychain.py` and `git_changelog.py`. Larger tools (`app_store_connect/`, `google_play/`, `firebase_app_distribution/`) are packages:
- `<tool>.py`: the `CliApp` class, assembled through multiple inheritance from action mixins.
- `actions/` and `action_groups/`: mixin classes containing the `@cli.action` methods.
- An abstract base (`abstract_base_action.py` or `*_action.py`): declares the shared attributes (`client`, `logger`, `printer`) and abstract signatures of actions defined in other mixins, so mixins can call each other in a type-safe way. Add a new action's signature here when other mixins need to call it.
- `arguments.py`, `argument_types.py`, `errors.py`, and `__main__.py` (which allows `python -m codemagic.tools.<tool>`).

### API and resource layers

- `apple/app_store_connect/` contains `AppStoreConnectApiClient`, which handles JWT auth and retries, plus one `ResourceManager` subclass per endpoint family, each with nested `Filter`/`Ordering` dataclasses. `apple/resources/` holds dataclass models with camelCase field names that mirror the API JSON (ruff `N815` is disabled there).
- `google/` contains `GoogleClient`-based `GooglePlayClient` and `FirebaseClient`, built on `googleapiclient`, with `services/` and `resources/` split per product.
- Enums that mirror API values subclass `models.enums.ResourceEnum`.

Conventions for these layers:
- Resource enums hold the exact wire values. When the CLI token has to differ from the wire value, add a separate enum in the tool layer's `argument_types.py` with a property that converts to the resource enum, and convert where the action calls into the client. `ReleasesOrderByArgument.order_by` → `OrderBy` is the reference example. Don't add CLI-presentation properties to resource enums.
- When an upstream API or tool introduces a new value, add the enum member. Don't add `_missing_` hooks or `UNKNOWN` catch-all members.

### Other packages

- `models/`: domain logic that doesn't depend on a particular API, such as provisioning profiles, certificates, export options, Android and iOS application packages, simulators, JUnit models, and the `xcresulttool` → JUnit conversion in `models/xctests/` (requires Xcode 16+).
- `shell_tools/`: wrappers around external binaries, including `bundletool` (the jar is bundled in `src/codemagic/data/jars/`), `keytool` and `jarsigner`.
- `scripts/code_signing_manager.rb`: a Ruby script that uses the `xcodeproj` gem. `models/code_signing_settings_manager.py` invokes it to apply provisioning profiles to Xcode projects.
- `utilities/log.py`: the logging setup. Logs always go to a file, and stream output is controlled by `--verbose`/`--silent`. Get loggers with `log.get_logger(cls)`.
