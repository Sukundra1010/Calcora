Neon Calculator Android app

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

For Google Play, create a signed release Android App Bundle (AAB), set a
unique package domain in buildozer.spec, and submit it through a Google Play
developer account. Google Play requires new apps to target Android 16 (API 36)
or higher starting August 31, 2026.
