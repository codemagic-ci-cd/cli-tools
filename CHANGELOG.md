Version 0.55.0
-------------
Changes in this release are from [PR #441](https://github.com/codemagic-ci-cd/cli-tools/pull/441).

**Development**
- **Breaking**: Deprecate Python 3.7, and Python 3.8 is now the minimum version of Python required.
- Add support to Python 3.13.
- Update `cffi` version to be compatible with latest version.
- Add Python 3.13 to GitHub Actions test matrix.

Version 0.54.4
-------------

**Bugfixes**
- Fix `team_identifier` property on `codemagic.models.ProvisioningProfile` to always return a string as the type hint suggests. [PR #440](https://github.com/codemagic-ci-cd/cli-tools/pull/440)

Version 0.54.3
-------------

**Bugfixes**
- Support device class `APPLE_SILICON_MAC` on App Store Connect API [`Device`](https://developer.apple.com/documentation/appstoreconnectapi/device) responses. [PR #437](https://github.com/codemagic-ci-cd/cli-tools/pull/437)
- Make undocumented `preOrder` and deprecated `inAppPurchases` relationships on App Store connect https://developer.apple.com/documentation/appstoreconnectapi/app/relationships-data.dictionary model optional . [PR #439](https://github.com/codemagic-ci-cd/cli-tools/pull/439)

**Improvements**
- Fail action `app-store-connect fetch-signing-files` early with descriptive error message if bundle ID identifier is not given. [PR #438](https://github.com/codemagic-ci-cd/cli-tools/pull/438)

Version 0.54.2
-------------

**Bugfixes**
- Fix action `keychain add-certificates` for macOS 15.1 when adding certificates with empty password. [PR #436](https://github.com/codemagic-ci-cd/cli-tools/pull/436)
- Introduce a new retrying condition for `altool` commands as part of `app-store-connect` action when unexpected return codes occurs. [PR #435](https://github.com/codemagic-ci-cd/cli-tools/pull/435)

Version 0.54.1
-------------

**Bugfixes**
- Fix testcase duration parsing from `XCResult` bundle when using Xcode 16.0+. [PR #433](https://github.com/codemagic-ci-cd/cli-tools/pull/433)

Version 0.54.0
-------------

This release contains changes from [PR #431](https://github.com/codemagic-ci-cd/cli-tools/pull/431)

**Features**
- Use new `xcresulttool` APIs for XcResult parsing when Xcode 16+ is selected. Applies to `xcode-project` actions `run-tests`, `test-summary` and `junit-test-results`.

**Bugfixes**
- Omit `failures` and `errors` attributes from JUnit `<testsuites>` in case none of the child `<testsuite>` elements specify those values instead of setting them to `0`.

**Development**
- Add new XcResult to JUnit test results converter implementation `Xcode16XcResultConverter`.
- Rename `XcResultConverter` to `LegacyXcResultConverter`.
- Add abstract `XcResultConverter` which automatically chooses correct implementation.
- Refactor module `codemagic.models.xctest.xcresult` to a package and move its contents to submodule `legacy_xcresult`. All public definitions remain accessible using the old namespace.
- Add submodule `xcode_16_xcresult` to package `codemagic.models.xctest.xcresult`.
- Remove method `get_tool_version` from `XcResultTool`.
- Add methods `is_legacy`, `get_test_report_summary` and `get_test_report_tests` to `XcResultTool`.
- Prohibit using `XcResultTool` methods `get_object` and `get_bundle` when Xcode 16 or newer is selected.

Version 0.53.9
-------------

**Development**
- Change release pipeline not to include source distributions in PyPI releases. Those are still available from GitHub. [PR #429](https://github.com/codemagic-ci-cd/cli-tools/pull/429)

Version 0.53.8
-------------

**Bugfixes**
- Fix action `keychain add-certificates` on macOS 15.0. [PR #428](https://github.com/codemagic-ci-cd/cli-tools/pull/428)

Version 0.53.7
-------------

**Bugfixes**
- Fix saving Apple code signing certificates to disk when using LibreSSL 3.0.0+. [PR #427](https://github.com/codemagic-ci-cd/cli-tools/pull/427)

Version 0.53.6
-------------

**Features**
- Update tool `app-store-connect` to support all Apple's [locales](https://developer.apple.com/documentation/appstoreconnectapi/app_store/app_metadata/app_info_localizations/managing_metadata_in_your_app_by_using_locale_shortcodes). [PR #425](https://github.com/codemagic-ci-cd/cli-tools/pull/425)

**Bugfixes**
- Cache generated fallback enumeration types so that enum identity checks work for undefined, but allowed enumerations. [PR #425](https://github.com/codemagic-ci-cd/cli-tools/pull/425)

**Docs**
- Update documentations for the following actions: [PR #425](https://github.com/codemagic-ci-cd/cli-tools/pull/425)
  - `app-store-connect app-store-versions localizations`,
  - `app-store-connect beta-build-localizations create`,
  - `app-store-connect beta-build-localizations list`,
  - `app-store-connect builds add-beta-test-info`,
  - `app-store-connect builds submit-to-app-store`,
  - `app-store-connect publish`.

Version 0.53.5
-------------

This release contains changes from [PR #421](https://github.com/codemagic-ci-cd/cli-tools/pull/421)
and [PR #422](https://github.com/codemagic-ci-cd/cli-tools/pull/422)

**Development**
- Add support for mutually exclusive groups on argument parser.

**Deprecations**

- The argument `--project-id` has been deprecated in favor of `--project-number` on all actions
of the tool `firebase-app-distribution` to be compliant with the [Firebase documentation](https://firebase.google.com/docs/projects/learn-more#project-number).

- A warning message is shown if commands are invoked with the deprecated argument.

Version 0.53.4
-------------

This is a bugfix version containing changes from [PR #424](https://github.com/codemagic-ci-cd/cli-tools/pull/424) to fix test result parsing with Xcode 16.0 beta 3+.

**Bugfixes**
- The following actions were fixed when used in conjunction with Xcode 16.0 beta 3+:
    - `xcode-project run-tests`,
    - `xcode-project test-summary`,
    - `xcode-project junit-test-results`.

**Development**
- Add `get_tool_version` method to `codemagic.models.xctests.XcResultTool` which can be used to detect `xcresulttool` version from currently active Xcode developer directory.

Version 0.53.3
-------------

This release contains changes from [PR #415](https://github.com/codemagic-ci-cd/cli-tools/pull/415).

**Bugfixes**
- Support signing certificates with type `DEVELOPER_ID_APPLICATION_G2` for `app-store-connect`.

**Development**
- Update `ruff` settings to be compatible with latest version.
- Update `pre-commit` hook versions.

Version 0.53.2
-------------

This is a bugfix release to resolve a regression that was introduced in version 0.53.1. [PR #413](https://github.com/codemagic-ci-cd/cli-tools/pull/413)

**Bugfixes**
- Remove type-checking import statement that is not available on Python 3.7.

Version 0.53.1
-------------

This bugfix release contains changes from [PR #411](https://github.com/codemagic-ci-cd/cli-tools/pull/411).

**Bugfixes**
- Fix saving code signing certificates fetched from App Store Connect if the certificate subject line contains non-ascii characters and export is done using OpenSSL version 3.2+.

**Dependencies**:
- Set lower bound version limit `>= 38.0.0` to [`cryptography`](https://cryptography.io/) dependency.


Version 0.53.0
-------------

**Feature**
- Update action `app-store-connect publish` to allow adding builds to beta groups without submitting to TestFlight. [PR #410](https://github.com/codemagic-ci-cd/cli-tools/pull/410)

Version 0.52.0
-------------

**Feature**
- Add optional argument `--platform` to action `app-store-connect apps builds` to list builds only for selected platform. [PR #407](https://github.com/codemagic-ci-cd/cli-tools/pull/407)
- Add optional argument `--platform` to action `app-store-connect builds list` to list builds only for selected platform. [PR #407](https://github.com/codemagic-ci-cd/cli-tools/pull/407)
- Add optional argument `--platform` to action `app-store-connect apps expire-build-submitted-for-review` to expire builds only for specified platform. [PR #407](https://github.com/codemagic-ci-cd/cli-tools/pull/407)

**Bugfixes**
- Action `app-store-connect publish` will only expire builds for the same platform that is being published when invoked with option `--expire-build-submitted-for-review`. [PR #407](https://github.com/codemagic-ci-cd/cli-tools/pull/407)
- Fix argument `--credentials` validation for tool `google-play`. [PR #406](https://github.com/codemagic-ci-cd/cli-tools/pull/406)

**Documentation**
- Update documentation for actions: [PR #407](https://github.com/codemagic-ci-cd/cli-tools/pull/407)
  - `app-store-connect apps builds`,
  - `app-store-connect apps expire-build-submitted-for-review`,
  - `app-store-connect builds list`.

Version 0.51.1
-------------

This is a bugfix release containing changes from [PR #405](https://github.com/codemagic-ci-cd/cli-tools/pull/405). Apple removed `idfaDeclaration` key from the data structure that represents App Store Version resources, which caused failures in App Store Connect client methods. Consequently, CLI actions started to fail.

**Bugfixes**
- Fix actions:
  - `app-store-connect app-store-versions create`,
  - `app-store-connect app-store-versions update`,
  - `app-store-connect apps app-store-versions`,
  - `app-store-connect builds app-store-version`,
  - `app-store-connect builds submit-to-app-store`,
  - `app-store-connect publish` when executed with `--app-store` option.

**Development**
- Remove attribute `idfaDeclaration` from `AppStoreVersion.Relationships`.
- Update App Store Connect API mock response for App Store Version.


Version 0.51.0
-------------

The highlight of this release is added support for phased releases when publishing application to App Store Connect, which was added in [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402).

**Features**
- Add new actions to work with phased releases in App Store Connect ([PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)):
  - `app-store-connect app-store-version-phased-releases enable`
  - `app-store-connect app-store-version-phased-releases set-state`
  - `app-store-connect app-store-version-phased-releases cancel`
  - `app-store-connect app-store-versions phased-release`
- Update actions `app-store-connect builds submit-to-app-store` and `app-store-connect publish` support enabling and disabling releasing App Store version in phases. [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)

**Documentation**
- Add documentation for new action group ([PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)):
  - `app-store-connect app-store-version-phased-releases`
- Update documentation for action groups ([PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)):
  - `app-store-connect builds submit-to-app-store`
  - `app-store-connect publish`
- Add documentation for actions ([PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)):
  - `app-store-connect app-store-version-phased-releases enable`
  - `app-store-connect app-store-version-phased-releases set-state`
  - `app-store-connect app-store-version-phased-releases cancel`
  - `app-store-connect app-store-versions phased-release`

**Bugfixes**
- Fix App Store Connect API responses deserialization for cases when resource contains an empty relationship. [PR #401](https://github.com/codemagic-ci-cd/cli-tools/pull/401)
- Fix globbing files using current path pattern. [PR #403](https://github.com/codemagic-ci-cd/cli-tools/pull/403)

**Development**
- Add missing attributes and relationships to `codemagic.apple.resources.App` and `codemagic.apple.resources.Build`. [PR #383](https://github.com/codemagic-ci-cd/cli-tools/pull/383)
- Define new enumerations `codemagic.apple.resources.enums.BuildAudienceType` and `codemagic.apple.resources.enums.SubscriptionStatusUrlVersion`. [PR #383](https://github.com/codemagic-ci-cd/cli-tools/pull/383)
- Add new model definition `codemagic.apple.resources.AppStoreVersionPhasedRelease`. [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)
- Add new App Store Connect API resource manager  `AppStoreVersionPhasedReleases` that implements HTTP client methods to work with App Store version phased releases. [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)
- Add new HTTP client methods `read_app_store_version_phased_release` and `read_app_store_version_phased_release_data` to App Store Connect API resource manager `AppStoreVersions`. [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)
- Refactor `BuildsActionGroup` of `AppStoreConnect` by moving methods `submit_to_testflight` and `submit_to_app_store` along used private methods to dedicated action classes `SubmitToTestFlightAction` and `SubmitToAppStoreAction` respectively. Python API via parent `AppStoreConnect` class remains identical to what it was. [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)
- Update public methods in `ResourceManagerMixin` to take both `ResourceId` and `Resource` instances as methods arguments where only IDs were allowed before. [PR #402](https://github.com/codemagic-ci-cd/cli-tools/pull/402)


Version 0.50.7
-------------

**Improvements**
- Remove usages of deprecated datetime properties on `x509.Certificate` instances. [PR #399](https://github.com/codemagic-ci-cd/cli-tools/pull/399)

Version 0.50.6
-------------

**Bugfixes**
- Fix actions `firebase-app-distribution get-latest-build-version` and `firebase-app-distribution releases list` to support releases with non-integer build version. [PR #397](https://github.com/codemagic-ci-cd/cli-tools/pull/397)

**Development**
- CI: Use test matrix to define Python versions in GitHub actions test workflows. [PR #396](https://github.com/codemagic-ci-cd/cli-tools/pull/396)

Version 0.50.5
-------------

This version reverts changes that were introduced in `0.50.4` as they did not have intended effect. [PR #395](https://github.com/codemagic-ci-cd/cli-tools/pull/395)

Version 0.50.4
-------------

**Bugfixes**
- Fix `app-store-connect publish` action getting stuck while binary is being uploaded using `altool`. [PR #394](https://github.com/codemagic-ci-cd/cli-tools/pull/394)

Version 0.50.3
-------------

**Bugfixes**
- Remove deprecated attributes and relationships for App Store Connect [App](https://developer.apple.com/documentation/appstoreconnectapi/app/) data structure. [PR #392](https://github.com/codemagic-ci-cd/cli-tools/pull/392)
  - `availableInNewTerritories` attribute,
  - `availableTerritories` and `prices` relationships.

Version 0.50.2
-------------

**Features**
- Allow custom export options in export options properly list for `xcode-project build-ipa` actions. [PR #391](https://github.com/codemagic-ci-cd/cli-tools/pull/391)

Version 0.50.1
-------------

**Bugfixes**
- Fix error handling for corrupt Xcresult parsing in `xcode-project` actions. [PR #390](https://github.com/codemagic-ci-cd/cli-tools/pull/390)

Version 0.50.0
-------------

**Features**
- Add new actions to work with bundle identifier capabilities [PR #388](https://github.com/codemagic-ci-cd/cli-tools/pull/388):
  - `app-store-connect bundle-ids capabilities` to list the capabilities that are enabled for identifier,
  - `app-store-connect bundle-ids enable-capabilities` to enable capabilities for identifier,
  - `app-store-connect bundle-ids disable-capabilities` to disable capabilities for identifier.

Version 0.49.0
-------------

This release contains changes from [PR #386](https://github.com/codemagic-ci-cd/cli-tools/pull/386) and [PR #387](https://github.com/codemagic-ci-cd/cli-tools/pull/387).

**Features**
- Unify `app-store-connect` command line API experience by gathering similar actions under respective action groups.
- New action groups were added to group similar actions together:
  - `app-store-connect bundle-ids`,
  - `app-store-connect certificates`,
  - `app-store-connect devices`,
  - `app-store-connect profiles`.

**Deprecations**
The following actions are deprecated and show a warning message when invoked:
  - `app-store-connect list-builds` (replaced by `app-store-connect builds list`),
  - `app-store-connect create-bundle-id` (replaced by `app-store-connect bundle-ids create`),
  - `app-store-connect delete-bundle-id` (replaced by `app-store-connect bundle-ids delete`),
  - `app-store-connect get-bundle-id` (replaced by `app-store-connect bundle-ids get`),
  - `app-store-connect list-bundle-id-profiles` (replaced by `app-store-connect bundle-ids profiles`),
  - `app-store-connect list-bundle-ids` (replaced by `app-store-connect bundle-ids list`),
  - `app-store-connect create-certificate` (replaced by `app-store-connect certificates create`),
  - `app-store-connect delete-certificate` (replaced by `app-store-connect certificates delete`),
  - `app-store-connect get-certificate` (replaced by `app-store-connect certificates get`),
  - `app-store-connect list-certificates` (replaced by `app-store-connect certificates list`),
  - `app-store-connect list-devices` (replaced by `app-store-connect devices list`),
  - `app-store-connect register-device` (replaced by `app-store-connect devices register`),
  - `app-store-connect create-profile` (replaced by `app-store-connect profiles create`),
  - `app-store-connect delete-profile` (replaced by `app-store-connect profiles delete`),
  - `app-store-connect get-profile` (replaced by `app-store-connect profiles get`),
  - `app-store-connect list-profiles` (replaced by `app-store-connect profiles list`).

**Development**
- Decorator `@action` signature was changed. Optional keyword argument `deprecated_alias: str` was replaced by optional `deprecation_info: ActionDeprecationInfo` which holds both version in which the action was deprecated, and the deprecated name of the action.
- Decorator `@action` definition was moved from `codemagic.cli.cli_app` to `codemagic.cli.action`. It is still accessible from package `codemagic.cli` as before.

**Documentation**
- Remove documentation of deprecated actions:
  - `app-store-connect list-builds` (replaced by `app-store-connect builds list`),
  - `app-store-connect create-bundle-id` (replaced by `app-store-connect bundle-ids create`),
  - `app-store-connect delete-bundle-id` (replaced by `app-store-connect bundle-ids delete`),
  - `app-store-connect get-bundle-id` (replaced by `app-store-connect bundle-ids get`),
  - `app-store-connect list-bundle-id-profiles` (replaced by `app-store-connect bundle-ids profiles`),
  - `app-store-connect list-bundle-ids` (replaced by `app-store-connect bundle-ids list`),
  - `app-store-connect create-certificate` (replaced by `app-store-connect certificates create`),
  - `app-store-connect delete-certificate` (replaced by `app-store-connect certificates delete`),
  - `app-store-connect get-certificate` (replaced by `app-store-connect certificates get`),
  - `app-store-connect list-certificates` (replaced by `app-store-connect certificates list`),
  - `app-store-connect list-devices` (replaced by `app-store-connect devices list`),
  - `app-store-connect register-device` (replaced by `app-store-connect devices register`),
  - `app-store-connect create-profile` (replaced by `app-store-connect profiles create`),
  - `app-store-connect delete-profile` (replaced by `app-store-connect profiles delete`),
  - `app-store-connect get-profile` (replaced by `app-store-connect profiles get`),
  - `app-store-connect list-profiles` (replaced by `app-store-connect profiles list`).
- Add documentation for new action groups:
  - `app-store-connect bundle-ids`,
  - `app-store-connect certificates`,
  - `app-store-connect devices`,
  - `app-store-connect profiles`.
- Update documentation for action groups:
  - `app-store-connect builds`.
- Add documentation for actions:
  - `app-store-connect builds list` (used to be `app-store-connect list-builds`)
  - `app-store-connect bundle-ids create` (used to be `app-store-connect create-bundle-id`)
  - `app-store-connect bundle-ids get` (used to be `app-store-connect get-bundle-id`)
  - `app-store-connect bundle-ids list` (used to be `app-store-connect list-bundle-ids`)
  - `app-store-connect bundle-ids profiles` (used to be `app-store-connect list-bundle-id-profiles`)
  - `app-store-connect app-store-connect certificates create` (used to be `app-store-connect create-certificate`)
  - `app-store-connect app-store-connect certificates delete` (used to be `app-store-connect delete-certificate`)
  - `app-store-connect app-store-connect certificates get` (used to be `app-store-connect get-certificate`)
  - `app-store-connect app-store-connect certificates list` (used to be `app-store-connect list-certificates`)
  - `app-store-connect app-store-connect devices list` (used to be `app-store-connect list-devices`)
  - `app-store-connect app-store-connect devices register` (used to be `app-store-connect register-device`)
  - `app-store-connect app-store-connect profiles create` (used to be `app-store-connect create-profile`)
  - `app-store-connect app-store-connect profiles delete` (used to be `app-store-connect delete-profile`)
  - `app-store-connect app-store-connect profiles get` (used to be `app-store-connect get-profile`)
  - `app-store-connect app-store-connect profiles list` (used to be `app-store-connect list-profiles`)

Version 0.48.2
-------------

This release contains changes from [PR #382](https://github.com/codemagic-ci-cd/cli-tools/pull/382)

**Features**
- Speed improvements for `app-store-connect` actions `get-latest-testflight-build-number`, `get-latest-app-store-build-number` and `app-store-connect get-latest-build-number` in case the application has a lot of versions in App Store Connect.

**Development**
- Add new App Store Connect API Client methods:
  - `codemagic.apple.app_store_connect.apps.Apps.list_app_store_versions_data` to fetch application's App Store versions as `list[dict]`,
  - `codemagic.apple.app_store_connect.versioning.AppStoreVersions.read_build_data` to fetch build of App Store version as `dict`,
  - `codemagic.apple.app_store_connect.versioning.PreReleaseVersions.list_data` to fetch pre-release versions as `list[dict]`,
  - `codemagic.apple.app_store_connect.versioning.PreReleaseVersions.list_builds_data` to fetch builds of pre-release version as `list[dict]`.
- Move implementations of latest build number actions from `codemagic.tools.AppStoreConnect` to dedicated classes and plug them back in as mixins.

Version 0.48.1
-------------

**Bugfixes**
- Fix error handling for invalid App Store Connect API private keys for `app-store-connect` actions. [PR #381](https://github.com/codemagic-ci-cd/cli-tools/pull/381)

Version 0.48.0
-------------

This PR contains changes from [PR #380](https://github.com/codemagic-ci-cd/cli-tools/pull/380)

**Features**
- Add new actions:
  - `app-store-connect app-store-versions get` to show App Store Version information. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/read_app_store_version_information).
  - `app-store-connect review-submission-items delete` to remove existing review submission item from App Store Connect. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/delete_v1_reviewsubmissionitems_id).
  - `app-store-connect review-submissions items` to list review submission items of specified review submission. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/list_the_items_in_a_review_submission).
- Add option `--locale` to action `app-store-connect app-store-versions localizations` to filter retrieved localizations by given specified locales.
- Improve error message for action `app-store-connect review-submission-items create` if creating review submission item fails because required values are missing for application default locale on respective App Store Version.

**Bugfixes**
- Fix invoking action `app-store-connect review-submission-items create` from command line.
- Do not require device IDs for action `app-store-connect create-profile` when not creating development or Ad Hoc provisioning profiles.

**Development**
- Add new module `codemagic.utilities.case_conversion` with public functions `snake_to_camel` and `camel_to_snake`.
- Add new client method `list_items` to review submissions resource manager in `src/codemagic/apple/app_store_connect/versioning/review_submissions.py` to retrieve submission items list from App Store Connect.
- `AppStoreConnectError` exceptions now have field `api_error: Optional[ErrorResponse]` to store App Store Connect API error information.

**Documentation**
- Update documentation for action groups
  - `app-store-connect app-store-versions`,
  - `app-store-connect review-submissions`,
  - `app-store-connect review-submission-items`.
- Add documentation for actions:
  - `app-store-connect app-store-versions get`,
  - `app-store-connect review-submissions items`,
  - `app-store-connect review-submission-items delete`.
- Update documentation for actions:
  - `app-store-connect app-store-versions localizations`,
  - `app-store-connect review-submission-items create`,
  - `app-store-connect create-profile`.

Version 0.47.4
-------------

**Bugfixes**
- Fail gracefully with informative error message if CLI args are passed with invalid encoding. [PR #376](https://github.com/codemagic-ci-cd/cli-tools/pull/376)
- Do not require `--device-ids` for action `app-store-connect create-profile` when not creating development or ad-hoc provisioning profiles. [PR #377](https://github.com/codemagic-ci-cd/cli-tools/pull/377)
- Fix error handling if device IDs are missing and development or ad-hoc provisioning profiles are being created (applies to actions `app-store-connect create-profile` and `app-store-connect fetch-signing-files`). [PR #377](https://github.com/codemagic-ci-cd/cli-tools/pull/377)
- Fix resolving certificate type for Mac Catalyst and In-House provisioning profiles. [PR #378](https://github.com/codemagic-ci-cd/cli-tools/pull/378)
- Improve error handling for `google-play` actions. Capture `oauth2client.client` errors in Google Play API client so that the action fails gracefully with appropriate error message. [PR #379](https://github.com/codemagic-ci-cd/cli-tools/pull/379)

**Docs**
- Update option `--device-ids` documentation for action `app-store-connect create-profile`. [PR #377](https://github.com/codemagic-ci-cd/cli-tools/pull/377)

Version 0.47.3
-------------

**Bugfixes**
- Fix handling of relative certificate path patterns for action `keychain add-certificates`. [PR #374](https://github.com/codemagic-ci-cd/cli-tools/pull/374)

Version 0.47.2
-------------

**Bugfixes**
- Fix actions `firebase-app-distribution get-latest-build-version` and `firebase-app-distribution releases list` for cases when specified application does not have any releases available. [PR #373](https://github.com/codemagic-ci-cd/cli-tools/pull/373)

Version 0.47.1
-------------

**Bugfixes**
- Update action `xcode-project use-profiles`. Fix assigning provisioning profiles to Xcode targets that have SDK specific provisioning profile specifiers. [PR #371](https://github.com/codemagic-ci-cd/cli-tools/pull/371)
- Do not crash `xcode-project` actions `clean`, `build-ipa` and `run-tests` if [`xcpretty`](https://github.com/xcpretty/xcpretty) is not installed. [PR #372](https://github.com/codemagic-ci-cd/cli-tools/pull/372)

Version 0.47.0
-------------

Changes in this release are from [PR #370](https://github.com/codemagic-ci-cd/cli-tools/pull/370) and add Python 3.12 compatibility.

[PEP-632](https://peps.python.org/pep-0632/) deprecated `distutils` module, and it was removed entirely in Python 3.12. This release ensures that `distutils` module is not used any more.

**None of the breaking changes have an effect on command line usage**, only the Python API is affected.

**Development**
- **Breaking**: Type of `codemagic.models.Xcode.version` property was changed. Instead of `distutils.version.LooseVersion` it is now `packaging.version.Version`.
- **Breaking**: Type of `codemagic.models.simulator.Runtime.runtime_version` property was changed. Instead of `distutils.version.LooseVersion` it is now `packaging.version.Version`.

Version 0.46.2
-------------

**Features**
- Show full executed command in error output if action execution fails unexpectedly. [PR #364](https://github.com/codemagic-ci-cd/cli-tools/pull/364)
- Show full exception tracktrace in STDOUT logs if `--verbose` option is set. [PR #364](https://github.com/codemagic-ci-cd/cli-tools/pull/364)

**Bugfixes**
- Fix handing of required arguments to `google-play` if they are defined as empty strings (`--track`, `-tracks`, `--package-name`, `--source-track` and `--target-track`). [PR #363](https://github.com/codemagic-ci-cd/cli-tools/pull/363)
- Fix looking for errors from Xcode build logs as part of `xcode-project build-ipa` if the logs contain byte sequences that cannot be decoded. [PR #365](https://github.com/codemagic-ci-cd/cli-tools/pull/365)

**Development**
- Support iterating over binary file descriptors with `codemagic.utilities.backwards_file_reader.iter_backwards`. [PR #365](https://github.com/codemagic-ci-cd/cli-tools/pull/365)

Version 0.46.1
-------------

**Bugfixes**
- Fix Google Play release promotion with action `google-play tracks promote-release` for releases that have release notes. [PR #361](https://github.com/codemagic-ci-cd/cli-tools/pull/361)

**Development**
- Add GitHub Actions job to run tests with Python 3.12. [PR #362](https://github.com/codemagic-ci-cd/cli-tools/pull/362)

Version 0.46.0
-------------

**Features**
- Add new option `--max-find-build-wait` to action `app-store-connect publish` to configure maximum waiting time to discover uploaded build from App Store Connect before failing publishing. Defaults to 10 minutes. [PR #355](https://github.com/codemagic-ci-cd/cli-tools/pull/355)

**Docs**
- Add option `--max-find-build-wait` documentation for action `app-store-connect publish`. [PR #355](https://github.com/codemagic-ci-cd/cli-tools/pull/355)
- Update option `--cancel-previous-submissions` documentation for actions `app-store-connect builds submit-to-app-store` and `app-store-connect publish`. [PR #353](https://github.com/codemagic-ci-cd/cli-tools/pull/353)

Version 0.45.3
-------------

**Bugfixes**
- Support Apple Vision Pro devices in App Store Connect API read device information and list devices endpoints. This is done by declaring `APPLE_VISION_PRO` definition in enumeration `codemagic.apple.resources.enums.DeviceClass`. [PR #357](https://github.com/codemagic-ci-cd/cli-tools/pull/357)

Version 0.45.2
-------------

**Bugfixes**
- Fix initializing `codemagic.models.application_package.Ipa` objects for big binaries (exceeding 4GB in size). [PR #356](https://github.com/codemagic-ci-cd/cli-tools/pull/356)

Version 0.45.1
-------------

**Bugfixes**
- Ensure that build for correct platform is looked up from App Store Connect after initial upload completes using `app-store-connect publish`. [PR #352](https://github.com/codemagic-ci-cd/cli-tools/pull/352)

Version 0.45.0
-------------

Additions and changes from [pull request #349](https://github.com/codemagic-ci-cd/cli-tools/pull/349). Resolves [issue #344](https://github.com/codemagic-ci-cd/cli-tools/issues/344).

**Features**
- Add new option `--include-version` to `app-store-connect` actions `get-latest-build-number`, `get-latest-app-store-build-number` and `get-latest-testflight-build-number`. If specified, the action outputs matched build's version string in addition to build number.

**Bugfixes**
- Output valid `JSON` string with `app-store-connect` actions `get-latest-build-number`, `get-latest-app-store-build-number` and `get-latest-testflight-build-number` if `--json` option is specified.

**Docs**
- Documentation was updated for actions:
  - `app-store-connect get-latest-build-number`,
  - `app-store-connect get-latest-app-store-build-number`,
  - `app-store-connect get-latest-testflight-build-number`.

Version 0.44.1
-------------

**Features**
- Log out processed build and its beta detail information before submitting it to App Store or TestFlight. [PR #347](https://github.com/codemagic-ci-cd/cli-tools/pull/347)

Version 0.44.0
-------------

Additions and changes from [pull request #345](https://github.com/codemagic-ci-cd/cli-tools/pull/345).

**Features**
- Add a new action `google-play tracks promote-release` to promote a release from one Google Play release track to another.

**Development**
- Define a new common argument type `bounded_number` for CLI usage that can be used to load floats and integers from CLI inputs within specified ranges.
- Add a new client method `update_track` to update release track in Google Play API client `codemagic.google_play.api_client.GooglePlayDeveloperAPIClient`.

**Documentation**
- Update documentation for action group `google-play tracks`.
- Add documentation for action `google-play tracks promote-release`.

Version 0.43.0
-------------

Additions and changes from [pull request #340](https://github.com/codemagic-ci-cd/cli-tools/pull/340). Resolves [issue #339](https://github.com/codemagic-ci-cd/cli-tools/issues/339).

**Features**
- Support submitting macOS packages to TestFlight using `app-store-connect publish --testflight`.
- Add new action `app-store-connect builds beta-details` to show beta detail information for specific build.
- Waiting for App Store Connect build processing also waits for beta builds details to be processed before returning.

**Development**
- Add new client method `read_beta_detail` to builds resource manager in `src/codemagic/apple/app_store_connect/builds/builds.py`.
- Add new definitions for App Store Connect models:
  - `BuildBetaDetail` for https://developer.apple.com/documentation/appstoreconnectapi/buildbetadetail,
  - `ExternalBetaState` enumeration for https://developer.apple.com/documentation/appstoreconnectapi/externalbetastate,
  - `InternalBetaState` for https://developer.apple.com/documentation/appstoreconnectapi/internalbetastate.

**Documentation**
- Add documentation for action `app-store-connect builds betat-details`.

Special thanks for contribution to [@nilsreichardt](https://github.com/nilsreichardt).

Version 0.42.2
-------------

**Bugfixes**
- Fix iOS application package abstraction layer in `codemagic.models.application_package.Ipa` to support large archives (exceeding 4GB in size). [PR #342](https://github.com/codemagic-ci-cd/cli-tools/pull/342)

Version 0.42.1
-------------

**Bugfixes**
- Do not require certificate private key to show certificate information using `app-store-connect get-certificate` if certificate is not saved to disk. [PR #337](https://github.com/codemagic-ci-cd/cli-tools/pull/337)

Version 0.42.0
-------------

**Features**
- Add `--omit-sdk` option to action `xcode-project run-tests` to exclude `-sdk` flag from being passed to underlying `xcodebuild test` command. [PR #335](https://github.com/codemagic-ci-cd/cli-tools/pull/335)

Version 0.41.0
-------------

Changes in this release improve `app-store-connect register-device` action by allowing to pass multiple UDIDs from different sources.

**None of the breaking changes have an effect on command line usage**, only the Python API of is affected.

**Features**
- Update `app-store-connect register-device` action:
  - The `--udid` argument now accepts multiple UDIDs.
  - The `--udid` argument now accepts a file or an environment variable as a source for UDIDs.
  - Introduce `--ignore-registration-errors` flag to continue registering devices despite errors
  - Introduce short flags:
    - `-n` flag for the device name,
    - `-u` flag for the UDIDs.

**Development**
- `AppStoreConnect.register_device` action method update:
  - It now accepts a list of UDIDs for registration at the keyword argument `device_udids`.
  - **Breaking**: `AppStoreConnect.register_device` now returns a list of registered devices.
- Add `ignore_registration_errors` keyword argument to continue registering devices despite errors.

**Documentation**
- Update documentation for `app-store-connect register-device` action:
  - Add new short flags: `-n` and `-u`.
  - Add the description for the new `--ignore-registration-errors` option.
  - Update the action description.

Version 0.40.5
-------------

**Development**
- Format Python source code with [Black](https://github.com/psf/black). [PR #322](https://github.com/codemagic-ci-cd/cli-tools/pull/322)
- Check Python linting rules with [Ruff](https://beta.ruff.rs). This replaces Flake8 and isort checks. [PR #322](https://github.com/codemagic-ci-cd/cli-tools/pull/322)

Version 0.40.4
-------------

**Deprecations**
- Method `list_capabilility_ids` of `codemagic.apple.app_store_connect.provisioning.BundleIds` is deprecated and shows a deprecation warning on calls. Use `list_capability_ids` of the same class instead. [PR #326](https://github.com/codemagic-ci-cd/cli-tools/pull/326)

**Development**
- Define `deprecated` decorator in `codemagic.utilities.decorators` to mark functions and methods as obsolete. [PR #326](https://github.com/codemagic-ci-cd/cli-tools/pull/326)

Version 0.40.3
-------------
**Features**
- Add support for visionOS runtime. [PR #325](https://github.com/codemagic-ci-cd/cli-tools/pull/325)

Version 0.40.2
-------------

**Bugfixes**
- Do not require `releaseNotes` from Firebase App Distribution release responses. [PR #323](https://github.com/codemagic-ci-cd/cli-tools/pull/323)

**Dependencies**
- Set lower bound version limit `>= 2.84.0` to [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) Python dependency in order to comply with Firebase App Distribution APIs. [PR #322](https://github.com/codemagic-ci-cd/cli-tools/pull/322)

Version 0.40.1
-------------

**Development**
- Add interface to declare aliases for deprecated actions. [PR #187](https://github.com/codemagic-ci-cd/cli-tools/pull/187)


Version 0.40.0
-------------

**Features**
- Introduce `firebase-app-distribution` tool with the actions:
  - `firebase-app-distribution releases list` action to list releases
  - `firebase-app-distribution get-latest-build-version` to get a version number for the latest release build

**Development**
- Introduce action methods:
  - `FirebaseAppDistribution.list_releases`
  - `FirebaseAppDistribution.get_latest_build_version`

**Tests**
- Coverage for Firebase client `FirebaseClient`
- Coverage for action methods: `FirebaseAppDistribution.list_releases` and `FirebaseAppDistribution.get_latest_build_version`

**Documentation**
- Document `firebase-app-distribution` tool
- Document actions:
  - `firebase-app-distribution releases list`
  - `firebase-app-distribution get-latest-build-version`

Version 0.39.2
-------------

**Features**
- Improve Python API for module `codemagic.tools.keychain`. Allow passing passwords as strings in addition to `codemagic.tools.keychain.Password` for `Keychain` methods. [PR #315](https://github.com/codemagic-ci-cd/cli-tools/pull/315)

**Bugfixes**
- Do not require `detail` attribute from App Store Connect API error responses. [PR #316](https://github.com/codemagic-ci-cd/cli-tools/pull/316)

Version 0.39.1
-------------

**Development**
- Marginal changes to start using timezone aware datetimes instead of timezone unaware datetimes. [PR #313](https://github.com/codemagic-ci-cd/cli-tools/pull/313)

Version 0.39.0
-------------

**Dependencies**
- Remove upper version limit from [`cryptography`](https://cryptography.io/) dependency. [PR #309](https://github.com/codemagic-ci-cd/cli-tools/pull/309)

Version 0.38.3
-------------

**Docs**
- Documentation was updated for actions:
  - `app-store-connect get-latest-build-number`,
  - `app-store-connect get-latest-app-store-build-number`,
  - `app-store-connect get-latest-testflight-build-number`.

Version 0.38.2
-------------

**Bugfix**
- Improve action `xcode-project use-profiles` stability so that different invocation with the same set  of provisioning profiles will always yield the same changeset to Xcode project settings. [PR #308](https://github.com/codemagic-ci-cd/cli-tools/pull/308)

Version 0.38.1
-------------

**Bugfix**
- Update flag `--cancel-previous-submissions` for the `app-store-connect builds submit-to-app-store` action to wait for Apple's confirmation that the submission is cancelled before attempting to submit a new build.

Version 0.38.0
-------------

This is an enhancement release to further streamline the App Store review submission automation capabilities.

Additions and changes from [pull request #289](https://github.com/codemagic-ci-cd/cli-tools/pull/289). Resolves [issue #289](https://github.com/codemagic-ci-cd/cli-tools/issues/288).

**Features**

- Add new action `app-store-connect apps list-review-submissions` to list existing review submissions in the App Store for a specific application. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/get_v1_reviewsubmissions).
- Add new action `app-store-connect apps cancel-review-submissions` to cancel existing review submissions in the App Store based on their type for a specific app. Uses the already existing `app-store-connect review-submissions cancel` action internally that allows to set the submission status to `canceled` using `PATCH`. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/patch_v1_reviewsubmissions_id).
- Add new action `app-store-connect builds expire` to expire a specific build that has been uploaded to App Store Connect. Modifies the existing build resource to an expired status using `PATCH`. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/modify_a_build).
- Add new action `app-store-connect apps expire-builds` to expire all builds uploaded to App Store Connect except the given build(s) for the specific application. Uses the aforementioned `app-store-connect builds expire` action internally.
- Add new action `app-store-connect apps expire-build-submitted-for-review` to expire build in App Store Connect that has been submitted to review and has not been `Approved` for a specific application. Uses the aforementioned `app-store-connect builds expire` action internally.
- Add new action `app-store-connect builds app` to get the application information based on the given build.
- Add flags `--cancel-previous-submissions` and `--expire-build-submitted-for-review` to the `app-store-connect publish` action.
- Add flag `--beta-review-state` to `app-store-connect apps builds` and `app-store-connect list-builds` actions for filtering builds based on their beta review state.
- Add flag `--cancel-previous-submissions` to the `app-store-connect builds submit-to-app-store` action.
- Add flag `--expire-build-submitted-for-review` to the `app-store-connect builds submit-to-testflight` action.

**Docs**
- Documentation updated for existing actions:
  - new option `--beta-review-state` for the action `app-store-connect apps builds`
  - new option `--cancel-previous-submissions` for the action `app-store-connect builds submit-to-app-store`
  - new option `--expire-build-submitted-for-review` for the action `app-store-connect builds submit-to-testflight`
  - new option `--beta-review-state` for the action `app-store-connect list-builds`
  - new options `--expire-build-submitted-for-review` and `--cancel-previous-submissions` for the action `app-store-connect publish`
  - description update for the `app-store-connect review-submissions cancel` action
- Documentation added for new actions:
  - `app-store-connect builds app`
  - `app-store-connect builds expire`
  - `app-store-connect apps expire-builds`
  - `app-store-connect apps expire-build-submitted-for-review`
  - `app-store-connect apps cancel-review-submissions`
  - `app-store-connect apps list-review-submissions`

Version 0.37.1
-------------

**Bugfixes**:
- Update action `app-store-connect build-ipa` to use `CODE_SIGN_STYLE=Manual` xcarg for underlying `xcodebuild archive` command when building with Xcode 14+ and none of the signing files are managed by Xcode. [PR #302](https://github.com/codemagic-ci-cd/cli-tools/pull/302)
- Make App Store and prerelease version comparisons more robust for `app-store-connect` actions. [PR #306](https://github.com/codemagic-ci-cd/cli-tools/pull/306)

**Dependencies**
- Declare direct Python dependency for package [`packaging`](https://packaging.pypa.io/en/stable/). Previously it was indirectly required by `setuptools`. [PR #306](https://github.com/codemagic-ci-cd/cli-tools/pull/306)

Version 0.37.0
-------------

This release includes changes from [PR #304](https://github.com/codemagic-ci-cd/cli-tools/pull/304).

**Features**
- Add option to include only _expired_ or _not expired_ builds to the latest build number lookup with action `app-store-connect get-latest-testflight-build-number`.

**Bugfixes**
- Avoid using _included_ resources when listing data with App Store Connect API for actions that detect the latest build number. When listing App Store or Prerelease (TestFlight) versions with included builds, then not all existing builds were present in the response. Fixed actions:
  - `app-store-connect get-latest-testflight-build-number`,
  - `app-store-connect get-latest-app-store-build-number` and
  - `app-store-connect get-latest-build-number`

**Development**
- Remove unused methods:
  - `AppStoreVersions.list_with_include`,
  - `PreReleaseVersions.list_with_include`.
- New API methods:
  - `PreReleaseVersions.list`,
  - `PreReleaseVersions.list_builds`.

Version 0.36.7
-------------

**Development**
- Regenerate `poetry.lock` with updated dependencies for development environments. [PR #301](https://github.com/codemagic-ci-cd/cli-tools/pull/301)
- Update type hints to be compatible with `mypy` version `0.991`. [PR #301](https://github.com/codemagic-ci-cd/cli-tools/pull/301)
- Marginal code formatting changes. [PR #301](https://github.com/codemagic-ci-cd/cli-tools/pull/301)

Version 0.36.6
-------------

This is a bugfix release including changes from [PR #300](https://github.com/codemagic-ci-cd/cli-tools/pull/300).

- Fixes the actions that detect the latest build number from App Store Connect for App Store or Pre Release (TestFlight) versions:
  - `app-store-connect get-latest-testflight-build-number`,
  - `app-store-connect get-latest-app-store-build-number` and
  - `app-store-connect get-latest-build-number`.

Version 0.36.5
-------------

**Bugfix**
- Support Python 3.11.1 [PR #295](https://github.com/codemagic-ci-cd/cli-tools/pull/295).

Version 0.36.4
-------------

This release contains changes from [PR #290](https://github.com/codemagic-ci-cd/cli-tools/pull/290).

**CI**
- Store releases only on PyPI and GitHub releases.
- Include wheel with fixed name under GitHub release assets so that latest version could be accessed with permalink.

Version 0.36.3
-------------

This release updates the current version of `bundletool`, as it is outdated, and issues potentially concerning it have risen for users with newer projects. Reported in [issue #286](https://github.com/codemagic-ci-cd/cli-tools/issues/286).

**Dependencies**
- Update [`bundletool`](https://developer.android.com/studio/command-line/bundletool) version from [`0.15.0`](https://github.com/google/bundletool/releases/tag/0.15.0) to [`1.13.1`](https://github.com/google/bundletool/releases/tag/1.13.1). [PR #287](https://github.com/codemagic-ci-cd/cli-tools/pull/287)

Version 0.36.2
-------------

**Bugfix**
- Remove mutable default value from `codemagic.models.Keystore` field `certificate_attributes`. [PR #284](https://github.com/codemagic-ci-cd/cli-tools/pull/284)

Version 0.36.1
-------------

**Bugfix**
- Fix regression from [PR #283](https://github.com/codemagic-ci-cd/cli-tools/pull/283).

Version 0.36.0
-------------

**Features**
- Update action `xcode-project use-profiles` argument `--custom-export-options` to accept export options definitions from file or environment variable references. If the value is not defined using CLI flag, it is automatically checked from environment variable `XCODE_PROJECT_CUSTOM_EXPORT_OPTIONS` by default. [PR #283](https://github.com/codemagic-ci-cd/cli-tools/pull/283)

Version 0.35.0
-------------

**Features**
- Add action `app-store-connect get-latest-build-number` that finds the highest build number across both TestFlight and App Store builds. [PR #281](https://github.com/codemagic-ci-cd/cli-tools/pull/281)

Version 0.34.3
-------------

**Bugfix**:
- Fix action `xcode-project detect-bundle-id` for cases when `xcodebuild -showBuildSettings` output does not have `PRODUCT_BUNDLE_IDENTIFIER` entry for some build settings. [PR #280](https://github.com/codemagic-ci-cd/cli-tools/pull/280)

**Improvements**:
- Action `xcode-project use-profiles` fails in case active Ruby installation does not have `xcodeproj` gem available. Should that happen, show appropriate and actionable error message. [PR #277](https://github.com/codemagic-ci-cd/cli-tools/pull/277)

Version 0.34.2
-------------

**Bugfix**:
- Do not throw `AssertionError` from `Certificate.from_p12` in case the given PKCS#12 container does not contain a certificate. Raise a `ValueError` with appropriate error message instead. [PR #274](https://github.com/codemagic-ci-cd/cli-tools/pull/274).

**Development**
- Regenerate `poetry.lock` with updated dependencies for development environments. [PR #275](https://github.com/codemagic-ci-cd/cli-tools/pull/275)

Version 0.34.1
-------------

This release includes changes from [PR #271](https://github.com/codemagic-ci-cd/cli-tools/pull/271).

**Docs**
- Update documentation for action `xcode-project use-profiles` option `--custom-export-options`.

Version 0.34.0
-------------

This release includes changes from [PR #269](https://github.com/codemagic-ci-cd/cli-tools/pull/269).

**Bugfix**:
- Previously non-encrypted private keys and PKCS#12 containers were treated equivalently to those that were encrypted with empty string. Now empty password for non-encrypted secret will yield an error, and vice-versa, not providing password for secret that is encrypted with empty string will also fail with encryption error.

**Dependencies**:
- Remove direct [`pyOpenSSL`](https://www.pyopenssl.org/) dependency.

**Development**:
- Replace `OpenSSL.crypto` usages with alternatives from `cryptography` library.
- Deprecate initialization of `codemagic.models.Certificate` from `OpenSSL.crypto.X509` instances. For now this will issue a warning, but will be fully removed in future versions.

Version 0.33.1
-------------

**Dependencies**:
- Set upper bound version limit `<38.0.0` to [`cryptography`](https://cryptography.io/) dependency. [PR #268](https://github.com/codemagic-ci-cd/cli-tools/pull/268)

Version 0.33.0
-------------

This release includes changes from [PR #266](https://github.com/codemagic-ci-cd/cli-tools/pull/266).

**Features**:
- Add `xcode-project show-build-settings` action. It outputs Xcode project build setting using `xcodebuild -showBuildSettings` command.
- Update `xcode-project build-ipa` action to run `xcodebuild -showBuildSettings` before `xcodebuild archive` to capture Xcode project build settings. The output of build settings is hidden by default, but shown if `--verbose` flag is set.

Version 0.32.2
-------------

This is a bugfix release to address regression from [PR #261](https://github.com/codemagic-ci-cd/cli-tools/pull/261).

**Bugfix**
- Fix setting code signing settings for unit test targets if matching host application target is not found. [PR #262](https://github.com/codemagic-ci-cd/cli-tools/pull/262)

Version 0.32.1
-------------

**Bugfix**
- Set proper code signing settings on Xcode unit testing targets (targets with product type `com.apple.product-type.bundle.unit-test`) using `xcode-project use-profiles` when appropriate code signing information is present. [PR #261](https://github.com/codemagic-ci-cd/cli-tools/pull/261)

Version 0.32.0
-------------

**Features**
- Action `app-store-connect fetch-signing-files` will create missing provisioning profiles so that all eligible team code signing certificates are included in it. [PR #257](https://github.com/codemagic-ci-cd/cli-tools/pull/257)

**Bugfixes**
- Configure proper signing info settings for Xcode UI testing targets with action `xcode-project use-profiles` provided that suitable signing files exist. [PR #258](https://github.com/codemagic-ci-cd/cli-tools/pull/258)

**Docs**
- Replace dead docstrings for `Profiles Profiles.list_device_ids`, `Profiles.list_certificate_ids`, `Profiles.get_bundle_id_resource_id` with pointers to the resources. Reported in [issue #237](https://github.com/codemagic-ci-cd/cli-tools/issues/237). [PR #259](https://github.com/codemagic-ci-cd/cli-tools/pull/259)

Version 0.31.3
-------------

**Bugfixes**
- Show error message when no matching test device is found in the Apple Developer Portal when creating an Ad Hoc or development provisioning profile. [PR #256](https://github.com/codemagic-ci-cd/cli-tools/pull/256)

Version 0.31.2
-------------

**Development**:
- Support file-like objects for `codemagic.utilities.backwards_file_reader.iter_backwards` in addition to file paths. [PR #255](https://github.com/codemagic-ci-cd/cli-tools/pull/255)

Version 0.31.1
-------------

**Development**:
- Save timestamp along with other failed App Store Connect HTTP request info. [PR #254](https://github.com/codemagic-ci-cd/cli-tools/pull/254)

Version 0.31.0
-------------

**Features**:
- Add new action `android-keystore certificate` to show certificate information for specific alias in the keystore. [PR #253](https://github.com/codemagic-ci-cd/cli-tools/pull/253)

Version 0.30.0
-------------

**Features**:
- Tool `app-store-connect` can now retry App Store Connect API requests that fail with status 5xx (server error). Number of retries can be configured by command line option `--api-server-error-retries`, or respective environment variable `APP_STORE_CONNECT_API_SERVER_ERROR_RETRIES`. [PR #249](https://github.com/codemagic-ci-cd/cli-tools/pull/249)

**Development**
- Save unexpected exception information and stacktrace to `$TMPDIR/codemagic-cli-tools/exceptions/yyyy-mm-dd/`. [PR #248](https://github.com/codemagic-ci-cd/cli-tools/pull/248)
- Save unsuccessful App Store Connect HTTP request and response information to `$TMPDIR/codemagic-cli-tools/failed-http-requests/yyyy-mm-dd/`. [PR #248](https://github.com/codemagic-ci-cd/cli-tools/pull/248)

**Docs**
- Update tool `app-store-connect` docs with `--api-server-error-retries` option. [PR #250](https://github.com/codemagic-ci-cd/cli-tools/pull/250)
- Add the changelog URL to the `pyproject.toml` project file so that the changelog reference is included under project links in PyPI. [PR #247](https://github.com/codemagic-ci-cd/cli-tools/pull/247)

Version 0.29.2
-------------

This is a bugfix release including changes from [PR #246](https://github.com/codemagic-ci-cd/cli-tools/pull/246).

**Bugfixes**
- Fix matching a profile in `app-store-connect fetch-signing-files` for cases where `type` is defined as `MAC_APP_DIRECT`.

Version 0.29.1
-------------

This is a bugfix release including changes from [PR #245](https://github.com/codemagic-ci-cd/cli-tools/pull/245).

**Bugfixes**
- Fix `xcode-project use-profiles` for cases when bundle identifier is defined in information property list files. Add fallback bundle identifier detection from Info.plist file to code signing setup script if `PRODUCT_BUNDLE_IDENTIFIER` is not resolved from build configuration.

Version 0.29.0
-------------

This release includes changes from [PR #244](https://github.com/codemagic-ci-cd/cli-tools/pull/244). The goal of this release is to migrate to [PEP 518](https://peps.python.org/pep-0518/) compliant build system by using [Poetry](https://python-poetry.org/) dependency management and packaging tool.

**Development**
- Migrate project dependency management from [Pipenv](https://pipenv.pypa.io/) to [Poetry](https://python-poetry.org/).
- Add `pyproject.toml` project file to specify dependencies, project packaging information and code style requirements. Flake8 configuration remains in `.flake8` as it does not support `pyproject.toml` yet.
- Changes to GitHub actions:
  - Update caching configuration.
  - Replace `pipenv` usages in GitHub action with Poetry.
- Changes to Codemagic workflows:
  - In `release` workflow run CI checks before building wheels and distribution. Use Poetry for building and PyPI releases.
  - Use Poetry in `test` workflow instead of Pipenv.
  - Define `release-test` workflow to build and release binary to [PyPI test mirror](https://test.pypi.org/).
- Project files `setup.cfg`, `setup.py`, `Pipfile` and `Pipfile.lock` were removed.
- Add `.pre-commit-config.yaml` which defines [`pre-commit`](https://pre-commit.com/) hooks.
- Move Ruby script `bin/code_signing_manager.rb` to `src/codemagic/scripts/code_signing_manager.rb`. This script will not be added to system `$PATH` at the time of package installation anymore. Consequence of this is that the action `xcode-project use-profiles` will now use the script which is bundled with installation, instead of what is available globally in the system.

**Docs**
- Update `README.md`:
  - update example code snippets that are out of date,
  - include all installed CLI tools to installed tools list,
  - add instructions for setting up development environment.

Version 0.28.0
-------------

This release includes changes and fixes from [PR #243](https://github.com/codemagic-ci-cd/cli-tools/pull/243).

**Bugfixes**
- Fix properties `not_after` and `not_before` of `codemagic.models.Certificate` to work with `pyOpenSSL` versions `<=19.1.0`.

**Development**
- Remove type stubs for package `cryptography`.
- Add tuple `SUPPORTED_PUBLIC_KEY_TYPES` to module `codemagic.models.private_key`.
- Remove [`OpenSSL.crypto.X509`](https://www.pyopenssl.org/en/stable/api/crypto.html?highlight=X509#x509-objects) usages from `codemagic.models.Certificate` internals by replacing them with functionality from [`cryptography.x509.Certificate`](https://cryptography.io/en/latest/x509/reference/#x-509-certificate-object).

Version 0.27.6
-------------

**Features**:
- Action `xcode-project run-tests` will now respect retried testcase outcome. In case the initial testcase execution fails, but retrying is turned on (by `-retry-tests-on-failure` Xcode testing flag) and subsequent testcase run turns out to be successful, then this testcase will not be considered as _failed_ in the context of whole test suite. [PR #242](https://github.com/codemagic-ci-cd/cli-tools/pull/242)

Version 0.27.5
-------------

**Dependencies**:
- Remove upper bound version limit `<37` from [`cryptography`](https://cryptography.io/) dependency, but exclude version [`37.0.0`](https://cryptography.io/en/latest/changelog/#v37-0-1) as it conflicts with `pyOpenSSL`. [PR #241](https://github.com/codemagic-ci-cd/cli-tools/pull/241)
- Remove upper bound version limit from [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) as all used functionality works also with recent versions. [PR #241](https://github.com/codemagic-ci-cd/cli-tools/pull/241)

Version 0.27.4
-------------

**Bugfixes**:
- Fix `ProvisioningProfile.application_identifier` property for profiles that list associated application identifiers. [PR #240](https://github.com/codemagic-ci-cd/cli-tools/pull/240)

Version 0.27.3
-------------

**Features**:
- Sanitize environment variable values in `altool` error logs when publishing to App Store Connect using `app-store-connect publish` fails. [PR #238](https://github.com/codemagic-ci-cd/cli-tools/pull/238)

**Bugfixes**:
- Fix handling invalid argument errors for grouped CLI arguments that are defined via environment variables. [PR #239](https://github.com/codemagic-ci-cd/cli-tools/pull/239)

Version 0.27.2
-------------

**Bugfixes**:
- Fix `AttributeError` that can occur on review submission creation error handling as part of action `app-store-connect builds submit-to-app-store`. [PR #236](https://github.com/codemagic-ci-cd/cli-tools/pull/236)

Version 0.27.1
-------------

**Development**
- Make type interface more strict for App Store Connect API client and resource definitions. [PR #221](https://github.com/codemagic-ci-cd/cli-tools/pull/221)
- Improve `ResourceManagerMixin` type interface. [PR #235](https://github.com/codemagic-ci-cd/cli-tools/pull/235)

**Bugfixes**:
- Fix `AttributeError` exceptions when constructing URLs for App Store Connect API requests to list certificates, certificate IDs, devices or device IDs for given `Profile` instance. [PR #221](https://github.com/codemagic-ci-cd/cli-tools/pull/221)

Version 0.27.0
-------------

**Fixes**
- Action `xcode-project use-profiles` failed to assign code signing information to build configurations that inherited build settings from `xcconfig` files. Reported in [issue #220](https://github.com/codemagic-ci-cd/cli-tools/issues/220). [PR #232](https://github.com/codemagic-ci-cd/cli-tools/pull/232)

**Development**
- Use default values for all arguments in `Keychain.add_certificates` and `XcodeProject.use_profiles`. [PR #226](https://github.com/codemagic-ci-cd/cli-tools/pull/226)

**Dependencies**
- Update [`PyJWT`](https://pyjwt.readthedocs.io/en/stable/) dependency minimum required version from `2.3.0` to `2.4.0`. [PR #231](https://github.com/codemagic-ci-cd/cli-tools/pull/231)

Version 0.26.0
-------------

This release includes changes from [PR #227](https://github.com/codemagic-ci-cd/cli-tools/pull/227).

Apple has deprecated the [Create an App Store Version Submission](https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version_submission) and replaced it by [Review Submissions](https://developer.apple.com/documentation/appstoreconnectapi/review_submissions) API. Changes included in this release update logic driving App Store publishing as part of actions `app-store-connect publish` and `app-store-connect builds submit-to-app-store`.

**Features**
- Add new action `app-store-connect review-submissions create` to create new review submission request for application's latest App Store Version.
- Add new action `app-store-connect review-submissions get` to show review submission information.
- Add new action `app-store-connect review-submission-items create` to add contents to review submission for App Store review request.
- Add new action `app-store-connect review-submissions confirm` to confirm pending review submission for App Review.
- Add new action `app-store-connect review-submissions cancel` to discard review submission from App Review.

**Development**
- **Breaking**: Return type for `AppStoreConnect.submit_to_app_store` changed. Instead of `AppStoreVersionSubmission` it now returns tuple `(ReviewSubmission, ReviewSubmissionItem)`.
- Add new resource manager properties `review_submissions` and `review_submissions_items` to `AppStoreConnectApiClient`.
- Update `AppStoreVersion` model with optional relationships `appClipDefaultExperience` and `appStoreVersionExperiments`.
- Define new `ReviewSubmissionState` and `ReviewSubmissionItemState` enumerations for App Store Connect API resources.
- Add model definition for resource [`ReviewSubmission`](https://developer.apple.com/documentation/appstoreconnectapi/reviewsubmission).
- Add model definition for resource [`ReviewSubmissionItem`](https://developer.apple.com/documentation/appstoreconnectapi/reviewsubmissionitem).
- Add method new methods to `AppStoreConnect`:
  - `cancel_review_submission`,
  - `confirm_review_submission`,
  - `create_review_submission`,
  - `create_review_submission_item`.


**Tests**
- Update mock for `AppStoreVersion` resource test.

**Docs**
- Add docs for app-store-connect `review-submission-items create`
- Add docs for app-store-connect `app-store-connect review-submissions cancel`
- Add docs for app-store-connect `app-store-connect review-submissions confirm`
- Add docs for app-store-connect `app-store-connect review-submissions create`
- Add docs for app-store-connect `app-store-connect review-submissions get`

Version 0.25.0
-------------

This release includes changes from [PR #224](https://github.com/codemagic-ci-cd/cli-tools/pull/224).

**Features**
- Add option `--archive-method` to action `xcode-project use-profiles` to limit code signing setup for specific profile type only. If archive method is not given, the action will attempt to use all profiles as it worked before.

**Development**
- **Breaking**: Definitions of enumeration base classes `ResourceEnum` and `ResourceEnumMeta` were moved from module `codemagic.apple.resources.enums` to `codemagic.models.enums`.
- `ArchiveMethod` enumeration parent class was changed from plain `enum.Enum` to `ResourceEnum`.
- `ArchiveMethod` class has new factory method `from_profile(profile: ProvisioningProfile)`.
- Method `XcodeProject.use_profiles` has new optional keyword argument `archive_method: Optional[ArchiveMethod] = None`.

**Docs**
- Update docs for action `xcode-project use-profiles`.

Version 0.24.3
-------------

**Improvements**
- Speed up `xcresult` parsing for `xcode-project` actions `run-tests`, `junit-test-results` and `test-summary`. [PR #223](https://github.com/codemagic-ci-cd/cli-tools/pull/223)

Version 0.24.2
-------------

**Fixes**
- Allow defining `distributionBundleIdentifier` export option by `--custom-export-options` for `xcode-project use-profiles`. [PR #218](https://github.com/codemagic-ci-cd/cli-tools/pull/218)

Version 0.24.1
-------------

**Dependencies**
- Add upper bound to [`cryptography`](https://cryptography.io/en/latest/) Python dependency (version `<37.0.0`) to persist compatibility with currently available `pyOpenSSL` version. [PR #217](https://github.com/codemagic-ci-cd/cli-tools/pull/217)

Version 0.24.0
-------------

Changes in this release improve usability of tool `google-play`. Updates are from [PR #215](https://github.com/codemagic-ci-cd/cli-tools/pull/215) and [PR #216](https://github.com/codemagic-ci-cd/cli-tools/pull/216).

**Breaking**

**None of the breaking changes have an effect on command line usage**, only the Python API of is affected.

- Method signature changes:
  - Signature of `GooglePlay` (tool `google-play`) initialization was changed:
    - positional argument `package_name` was removed,
    - keyword argument `log_requests` was removed,
    - keyword argument `json_output` was removed,
    - positional argument `credentials` accepts now Google Play service account credentials both as JSON `str` and parsed `dict`.
  - Signature of `GooglePlayDeveloperAPIClient` initialization was changed and simplified:
    - positional argument `resource_printer` was removed,
    - positional argument `package_name` was removed.
  - `GooglePlay` method `get_latest_build_number` requires `package_name` argument,
  - `GooglePlayDeveloperAPIClient` methods `create_edit` and `delete_edit` require `package_name` argument,
  - property `max_version_code` of `Track` was converted into a method `get_max_version_code()`.
- CLI argument definitions for `google-play` were updated and moved from `codemagic.tools.google_play` to `codemagic.tools.google_play.arguments`.
- Removed definitions:
  - enumeration `codemagic.google_play.resources.TrackName` was removed.
  - class `codemagic.google_play.ResourcePrinter` was removed.
  - exception `codemagic.google_play.VersionCodeFromTrackError` was removed.
  - removals in `GooglePlayDeveloperAPIClient`:
    - method `get_track_information` was removed,
    - property `service` was removed.

**Features**

- Update tool `google-play`:
  - Allow using custom release tracks with action `google-play get-latest-build-number`.
  - Add new action `google-play tracks get` to get information about specific release track for given package name.
  - Add new action `google-play tracks list` to get information about all available release tracks for given package name.

**Development**

- Module `codemagic.tools.google_play` was refactored by splitting single source file into a subpackage.
  - Define actions group `TracksActionGroup` for working with tracks.
  - Move `get_latest_build_number` action / method implementation into separate subclass `GetLatestBuildNumberAction`.
- Rework the internals of `GooglePlayDeveloperAPIClient`:
  - add context manager to handle `edit` lifecycle so that callers don't have to take care of deletion afterwards,
  - add new methods `get_track` and `list_tracks`,
  - service resource instance was removed from class instance as it wasn't thread safe.
- Update `mypy` version.
- Add more tests for `GooglePlay` tool.

**Docs**

- Update docs for tool `google-play`.
- Update docs for action `google-play get-latest-build-number`.
- Add docs for action group `google-play tracks`.
- Add docs for action `google-play tracks get`.
- Add docs for action `google-play tracks list`.

Version 0.23.1
-------------

**Fixes**
- Action `google-play get-latest-build-number` crashed when [`Track`](https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks) response from Google Play Developer API did not specify `includeRestOfWorld` field for [`CountryTargeting`](https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#countrytargeting). [PR #214](https://github.com/codemagic-ci-cd/cli-tools/pull/214)

Version 0.23.0
-------------

This release includes changes from [PR #213](https://github.com/codemagic-ci-cd/cli-tools/pull/213) to improve command line usage and Python client usability for managing Android keystores.

**Breaking**
- Remove key password option (specified by `-l`, `--ks-key-pass` or `--key-pass`) from action `android-keystore verify` as it is not used.

**Features**
- Add new action `android-keystore certificates` to list information about certificates included in the keystore.

**Development**
- **Breaking.** Remove `key_password` keyword argument from `AndroidKeystore.verify`.
- **Breaking.** Change signature of `Keytool.validate_keystore`. Instead of taking `keystore: Keystore` as the argument, now `keystore_path: pathlib.Path`, `keystore_password: str` and, `key_alias: str` are taken. Method functionality remains intact.
- Add new method `Keytool.get_certificates -> List[Certificate]` to extract certificates from specified android keystore.
- Add new convenience methods to `codemagic.models.Certificate`:
  - `get_summary() -> Dict` to generate JSON serializable dictionary containing information about the certificate.
  - `get_text_summary() -> str` that generates a printable and user-readable string representation of the certificate's information.

**Docs**
- Update documentation for tool `android-keystore`.
- Update documentation for action `android-keystore verify`.
- Add documentation for action `android-keystore certificates`.

Version 0.22.5
-------------

**Fixes**
- Return `True` from `Certificate.is_development_certificate` property if the certificate is _Mac Development_ code signing certificates, as those certificates are used to sign development versions of Mac apps. [PR #212](https://github.com/codemagic-ci-cd/cli-tools/pull/212)

Version 0.22.4
-------------

**Development**
- Add properties `creation_date` and `expiration_date` to `ProvisioningProfile` object. [PR #211](https://github.com/codemagic-ci-cd/cli-tools/pull/211)

Version 0.22.3
-------------

This is a bugfix release from [PR #210](https://github.com/codemagic-ci-cd/cli-tools/pull/210) to fix problems with tool `android-keystore` that was first added in [version 0.21.0](https://github.com/codemagic-ci-cd/cli-tools/releases/tag/v0.21.0).

**Improvements**
- Use better error message for keystore validation in case non-keystore file is passed for validation.

**Fixes**
- Fix debug keystore creation using action `android-keystore create-debug-keysotre`. It was using invalid keyword argument to specify keystore path.
- Make keystore path argument `--keystore` required for `android-keystore create` and `android-keystore verify` actions.

Version 0.22.2
-------------

This is a bugfix release from [PR #209](https://github.com/codemagic-ci-cd/cli-tools/pull/209).

**Fixes**
- Fix loading code signing entitlements from Xcode archives and iOS App Store Packages (`*.xcarchive` and `*.ipa` files respectively) with Xcode 13.3+. A tool called `codesign` which is bundled with Xcode is used to extract code signing entitlements information from application packages. The version of `codesign` included in Xcode 13.3 came with some modifications that broke the flow which is used to collect code signing entitlements.

Version 0.22.1
-------------

**Development**
- [PEP 561](https://www.python.org/dev/peps/pep-0561/) compliance. Include `py.typed` marker file to indicate that this package has inline type hints. [PR #207](https://github.com/codemagic-ci-cd/cli-tools/pull/207)

Version 0.21.0
-------------

This release contains updates from [PR #206](https://github.com/codemagic-ci-cd/cli-tools/pull/206).

**Features**
- Add new tool `android-keystore` to Android app code signing keystores. New actions are:
  - `android-keystore create` to initialize new Android keystore,
  - `android-keystore create-debug-keystore` to initialize new debug Android keystore with default settings,
  - `android-keystore verify` to check that Android keystore alias and passwords are correct.

**Development**
- Add optional `env` keyword argument to `CliProcess.execute` method to specify process specific environment variables.
- Add dataclass `CertificateAttributes` to store certificate issuer information.
- Add dataclass `Keystore` to store keystore information.
- Add new module `codemagic.shell_tools` to contain Python wrappers for command line utilities.
- Add minimal Python wrapper for `keytool` command line utility in `codemagic.shell_tools.Keytool`.


**Docs**
- Add documentation for tool `android-keystore`.
- Add documentation for action `android-keystore create`.
- Add documentation for action `android-keystore create-debug-keystore`.
- Add documentation for action `android-keystore verify`.

Version 0.20.0
-------------

This release contains improvements from [PR #205](https://github.com/codemagic-ci-cd/cli-tools/pull/205).

**Features**
- Add option `--p12-path` for `app-store-connect` actions `create-certificate` and `get-certificate` to specify PKCS#12 container save path that can be used together with `--save` to specify exact file path where the container is saved. It overrides default save location, which is configured by `--certificates-dir`.

**Fixes**
- Support certificates that do not have common name defined in subject.

**Development**
- Describe new common argument type `CommonArgumentType.non_existing_path` which asserts that specified file does not exist.
- PKCS#12 support in `pyOpenSSL` is deprecated and `cryptography` APIs should be used instead. Replace the deprecated `crypto.load_pkcs12` in `Certificate.from_p12` with `cryptography`'s `pkcs12.load_key_and_certificates`.
- Add new factory method `PricateKey.from_p12` to load private key from PKCS#12 container.
- Allow using `PrivateKey` instances for `AppStoreConnect` methods that take `certificate_key` argument. Before only instances of `Types.CertificateKeyArgument` were supported.
- Support `DSA` and elliptic curve private keys for `PrivateKey`.

Version 0.19.1
-------------

This is a bugfix release from [PR #204](https://github.com/codemagic-ci-cd/cli-tools/pull/204) to address the regression introduced in [PR #203](https://github.com/codemagic-ci-cd/cli-tools/pull/203).

**Fixes**
- Fix export options plist generation with `xcode-project use-profiles` in case provisioning profiles with wildcard identifiers (such as `*` or `com.example.*`) were used.

**Development**
- Add new data container class `ProvisioningProfileAssignment` which can be used to track the Xcode project target onto which certain provisioning profile was assigned to.
- Change `ExportOptions` factory method `from_used_profiles(cls, used_profiles: Sequence[ProvisioningProfile]) -> ExportOptions` to `from_profile_assignments(cls, profile_assignments: Sequence[ProvisioningProfileAssignment])`. This will persist the actual bundle identifiers of the Xcode targets when the property list constructed, instead of possibly using wildcard identifiers from provisioning profiles.

Version 0.19.0
-------------

This release includes changes from [PR #203](https://github.com/codemagic-ci-cd/cli-tools/pull/203) to improve usability and feedback from `xcode-project use-profiles`.

**Features**
- Improve `xcode-project use-profiles` log output. Highlight Xcode targets for which code signing settings were not configured, but are likely necessary for successful build.
- Add `--code-signing-setup-verbose-logging` option to action `xcode-project use-profiles` which turns on detailed log output for code signing settings configuration.

**Docs**
- Update docs for `xcode-project use-profiles` action. Add documentation for option `--code-signing-setup-verbose-logging`.

**Development**
- **Breaking.** Remove dataclass `codemagic.models.matched_profiles.MatchedProfile` and all its usages.
- **Breaking.** Replace `ExportOptions.from_matched_profiles` with `ExportOptions.from_used_profiles`. Old method was relying on the removed `MatchedProfile` class, while new method has more generic interface requiring only sequence of `ProvisioningProfiles` as arguments.
- **Breaking.** Change command line interface for `code_signing_manager.rb`:
  - Replace command line option `-u` / `--used-profiles` with `-r` / `--result-path` to better reflect the updated contents of result file.
  - Results saved into file specified by `--result-path` will now include all found Xcode targets, including those that were not assigned provisioning profile. The targets for which matching provisioning profile was found and configured, the reference also includes the used provisioning profile `uuid`.
  - The saved JSON file structure what used to be `{profile_uuid: [<target_info>, ...]}` is now `[<target_info>, ...]`.
- Always multiplex `code_signing_manager.rb` verbose log output to main file log.
- `CodeSigningManager.use_profiles` logs Xcode project targets for which provisioning profiles were not found, but are likely necessary for building `ipa`.

Version 0.18.1
-------------

**Fixes**
- Allow using `manageAppVersionAndBuildNumber` as an export option when building with `xcode-project build-ipa`. [PR #201](https://github.com/codemagic-ci-cd/cli-tools/pull/201)

Version 0.18.0
-------------

**Fixes**
- When creating new provisioning profiles as part of action `app-store-connect fetch-signing-files` include only eligible devices when creating the profiles. Before the action could fail for example in case when iOS development or Ad Hoc provisioning profile was created, but an Apple TV device was included as a create parameter. [PR #200](https://github.com/codemagic-ci-cd/cli-tools/pull/200)

**Features**
- Change default behaviour for resolving certificate type from provisioning profile type. Map `IOS_APP_ADHOC` provisioning profile type to `DISTRIBUTION` certificate type instead of `IOS_DISTRIBUTION`. "Apple Distribution" certificates can be used to sign any type of application (iOS, tvOS, Mac, Universal, etc.) and as a result fewer certificates are required. Applies to the following actions:
  - `app-store-connect fetch-signing-files`,
  - `app-store-connect list-certificates`.

  This change is backwards compatible in the sense that existing matching `IOS_DISTRIBUTION` certificates are still used for `IOS_APP_ADHOC` provisioning profiles if found. [PR #198](https://github.com/codemagic-ci-cd/cli-tools/pull/198)

**Development**
- Behaviour of `CertificateType.from_profile_type` was changed:
  - calling it with `ProfileType.IOS_APP_STORE` returns `CertificateType.DISTRIBUTION` instead of `CertificateType.IOS_DISTRIBUTION` as before. [PR #198](https://github.com/codemagic-ci-cd/cli-tools/pull/198)

Version 0.17.2
-------------

This is a bugfix release to fix the regression introduced in v0.17.1.

**Fixes**
- Consider OpenSSH private keys for `app-store-connect` argument `--certificate-key` valid again. Due to changes in [PR #196](https://github.com/codemagic-ci-cd/cli-tools/pull/196) only PEM encoded keys were accepted as certificate keys, but OpenSSH keys are not fully compatible with the PEM standard, and should be allowed too. [PR #197](https://github.com/codemagic-ci-cd/cli-tools/pull/197)

Version 0.17.1
-------------

**Fixes**
- Validate that App Store Connect API private key specified for `app-store-connect` tool by argument `--private-key` is a valid PEM encoded key. [PR #196](https://github.com/codemagic-ci-cd/cli-tools/pull/196)

Version 0.17.0
-------------

**Features**
- When retrying `altool` commands as part of `app-store-connect publish` action, kill open Xcode processes before another attempt is made. It is applicable only if the action is launched in CI environment (environment variable `CI` is set to _truthy_ value). [PR #192](https://github.com/codemagic-ci-cd/cli-tools/pull/192)

**Fixes**
- Value of test output directory, specified by argument `--output-dir`, for actions [`xcode-project junit-test-results`](https://github.com/codemagic-ci-cd/cli-tools/blob/v0.16.1/docs/xcode-project/junit-test-results.md#junit-test-results) and [`xcode-project run-tests`](https://github.com/codemagic-ci-cd/cli-tools/blob/v0.16.1/docs/xcode-project/run-tests.md#run-tests) had to point to existing directory, which is too restrictive. Change it so that the specified test output directory can be either created, or it has to exist. File paths are still considered to be invalid inputs. [PR #191](https://github.com/codemagic-ci-cd/cli-tools/pull/191)
- Fix default test destination for `xcode-project run-tests` when tests are run for macOS SDK. Omit test destination for these cases as the tests will be launched on the host machine directly. Otherwise, the default simulator obtained by [`xcode-project default-test-destination`](https://github.com/codemagic-ci-cd/cli-tools/blob/v0.16.1/docs/xcode-project/default-test-destination.md) is still used as before if no devices are specified. [PR #191](https://github.com/codemagic-ci-cd/cli-tools/pull/191)

**Docs**
- Apply bold style to Markdown docs that are shown using ANSI bold in terminal help messages. [PR #190](https://github.com/codemagic-ci-cd/cli-tools/pull/190)
- Apply pre style to Markdown docs that are shown in bright blue color in terminal help messages. [PR #190](https://github.com/codemagic-ci-cd/cli-tools/pull/190)
- Update docs for `xcode-project run-tests` action. [PR #191](https://github.com/codemagic-ci-cd/cli-tools/pull/191)

**Development**
- Add function `codemagic.cli.environment.is_ci_environment() -> bool` which checks whether current process is being run in a CI environment. Check is being performed based on the value of `CI` environment variable. [PR #192](https://github.com/codemagic-ci-cd/cli-tools/pull/192)

**Dependencies**
- Add [`psutil`](https://pypi.org/project/psutil/) Python dependency (version `5.8.0+`) to manage ongoing system processes in a platform-agnostic way. [PR #192](https://github.com/codemagic-ci-cd/cli-tools/pull/192)
- Bumps `pipenv` dependency from version `2021.11.23` to `2022.1.8` (development only). [PR #193](https://github.com/codemagic-ci-cd/cli-tools/pull/193)

Version 0.16.1
-------------

**Fixes**
- Revoke cached App Store Connect API JSON web token when unauthorized request retry attempts are exhausted. [PR #188](https://github.com/codemagic-ci-cd/cli-tools/pull/188)

**Development**
- Log for which App Store Connect API key JWT is generated or loaded from disk cache. [PR #188](https://github.com/codemagic-ci-cd/cli-tools/pull/188)
- Remove `reset_token` parameter from `AppStoreConnectApiClient.generate_auth_headers`. [PR #188](https://github.com/codemagic-ci-cd/cli-tools/pull/188)
- Add optional `revoke_auth_info: Callable[[], None]` parameter to `AppStoreConnectApiSession` to reset App Store Connect API authentication information in case of unauthorized requests. [PR #188](https://github.com/codemagic-ci-cd/cli-tools/pull/188)

Version 0.16.0
-------------

**Features**
- Change default behaviour for resolving certificate type from provisioning profile type. Map both `IOS_APP_STORE` and `MAC_APP_STORE` provisioning profile types to `DISTRIBUTION` certificate type instead of the old approach where `IOS_DISTRIBUTION` and `MAC_APP_DISTRIBUTION` certificate types were used respectively. "Apple Distribution" certificates can be used to sign any type of application (iOS, tvOS, Mac, Universal, etc.) and as a result fewer certificates are required. Applies to the following actions:
  - `app-store-connect fetch-signing-files`,
  - `app-store-connect list-certificates`.

  This change is backwards compatible in the sense that existing matching `IOS_DISTRIBUTION` and `MAC_APP_DISTRIBUTION` certificates are still used for `IOS_APP_STORE` and `MAC_APP_STORE` provisioning profiles if found. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)
- Unify formatting for signing certificates, profiles and bundle IDs in `app-store-connect fetch-signing-files` log output. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)
- Multiple `--type` arguments are now supported for `app-store-connect list-certificates` action. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)
- When either signing certificate or provisioning profile is saved to disk (for example as part of `app-store-connect fetch-signing-files`), then the save path will include resource ID and type, which makes it possible to easily match process output to file on disk. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)

**Dependencies**
- Update required [PyJWT](https://pyjwt.readthedocs.io/en/stable/index.html) version from `2.0.0` to `2.3.0`.  [#186](https://github.com/codemagic-ci-cd/cli-tools/pull/186)

**Development**
- Behaviour of `CertificateType.from_profile_type` was changed:
  - calling it with `ProfileType.IOS_APP_STORE` returns `CertificateType.DISTRIBUTION` instead of `CertificateType.IOS_DISTRIBUTION` as before,
  - and calling it with `ProfileType.MAC_APP_STORE` returns `CertificateType.DISTRIBUTION` instead of `CertificateType.MAC_APP_DISTRIBUTION`. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)
- Signature of `AppStoreConnect.list_certificates` was updated. Method argument `certificate_type: Optional[CertificateType] = None` was deprecated and replaced by `certificate_types: Optional[Union[CertificateType, Sequence[CertificateType]]] = None`. This change is fully backwards compatible in the sense that as of now both the positional usage of the argument still works, and `certificate_type` can still also be used as a keyword argument. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)

**Docs**
- Update documentation for `app-store-connect list-certificates` to reflect the possibility of multiple `--type` arguments. [PR #185](https://github.com/codemagic-ci-cd/cli-tools/pull/185)

Version 0.15.0
-------------

**Features**
- Add `--api-unauthorized-retries` option to `app-store-connect` actions to gracefully handle invalid `401 Unauthorized` responses from App Store Connect API. In case HTTP request to App Store Connect API fails with authentication error, generate new JSON Web Token, and try to do the request again until retries are exhausted. Retry count default to `3` for CLI invocations. [PR #178](https://github.com/codemagic-ci-cd/cli-tools/pull/178)
- Improve error messages for CLI invocations in case invalid value is provided to CLI argument that can be specified using an environment variable. [PR #180](https://github.com/codemagic-ci-cd/cli-tools/pull/180)
- Add option to cache App Store Connect JSON Web Token to disk so that the same token could be reused between subsequent `app-store-connect` command invocations to avoid false positive authentication errors from App Store Connect API. [PR #181](https://github.com/codemagic-ci-cd/cli-tools/pull/181)
- All `app-store-connect` actions have new option `--disable-jwt-cache` to turn off caching App Store Connect JWT to disk. The default behaviour is to have disk cache enabled. That is JWT is loaded from disk if present and not expired, and generated tokens are cached to disk unless this feature is turned off. [PR #181](https://github.com/codemagic-ci-cd/cli-tools/pull/181)

**Development**
- `AppStoreConnect`, `AppStoreConnectApiClient` and `AppStoreConnectApiSession` classes take new optional keyword argument `unauthorized_request_retries` which defines how many times request with unauthorized response should be retried. [PR #178](https://github.com/codemagic-ci-cd/cli-tools/pull/178)
- Use custom abstract metaclass for `TypedCliArgument` that enables class name transformation during CLI argument parsing. Pretty class name can be defined using `type_name_in_argparse_error` attribute on classes that inherit from `TypedCliArgument`. In case pretty name is not defined, then basic types are mapped to string representation, and otherwise `CamelCase` names are converted `camel case`. [PR #180](https://github.com/codemagic-ci-cd/cli-tools/pull/180)
- Extract logic that deals with App Store Connect JWT generation and lifespan from `AppStoreConnectApiClient` to standalone `JsonWebTokenManager` class. [PR #181](https://github.com/codemagic-ci-cd/cli-tools/pull/181)
- `AppStoreConnect` and `AppStoreConnectApiClient` classes take new optional keyword argument `enable_jwt_cache` which configures whether the JSON web token is cached to file or not. [PR #181](https://github.com/codemagic-ci-cd/cli-tools/pull/181)

**Docs**
- Update docs for `app-store-connect` actions and include information about `--api-unauthorized-retries` option. [PR #179](https://github.com/codemagic-ci-cd/cli-tools/pull/179)
- Update docs for `app-store-connect` actions and include information about `--disable-jwt-cache` option. [PR #183](https://github.com/codemagic-ci-cd/cli-tools/pull/183)

Version 0.14.1
-------------

**Fixes**
- In case updating or creating localized App Store version meta information fails for any of the provided languages, do not fail the calling action, but log the error instead. Has an effect on `app-store-connect publish` and `app-store-connect builds submit-to-app-store`. [PR #175](https://github.com/codemagic-ci-cd/cli-tools/pull/175)

Version 0.14.0
-------------

**Deprecations**
- Option `--skip-package-validation` of `app-store-connect publish` is ignored and shows a deprecation warning. [PR #174](https://github.com/codemagic-ci-cd/cli-tools/pull/174)

**Features**
- Change `app-store-connect publish` not to run package validation by default before uploading it to App Store Connect. [PR #174](https://github.com/codemagic-ci-cd/cli-tools/pull/174)
- Add new option `--enable-package-validation` to action `app-store-connect publish` that turns on package validation before it is uploaded to App Store Connect. [PR #174](https://github.com/codemagic-ci-cd/cli-tools/pull/174)

Version 0.13.2
-------------

**Features**
- Improve error messages for CLI invocations in case invalid value was provided for argument with `Enum` type. [PR #170](https://github.com/codemagic-ci-cd/cli-tools/pull/170)

**Fixes**

- Use correct package type for `altool` commands when publishing tvOS apps using `app-store-connect publish`. [PR #173](https://github.com/codemagic-ci-cd/cli-tools/pull/173)

Version 0.13.1
-------------

This is an enhancement release to further streamline the App Store review submission automation capabilities.

Additions and changes from [pull request #172](https://github.com/codemagic-ci-cd/cli-tools/pull/172).

**Features**
- Support setting localized meta information for App Store versions when submitting build to App Store review.
- Add new actions group `app-store-version-localizations` to `app-store-connect`.
- Add new action `app-store-connect app-store-version-localizations create` to add localized metadata to an App Store version.
- Add new action `app-store-connect app-store-version-localizations delete` to remove localized metadata from an App Store version.
- Add new action `app-store-connect app-store-version-localizations get` to read App Store version localized metadata.
- Add new action `app-store-connect app-store-version-localizations modify` to edit App Store version localized metadata.
- Add new action `app-store-connect app-store-versions localizations` to list App Store version localizations for an App Store version.
- Change `app-store-connect publish` to support adding or updating localized version metadata when submitting build to App Store review.
- Change `app-store-connect builds submit-to-app-store` to support adding or updating localized version metadata for App Store version.
- Add new App Store Connect API client method `AppStoreVersionLocalizations.create` to create App Store version localization meta information. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version_localization).
- Add new App Store Connect API client method `AppStoreVersionLocalizations.read` to obtain App Store version localization meta information. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/read_app_store_version_localization_information).
- Add new App Store Connect API client method `AppStoreVersionLocalizations.modify` to edit existing App Store version localization meta information. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/modify_an_app_store_version_localization).
- Add new App Store Connect API client method `AppStoreVersionLocalizations.delete` to remove existing App Store version localization meta information. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version_localization).
- Add new App Store Connect API client method `AppStoreVersions.list_app_store_version_localizations` to list all App Store version localizations for given App Store version. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/list_all_app_store_version_localizations_for_an_app_store_version).
- Show more informative error messages in case CLI arguments from environment variables or files are invalid.
- Add new options to actions `app-store-connect publish` and `app-store-connect builds submit-to-app-store`:
  - `--app-store-version-info`,
  - `--description`,
  - `--keywords`,
  - `--marketing-url`,
  - `--promotional-text`,
  - `--support-url`,
  - `--app-store-version-localizations`.

**Docs**

- Create docs for `app-store-connect` actions group `app-store-version-localizations`.
- Create docs for action `app-store-connect app-store-version-localizations create`.
- Create docs for action `app-store-connect app-store-version-localizations delete`.
- Create docs for action `app-store-connect app-store-version-localizations get`.
- Create docs for action `app-store-connect app-store-version-localizations modify`.
- Update docs for `app-store-connect` actions group `app-store-versions`.
- Create docs for action `app-store-connect app-store-versions localizations`.
- Update docs for action `app-store-connect app-store-versions create`.
- Update docs for action `app-store-connect app-store-versions modify`.
- Update docs for action `app-store-connect builds submit-to-app-store`.
- Update docs for action `app-store-connect publish`.
- Remove backticks from terminal help messages and keep them only for markdown documentation formatting.

**Development**

- Add option to limit number of responses in App Store Connect API client pagination method.
- Change type of `App.Attributes.locale` from plain `str` to `Locale` enumeration.
- Add definition for `AppStoreVersionLocalization` resource. See official resource [documentation](https://developer.apple.com/documentation/appstoreconnectapi/appstoreversionlocalization).
- Reorder method signatures in `AbstractBaseAction` and unify indentation for method arguments.
- Add references to implementing methods to `AbstractBaseAction` interface.

Version 0.13.0
-------------

Additions and changes from [pull request #164](https://github.com/codemagic-ci-cd/cli-tools/pull/164).

**Features**

- Add new App Store Connect API client method `AppStoreVersions.create` to create an App Store version. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/create_an_app_store_version).
- Add new App Store Connect API client method `AppStoreVersions.read_build` to read associated build from an App Store version. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/read_the_build_information_of_an_app_store_version).
- Add new App Store Connect API client method `AppStoreVersions.read_app_store_version_submission` to read associated App Store version submission from an App Store version. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/read_the_app_store_version_submission_information_of_an_app_store_version).
- Add new App Store Connect API client method `AppStoreVersions.modify` to edit existing App Store version details. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/modify_an_app_store_version).
- Add new App Store Connect API client method `AppStoreVersions.delete` to delete an App Store version. See official API method [documentation](https://developer.apple.com/documentation/appstoreconnectapi/delete_an_app_store_version).
- Add ability to group optional CLI action arguments into named argument groups.
- Add new actions group `app-store-versions` to `app-store-connect`.
- Add new action `app-store-connect app-store-versions create` to create a new App Store version using specified build to an app.
- Add new action `app-store-connect app-store-versions modify` to update existing App Store version details.
- Add new action `app-store-connect app-store-versions delete` to remove App Store version.
- Add option to specify build filters for action `app-store-connect apps builds`.
- Add new action `app-store-connect builds app-store-version` to get the App Store version of a specific build.
- Add new action `app-store-connect builds submit-to-app-store` to submit specified build to App Store review. Optionally specify version details and release type.
- Update `app-store-connect publish` action to allow automatic App Store review submission after binary upload.
- Use grouped CLI arguments in action `app-store-connect publish` for better help messages and documentation.
- Add new option `--skip-package-upload` to `app-store-connect publish`.
- Add short aliases for CLI flags:
  - `-su` for `--skip-package-upload`,
  - `-sv` for `--skip-package-validation`,
  - `-w` for `--max-build-processing-wait`.

**Fixes**

- Fix creating `Resource` objects that do not have any attributes.
- Fix `--max-build-processing-wait` CLI option validation.
- Allow non-integer version numbers for `--build-version-number`.

**Docs**

- Update docs for tool `app-store-connect`.
- Create docs for `app-store-connect` actions group `app-store-versions`.
- Create docs for action `app-store-connect app-store-versions create`.
- Create docs for action `app-store-connect app-store-versions delete`.
- Create docs for action `app-store-connect app-store-versions modify`.
- Create docs for `app-store-connect` actions group `apps`.
- Update docs for action `app-store-connect apps app-store-versions`.
- Update docs for action `app-store-connect apps builds`.
- Update docs for action `app-store-connect apps list`.
- Create docs for `app-store-connect` actions group `builds`.
- Create docs for action `app-store-connect builds app-store-version`.
- Create docs for action `app-store-connect builds submit-to-app-store`.
- Update docs for action `app-store-connect builds submit-to-testflight`.
- Update docs for action `app-store-connect list-builds`.
- Update docs for action `app-store-connect publish`.

**Development**

- Support filtering by multiple values for one parameter in `ResourceManager.filter`.
- Change `ResourceManager._get_update_payload` to accept `relationships` in addition to `attributes`. Make `attributes` and `relationships` arguments keyword-only.
- Add missing return type hints to resource manger methods that did not have them.
- Extract argument parser setup from `CliApp` class into separate module under `ArgumentParserBuilder` class.
- Move `create_app_store_version_submission` and `delete_app_store_version_submission` methods from `AppStoreConnect` class to `AppStoreVersionSubmissionsActionGroup`.
- Collect `app-store-connect` actions arguments that are used number of times under argument groups to reduce duplication.
- Refactor `PublishAction` class:
  - extract `publish` action arguments validation into separate method,
  - move decorator arguments into separate tuple,
  - add dataclasses for subaction options,
  - support App Store review submission.

Version 0.12.1
-------------

**Fixes**

- Show appropriate error messages when invalid values are passed to CLI actions using environment variables. [PR #168](https://github.com/codemagic-ci-cd/cli-tools/pull/168)

Version 0.12.0
-------------

**Breaking**

- Action `app-store-connect publish` option `--verbose-altool-logging` was renamed to `--altool-verbose-logging`. Corresponding environment variable configuration options was also changed from `APP_STORE_CONNECT_VERBOSE_ALTOOL_LOGGING` to `APP_STORE_CONNECT_ALTOOL_VERBOSE_LOGGING`. [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)
- Python API for `AppStoreConnect.publish` was changed: keyword argument `verbose_altool_logging` was renamed to `altool_verbose_logging`. [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)

**Features**

- Action `app-store-connect pubish` will now retry package validation and upload in case of some known errors (authentication failure, timeout) for configured amount of time. [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)
- Add new option `--altool-retries` to action `app-store-connect pubish` to configure how many times `altool` action will be retried on known flaky error. [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)
- Add new option `--altool-retry-wait` to action `app-store-connect pubish` to configure wait duration in seconds between `altool` action retries. [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)

**Development / Docs**

- Do not use line wrapping when generating docs (new feature in [`mdutils` version 1.3.1](https://github.com/didix21/mdutils/blob/master/CHANGELOG.md#v131-2021-07-10)). [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)
- Generate new docs for action `app-store-connect publish`. [PR #163](https://github.com/codemagic-ci-cd/cli-tools/pull/163)

Version 0.11.4
-------------

**Fixes**

- Fix decoding undefined byte sequences while processing subprocess streams. [PR #162](https://github.com/codemagic-ci-cd/cli-tools/pull/162)

Version 0.11.3
-------------

**Features**

- Add switch to use verbose logging for `altool` subcommands that are executed as part of `app-store-connect publish`. [PR #160](https://github.com/codemagic-ci-cd/cli-tools/pull/160)

**Development / Docs**

- Update `app-store-connect publish` action docs. [PR #160](https://github.com/codemagic-ci-cd/cli-tools/pull/160)

Version 0.11.2
-------------

**Fixes**

- Add validation for export options plist path on `xcode-project build-ipa` action. Handle missing files and invalid property list files gracefully [PR #155](https://github.com/codemagic-ci-cd/cli-tools/pull/155).

**Features**

- Support running subprocesses on Windows. [PR #156](https://github.com/codemagic-ci-cd/cli-tools/pull/156)
- Capture logs from subprocesses on Windows. [PR #156](https://github.com/codemagic-ci-cd/cli-tools/pull/156)

**Development / Docs**

- Do not import `fcntl` module globally in order to support Windows platform. [PR #156](https://github.com/codemagic-ci-cd/cli-tools/pull/156)
- Create `CliProcessStream` abstraction layer to handle streams on both POSIX and Windows. [PR #156](https://github.com/codemagic-ci-cd/cli-tools/pull/156)

Version 0.11.1
-------------

**Features**

- Show unformatted Xcode build errors on `xcode-project build-ipa` invocations that fail due to errors on `xcodebuild archive`. [PR #153](https://github.com/codemagic-ci-cd/cli-tools/pull/153).

**Development / Docs**

- Add a generator `codemagic.utilities.backwards_file_reader.iter_backwards` that returns the lines of a file in reverse order. [PR #153](https://github.com/codemagic-ci-cd/cli-tools/pull/153).

Version 0.11.0
-------------

**Features**

- New `app-store-connect register-device` action to add new device to Apple Developer team. Registering a device allows creating a provisioning profile for app testing and ad hoc distribution.

**Development / Docs**

- Rename `DeviceArgument.DEVICE_NAME` CLI argument to `DeviceArgument.DEVICE_NAME_OPTIONAL`.
- Update docs for action `app-store-connect beta-groups add-build`.
- Update docs for action `app-store-connect beta-groups remove-build`.
- Update docs for action `app-store-connect list-devices`.
- Add docs for action `app-store-connect register-device`.

Version 0.10.3
-------------

**Development / Docs**

- Add `get_fingerprint` method to `codemagic.models.Certificate` class which returns certificate's hexadecimal fingerprint for requested hashing algorithm.

Version 0.10.2
-------------

**Fixes**

- Make `codemagic.apple.resources.App` relationship for `ciProduct` optional.

Version 0.10.1
-------------

**Fixes**

- Fix `codemagic.models.application_package.Ipa` initialization for packages that are compressed using [`LZFSE`](https://github.com/lzfse/lzfse) compression algorithm. Fix requires `unzip` to be available in system `$PATH`.

Version 0.10.0
-------------

**Features**

- New `app-store-connect beta-groups` action set to add and remove TestFlight builds from groups of beta testers.
- `app-store-connect publish` action accepts multiple Beta group names under `--beta-group` key. The uploaded TestFlight build will be made available to the specified groups of beta testers.

**Development / Docs**

- Update `app-store-connect publish` action docs.

Version 0.9.8
-------------

**Fixes**

- Fail action `app-store-connect builds subtmit-to-testflight` properly using error handling in case the application is missing required test information in App Store Connect.
- Support `links` field in App Store Connect API [error responses](https://developer.apple.com/documentation/appstoreconnectapi/errorresponse/errors).

Version 0.9.7
-------------

**Improvements**

- Accept list of `BetaBuildInfo` objects as `beta_build_localizations` argument for `AppStoreConnect.add_beta_test_info` using Python API.

Version 0.9.6
-------------

**Improvements**

- Add new action `add-beta-test-info` to submit What's new (What to test) localized information for a beta build.
- Add new action `submit-to-testflight` to submit beta build to TestFlight.
- Introduce strict with match with `--strict-match-identifier` keyword when listing applications filtered by Bundle ID.
- Avoid waiting for processed build when `MAX_BUILD_PROCESSING_WAIT` or `--max-build-processing-wait` is set to 0.

**Development**

- `publish` command will now rely on `add-beta-test-info` and `submit-to-testflight` tasks.
- Add `read_with_include` for Builds to return an application along with a build.

Version 0.9.5
-------------

**Improvements**

- Add missing `submittedDate` to Beta App Review Submission attributes

**Fixes**

- Ignore undefined model attributes in App Store Connect API responses instead of failing with `TypeError`.
- Fix finding uploaded build as part of `app-store-connect publish`.
- Fix `app-store-connect apps builds` action by replacing broken [List All Builds of an App
](https://developer.apple.com/documentation/appstoreconnectapi/list_all_builds_of_an_app) API endpoint by [List Builds
](https://developer.apple.com/documentation/appstoreconnectapi/list_builds) endpoint.

**Development / Docs**

- Add warning to method `list_builds` in `Apps` resource manager about malfunctioning pagination.
- Add missing relationship `ciProduct` to `App` model.
- Accept strings for builds filter version restriction.

Version 0.9.4
-------------

**Fixes**

- Fix custom export option usage on `xcode-project use-profiles --custom-export-options`. Replace faulty argument unpacking usage with plain dictionary updates and iteration.

Version 0.9.3
-------------

**Improvements**

- Double the number of attempts to find an uploaded build on App Store Connect side

Version 0.9.2
-------------

**Improvements**

- Require API key based authentication for `app-store-connect publish` when `--beta-build-localizations` is used.

Version 0.9.1
-------------

**Features**

- Add action `codemagic-cli-tools installed-tools` to show the tools that are installed by current Codemagic CLI tools version.
- Add action `codemagic-cli-tools version` to show version of currently installed Codemagic CLI tools.

**Development / Docs**

- Create keychains in `~/Library/codemagic-cli-tools/keychains` by default when `--path` is not specified with `keychain initialize`.
- Add docs for new actions from tool `codemagic-cli-tools`.
- Fix typos in CLI arguments help messages/docs that can be specified using `@env:` or `@file:` prefixes.

Version 0.9.0
-------------

**Features**

- Add action `keychain use-login` to make login keychain from `~/Library/Keychains` system default keychain again.

**Improvements**

- Save new keychain to `~/Library/Keychains/codemagic-cli-tools` instead of `$TMPDIR` by default with `keychain initialize` in case the `--path` option is not specified.

**Development / Docs**

- Add docs for action `keychain use-login`.

Version 0.8.5
-------------

**Features**

- Make `--whats-new` option independent of `--testflight` for `app-store-connect publish` since submission to external beta review is not necessary to specify notes.
- Make App Store Connect application entry default locale detection more robust by using `primaryLocale` attribute instead of using the first `betaAppLocalization` for that app.
- Show more descriptive error messages for invalid inputs to CLI arguments that can be defined using `@env:<var_name>` and `@file:<file_path>` notations.
- Add more blue and green colors to logs to indicate the start of an activity and completion of it.

**Development / Docs**

- Allow `str` input for `whats_new` arguments to actions defined in `BetaBuildLocalizationsActionGroup`.
- Remove obsolete test which verified that `--whats-new` could only be used together with `--testflight`.
- Update `app-store-connect publish` action docs.

Version 0.8.4
-------------

**Features**

- Remove default value from `--locale` option for actions `app-store-connect beta-build-localizations create` and `app-store-connect publish`. In case it is not provided, resolve the default locale value from related application's primary test information.
- Make `app-store-connect beta-build-localizations create` more forgiving and allow the cases when beta build localization already exists for the locale. On such occasions just update the resource.

**Development / Docs**

- Update `app-store-connect publish` action docs.
- Update `app-store-connect beta-build-localizations create` action docs.
- Do not use runtime enum definition generation during argument parsing.
- Fix error messages for invalid enumeration values.
- Update [requests](https://docs.python-requests.org/en/master/) dependency requirement from version 2.22.0 to 2.25.1.

Version 0.8.3
-------------

**Features**

- Check if application has complete test information in App Store Connect before submitting a build for external testing with `app-store-connect publish --testflight`. This will enable the submission to fail fast with descriptive message instead of waiting until build processing completes by Apple and only then failing while creating the TestFlight submission.
- Add `--max-build-processing-wait` option to configure maximum time that `app-store-connect publish` will wait for the package to be processed before failing the TestFlight submission.
- Improve error message when waiting for package to be processed times out during TestFlight submission as part of `app-store-connect publish`.

**Development / Docs**

- Get build and related resources using App Store Connect API client directly for `app-store-connect publish` instead of reusing other `app-store-connect` actions to reduce unnecessary repetition in the terminal output.
- Extract application lookup into a separate method for finding uploaded build.
- Define new models for Apple API resources: `BetaAppLocalization` and `BetaAppReviewDetail`.
- Implement new App Store Connect API client methods to consume endpoints to [list beta app Localizations of an app](https://developer.apple.com/documentation/appstoreconnectapi/list_all_beta_app_localizations_of_an_app) and to [read the beta app review details of an app](https://developer.apple.com/documentation/appstoreconnectapi/read_the_beta_app_review_details_resource_of_an_app).
- Show default values for arguments of type `TypedCliArgument`.
- Add documentation for action `app-store-connect builds get`.
- Document `--max-build-processing-wait` option in `app-store-connect publish` action.
- Show default values for arguments of type `TypedCliArgument`.
- Show the long version of CLI flag first in help messages and online documentation to reduce ambiguity. For example use `--testflight` instead of `-t` in help messages.

Version 0.8.2
-------------

**Improvements**

- Explicitly mention "certificate" in `app-store-connect` error messages when `--certificate-key` is missing to avoid confusion with App Store Connect API key `--private-key`.

Version 0.8.1
-------------

**Fixes**

- Submit only uploaded iOS application packages (`*.ipa` files) to TestFlight from `app-store-connect publish` action when submission to Testflight is enabled by `--testflight` flag.

Version 0.8.0
-------------

**Features**

- Add option to submit "What's new" information along with Testflight build via `--locale` and `--whats-new` arguments in `app-store-connect publish` command.
- Add a set of actions for managing "What's new" information for Testflight builds `app-store-connect beta-build-localizations`
- Add action `app-store-connect beta-build-localizations create` to create localized "What's new" notes for a given beta build
- Add action `app-store-connect beta-build-localizations delete` to delete localized "What's new" notes by its ID
- Add action `app-store-connect beta-build-localizations modify` to update "What's new" content by its ID
- Add action `app-store-connect beta-build-localizations list` to list localized "What's new" notes filtered by Build ID and locale code
- Add action `app-store-connect beta-build-localizations get` to retrieve localized "What's new" notes by its ID

Version 0.7.7
-------------

**Fixes**

- Before creating Beta App Review Submission (submitting build to TestFlight) as part of `app-store-connect publish`, wait until the uploaded build processing completes.

Version 0.7.6
-------------

**Fixes**

- Make `altool` output parsing less strict. Do not fail `app-store-connect publish` action invocation if `altool` output cannot be interpreted.

Version 0.7.5
-------------

**Features**

- Add option to skip package validation for action `app-store-connect publish` with `--skip-package-validation` flag. This allows to opt out from running `altool --validate-app` before actual upload.

**Development / Docs**

- Update `app-store-connect publish` action docs to reflect new option `--skip-package-validation`.

Version 0.7.4
-------------

**Fixes**

- Do not fail actions `app-store-connect get-latest-app-store-build-number` and `app-store-connect get-latest-testflight-build-number` in case no builds were found for specified constraints.

**Development / Docs**

- Split monolith`AppStoreConnect` tool tests file into smaller chunks in separate test module.

Version 0.7.3
-------------

**Fixes**

- Do not require App Store Connect API keys for `app-store-connect publish` unless `--testflight` option is specified as binary upload can be done with Apple ID and App Specific password only.

Version 0.7.2
-------------

**Fixes**

- Support non-integer (dot-separated versions such as 10.14.1) version codes for `app-store-connect get-latest-app-store-build-number` and `app-store-connect get-latest-testflight-build-number`.

Version 0.7.1
-------------

**Fixes**

- Ignore undefined model relationships in App Store Connect API responses instead of failing with `TypeError`.
- Dynamically generate enumerations for undefined values from App Store Connect API responses instead of failing with `ValueError`.

**Development / Docs**

- Make `SignignCertificate` model relationship `passTypeId` optional.

Version 0.7.0
-------------

**New features**

- Add action `app-store-connect apps get` to get information about a specific app.
- Add action `app-store-connect apps list` to find apps added in App Store Connect.
- Add action `app-store-connect apps app-store-versions` to find App Store versions associated with a specific app.
- Add action `app-store-connect apps builds` to find builds associated with a specific app.
- Add action `app-store-connect apps pre-release-versions` to find prerelease versions associated with a specific app.
- Add action `app-store-connect beta-app-review-submissions create` to submit an app for beta app review to allow external testing.
- Add action `app-store-connect beta-app-review-submissions list` to find beta app review submissions of a build.
- Add action `app-store-connect builds pre-release-version` to find the prerelease version for a specific build
- Add action `app-store-connect publish` to upload application packages to App Store and submit them to Testflight.
- Add action `xcode-project ipa-info` to show information about iOS App Store Package file.
- Add action `xcode-project pkg-info` to show information about macOS Application Package file.
- Support loading App Store Connect API key from disk using key identifier by checking predefined locations `./private_keys`, `~/private_keys`, `~/.private_keys`, `~/.appstoreconnect/private_keys` for file `AuthKey_<key_identifier>.p8`.
- Add Python wrapper to Apple's Application Loader tool and use it to publish application packages to App Store Connect.

**Fixes**

- Handle missing action for action group on command invocation.
- Fix initializing provisioning profiles from in-memory content.

**Development / Docs**

- Improve modularity by adding support to define tool actions and action groups in separate modules.
- Support strings as path argument for `Certificate.export_p12`.
- Support strings as path argument for `ExportOptions.from_path` factory method.
- Support strings as path argument for `PbxProject.from_path` factory method.
- Extract resource management methods from `AppStoreConnect` to separate mixin class.
- Generate documentation for action `app-store-connect apps get`.
- Generate documentation for action `app-store-connect apps list`.
- Generate documentation for action `app-store-connect apps app-store-versions`.
- Generate documentation for action `app-store-connect apps builds`.
- Generate documentation for action `app-store-connect apps pre-release-versions`.
- Generate documentation for action `app-store-connect beta-app-review-submissions create`.
- Generate documentation for action `app-store-connect beta-app-review-submissions list`.
- Generate documentation for action `app-store-connect builds pre-release-version`.
- Generate documentation for action `app-store-connect publish`.
- Generate documentation for action `xcode-project ipa-info`.
- Generate documentation for action `xcode-project pkg-info`.

Version 0.6.1
-------------

**Fixes**

- Allow `passTypeId` relationship for [Certificate](https://developer.apple.com/documentation/appstoreconnectapi/certificate) model.

Version 0.6.0
-------------

**New features**

- Add action group support for tools.
- Add action `get-profile` to `app-store-connect` to show provisioning profile based on resource identifier.
- Add action `app-store-connect app-store-version-submissions create` to submit App Store Version to review.
- Add action `app-store-connect app-store-version-submissions delete` to remove App Store Version from review.

**Development / Docs**

- Update `--profile` option default value in action `xcode-project use-profiles` docs.
- Generate documentation for action groups and list groups under tool documentation pages.
- Add documentation for action `app-store-connect get-profile`.
- Add documentation for action `app-store-connect app-store-version-submissions create`.
- Add documentation for action `app-store-connect app-store-version-submissions delete`.

Version 0.5.9
-------------

**Fixes**

- Accept `SERVICES` as a valid [Bundle Identifier platform](https://developer.apple.com/documentation/appstoreconnectapi/bundleidplatform).

Version 0.5.8
-------------

**Improvements**

- Bugfix: Allow Google Play releases with no name provided in `google-play` tool.

Version 0.5.7
-------------

**Improvements**

- Bugfix: Include MacOS application's codesigning certificates in `keychain list-certificates` output.
- Bugfix: Include provisioning profiles with `.provisionprofile` extension in in `xcode-project use-profiles` search.
- Bugfix: handle provisioning profiles entitlements keys with prefixes e.g. `com.apple.application-identifier`.
- Bugfix: Improve SDK detection when setting code signing infortmation on Xcode projects instead of always defaulting to `iphoneos` .

Version 0.5.6
-------------

**Improvements**

- CI pipeline: Use GitHub CLI tools for releases

Version 0.5.5
-------------

**Improvements**

- Bugfix: export MacOS application's provisioning profiles with `.provisionprofile` extension instead of `.mobileprovision`.

Version 0.5.4
-------------

**Improvements**

- Feature: Add option `--platform` to specify the platform for `app-store-connect` actions `get-latest-app-store-build-number` and `get-latest-testflight-build-number`.

Version 0.5.3
-------------

**Improvements**

- Feature: Add option to strictly match bundle IDs by the identifier for `app-store-connect` actions `fetch-signing-files` and `list-bundle-ids` using flag `--strict-match-identifier`.

**Dependencies**

- Update [PyJWT](https://pyjwt.readthedocs.io/en/stable/) Python dependency to version ~=2.0.

Version 0.5.2
-------------

**Improvements**

- Enhancement: Include the certificate common name in `SigningCertificate` string representation when showing certificates with `app-store-connect` actions.

Version 0.5.1
-------------

**Improvements**

- Feature: add the `warn-only` flag to `xcode-project use-profiles` not to fail the action when profiles can't be applied to any of the Xcode projects

Version 0.5.0
-------------

**Improvements**

- Feature: add tool `google-play` with action `get-latest-build-number`

Version 0.4.10
-------------

**Improvements**

- Bugfix: Fix regression introduced in 0.4.9 that excluded bundle identifiers with platform type `UNIVERSAL` from list bundle identifiers result in case platform filter (`IOS` or `MAC_OS`) was specified.
- Bugfix: Fix check for profiles types that have devices allowed. Allow specifying devices only for ad hoc and development provisioning profiles.

Version 0.4.9
-------------

**Improvements**

- Bugfix: Fix platform filter for listing bundle identifiers using App Store Connect API.

Version 0.4.8
-------------

**Improvements**

- Improvement: Add support for tvOS distribution certificates.

Version 0.4.7
-------------

**Improvements**

- Feature: Add an option to extract a certificate from PKCS12 archive.

Version 0.4.6
-------------

**Improvements**

- Feature: Add action `list-builds` to `app-store-connect` to list Builds from Apple Developer Portal matching given constraints.
- Feature: Add action `get-latest-testflight-build-number` to `app-store-connect` to get latest Testflight build number for the given application.
- Feature: Add action `get-latest-app-store-build-number` to `app-store-connect` to get latest App Store build number for the given application.
- Improvement: handle datetime in a format containing timezone timedelta

Version 0.4.5
-------------

**Improvements**

- Dependency update: Bump cryptography from ~3.2 to ~3.3
- Improvement: Add options to `keychain add-certificates` to specify which applications have access to the imported certificate without warning.

Version 0.4.4
-------------

**Improvements**

- Improvement: Reduce memory footprint for `xcode-process` by not storing xcodebuild logs in memory. Read them from file if need be.

Version 0.4.3
-------------

**Improvements**

- Improvement: Use a single `xcpretty` process throughout `xcodebuild` invocation for log formatting instead of forking new processes for each log chunk.

Version 0.4.2
-------------

**Improvements**

- Bugfix: [PyJWT](https://pypi.org/project/PyJWT/) Python dependency to version 1.x since 2.0.0 has breaking API changes.

Version 0.4.1
-------------

**Improvements**

- Bugfix: Fix converting Xcresults to Junit if testsuite duration is missing from Xcresult's ActionTestMetadata

Version 0.4.0
-------------

**Improvements**

- Feature: Add action `clean` to `xcode-project` to clean Xcode project.
- Feature: Add action `default-test-destination` to `xcode-project` to show default test destination for the chosen Xcode version.
- Feature: Add action `test-destinations` to `xcode-project` to list available destinations for test runs.
- Feature: Add action `junit-test-results` to `xcode-project` to convert Xcode Test Result Bundles (*.xcresult) to JUnit XML format.
- Feature: Add action `run-tests` to `xcode-project` to run unit or UI tests for given Xcode project or workspace.
- Feature: Add action `test-summary` to `xcode-project` to show test result summary from given Xcode Test Result Bundles (*.xcresult).
- Refactoring: Create `RunningCliAppMixin` to avoid passing around currently invoked app instance.

- Update [cryptography](https://github.com/pyca/cryptography) Python dependency to version ~=3.2.

Version 0.3.2
-------------

**Improvements**

- Bugfix: Do not fail `keychain add-certificate` action in case the added certificate already exists in keychain.

Version 0.3.1
-------------

- Update [cryptography](https://github.com/pyca/cryptography) Python dependency to version ~=3.2.

Version 0.3.0
-------------

**Improvements**

- Feature: Add option to specify custom `xcodebuild` arguments and flags for `archive` and `-exportArchive` actions with `xcode-project build-ipa` using `--archive-flags`, `--archive-xcargs`, `--export-flags` and `--export-xcargs` modifiers.

Version 0.2.13
-------------

**Improvements**

- Improvement: Due to invalid CoreSimulatorService state `xcodebuild` build commands can fail with error `Failed to find newest available Simulator runtime`. To overcome this, make sure that when Xcode project or workspace is archived with `xcode-project build-ipa`, then CoreSimulatorService is in a clean state.

Version 0.2.12
-------------

**Improvements**

- Improvement: Fail gracefully with appropriate error message when non-existent export options plist path is passed to `xcode-project build-ipa`.

Version 0.2.11
-------------

**Improvements**

- Bugfix: Fix obtaining `iCloudContainerEnvironment` export option when multiple values are available.

Version 0.2.10
-------------

**Improvements**

- Bugfix: Specify `iCloudContainerEnvironment` export option when exporting xcarchive to ipa using `xcode-project build-ipa`.

Version 0.2.9
-------------

**Improvements**

- Update: Make removing generated xcarchive optional.

Version 0.2.8
-------------

**Improvements**

- Bugfix: Support profile state `EXPIRED`.

Version 0.2.7
-------------

**Improvements**

- Bugfix: Respect custom values specified by `--certificates-dir` and `--profiles-dir` flags for `app-store-connect`.
- Feature: Add `--profile-type` filter to `app-store-connect list-certificates` to show only certificates that can be used with given profile type.
- Feature: Support new certificate types `DEVELOPMENT` and `DISTRIBUTION`.
- Feature: Support new profile types `MAC_CATALYST_APP_DEVELOPMENT`, `MAC_CATALYST_APP_DIRECT` and `MAC_CATALYST_APP_STORE`.

Version 0.2.6
-------------

**Improvements**

- Feature: Support OpenSSH private key format for certificate private key (`--certificate-key` option for `app-store-connect`).
- Bugfix: For `app-store-connect fetch-signing-files` use given platform type for listing devices on creating new provisioning profiles instead of detecting it from bundle identifier.

Version 0.2.5
-------------

**Improvements**

- Bugfix: Improve product bundle identifier resolving for settings code signing settings.

Version 0.2.4
-------------

**Improvements**

- Feature: Add option to specify archive directory to `xcode-project build-ipa` using `--archive-directory` flag.

Version 0.2.3
-------------

**Improvements**

- Bugfix: Improve variable resolving from Xcode projects for setting code signing settings.

Version 0.2.2
-------------

**Improvements**

- Bugfix: Fix nullpointer on setting process stream flags.

Version 0.2.1
-------------

**Improvements**

- Bugfix: Reading `jarsigner verify` output streams got stuck on some Android App bundles.

Version 0.2.0
-------------

**Improvements**

- Feature: Add new command `android-app-bundle`
- Feature: Include [Bundletool](https://developer.android.com/studio/command-line/bundletool) jar in the distribution
- Bugfix: Gracefully handle Xcodeproj exceptions on saving React Native iOS project code signing settings

**Deprecations**

- Add deprecation notice to `universal-apk` command

Version 0.1.9
-------------

- Improve error messages on invalid inputs when using argument values from environment variables.

Version 0.1.8
-------------

- Add `--version` option to tools to display current version.

Version 0.1.7
-------------

- Bugfix: Fix Apple Developer Portal API pagination.
Avoid duplicate query parameters in subsequent pagination calls when listing resources.

Version 0.1.6
-------------

- Bugfix: Fix creating iOS App Store and iOS In House provisioning profiles.
Do not include devices in the create resource payload.

Version 0.1.5
-------------

- Bugfix: Fix `TypeError` on Apple Developer Portal resource creation

Version 0.1.4
-------------

- Bugfix: Accept `UNIVERSAL` as valid Bundle ID platform value

Version 0.1.3
-------------

- Bugfix: Improve detection for Xcode managed provisioning profiles

Version 0.1.2
-------------

Released 10.02.2020

- Return exit code `0` on successful invocation of `git-changelog`
- Return exit code `0` on successful invocation of `universal-apk`

Version 0.1.1
-------------

Released 31.01.2020

- Update documentation

Version 0.1.0
-------------

Released 14.01.2020

- Add tool `app-store-connect`
- Add tool `keychain`
- Add tool `xcode-project`
