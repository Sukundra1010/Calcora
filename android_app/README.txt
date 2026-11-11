Calcora Android app

This folder contains a Python/Kivy Android app. It is separate from the
calculator website in the parent folder.

To try the app on a computer, install Kivy and run:

  python main.py

To build an Android package, use Linux or Windows Subsystem for Linux (WSL).
Buildozer downloads the Android build tools the first time it runs. From this
folder, run:

  buildozer android debug

The debug APK is written to the bin folder. It can be installed on an Android
device for testing.

For Google Play, run `buildozer android release` from this folder. The release
artifact is configured as an Android App Bundle (AAB), using package ID
`com.sukundra1010.calcora` and Android API 36. Sign the AAB with your upload key
before submitting it through Play Console. Keep the keystore and passwords
private; never commit them or put them in the repository.

Publishing requires a Google Play Console developer account and completion of
the app setup and policy declarations. New personal accounts created after
November 13, 2023 must complete a closed test with at least 12 testers opted
in continuously for 14 days before they can apply for production access.
