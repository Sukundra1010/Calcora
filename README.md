# Calcora

Calcora includes a calculator website and a Python/Kivy Android app.

## Run the website

From the project folder, run:

```text
python calculator.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser.

## Publish the website

The website uses Python, so GitHub Pages cannot host the calculator by itself.
To publish it for other phones and computers, connect this GitHub repository to
[Render](https://render.com/) and create a Blueprint from `render.yaml`. Render
will build and start the Python server and provide a public website URL. Its
free service may take a short time to wake up after being idle.

## Android app

The Android project is in `android_app`. It uses Kivy and Buildozer. See
`android_app/README.txt` for instructions to run it or build an Android package.
