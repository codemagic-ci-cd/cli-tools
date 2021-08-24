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
