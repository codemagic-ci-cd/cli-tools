Version 0.4.5
-------------

**Improvements**

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
