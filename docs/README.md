
CLI tools
=========

|Tool name|Description|
| :--- | :--- |
|[`android-app-bundle`](android-app-bundle/README.md)|Manage Android App Bundles using [Bundletool](https://developer.android.com/studio/command-line/bundletool).<br>Requires a Java runtime for Bundletool and `jarsigner` from a JDK for the signing actions.<br>Platform support: Linux, macOS and Windows.|
|[`android-keystore`](android-keystore/README.md)|Manage your Android app code signing keystores.<br>Requires `keytool` from a JDK on PATH.<br>Platform support: Linux, macOS and Windows.|
|[`app-store-connect`](app-store-connect/README.md)|Interact with Apple services via App Store Connect API.<br>The `publish` action runs `xcrun altool` and therefore needs macOS.<br>Platform support: Linux, macOS and Windows.|
|[`codemagic-cli-tools`](codemagic-cli-tools/README.md)|Show general information of installed Codemagic CLI tools.<br>Platform support: Linux, macOS and Windows.|
|[`firebase-app-distribution`](firebase-app-distribution/README.md)|Utility to list releases and retrieve the latest release build version number from Firebase.<br>Platform support: Linux, macOS and Windows.|
|[`git-changelog`](git-changelog/README.md)|Generate a changelog text from git history.<br>Requires `git` on PATH.<br>Platform support: Linux, macOS and Windows.|
|[`google-play`](google-play/README.md)|Utility to get the latest build numbers from Google Play using Google Play Developer API.<br>Requires a Java runtime for the actions that read an Android App Bundle.<br>Platform support: Linux, macOS and Windows.|
|[`keychain`](keychain/README.md)|Utility to manage macOS keychains and certificates. Drives the system `security` tool.<br>Platform support: macOS.|
|[`universal-apk`](universal-apk/README.md)|Generate universal APK files from Android App Bundles. DEPRECATED! Use `android-app-bundle` instead.<br>Requires a Java runtime for Bundletool, which it delegates to.<br>Platform support: Linux, macOS and Windows.|
|[`xcode-project`](xcode-project/README.md)|Utility to work with Xcode projects. Use it to manage iOS application code signing properties for builds, create IPAs and run tests.<br>Requires the Xcode command line tools.<br>Platform support: macOS.|
