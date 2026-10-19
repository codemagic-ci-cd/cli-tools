
CLI tools
=========

|Tool name|Description|
| :--- | :--- |
|[`android-app-bundle`](android-app-bundle/README.md)|Manage Android App Bundles using [Bundletool](https://developer.android.com/studio/command-line/bundletool).  Platform support: Linux and macOS, with a Java runtime for Bundletool and `jarsigner` from a JDK for the signing actions.|
|[`android-keystore`](android-keystore/README.md)|Manage your Android app code signing keystores.  Platform support: Linux and macOS, with `keytool` from a JDK on PATH.|
|[`app-store-connect`](app-store-connect/README.md)|Interact with Apple services via App Store Connect API.  Platform support: Linux and macOS, except the `publish` action, which runs `xcrun altool` and therefore needs macOS.|
|[`codemagic-cli-tools`](codemagic-cli-tools/README.md)|Show general information of installed Codemagic CLI tools.  Platform support: Linux and macOS.|
|[`firebase-app-distribution`](firebase-app-distribution/README.md)|Utility to list releases and retrieve the latest release build version number from Firebase.  Platform support: Linux and macOS.|
|[`git-changelog`](git-changelog/README.md)|Generate a changelog text from git history.  Platform support: Linux and macOS, with `git` on PATH.|
|[`google-play`](google-play/README.md)|Utility to get the latest build numbers from Google Play using Google Play Developer API.  Platform support: Linux and macOS, with a Java runtime for the actions that read an Android App Bundle.|
|[`keychain`](keychain/README.md)|Utility to manage macOS keychains and certificates.  Platform support: macOS only, since it drives the system `security` tool.|
|[`universal-apk`](universal-apk/README.md)|Generate universal APK files from Android App Bundles. DEPRECATED! Use `android-app-bundle` instead.  Platform support: Linux and macOS, with a Java runtime for Bundletool, which it delegates to.|
|[`xcode-project`](xcode-project/README.md)|Utility to work with Xcode projects. Use it to manage iOS application code signing properties for builds, create IPAs and run tests.  Platform support: macOS only, with the Xcode command line tools.|
