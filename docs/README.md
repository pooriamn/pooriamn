# Portfolio website

The website uses plain HTML, CSS and JavaScript. There is no build step or third-party framework.

To preview it from the repository root:

```sh
python -m http.server 8000 --directory docs
```

Open http://localhost:8000 in a browser. The project cards link to the source and documentation, and the calculator runs locally in the browser.

To publish it, enable GitHub Pages in repository Settings → Pages, select **Deploy from a branch**, then choose **main** and **/docs**. The expected project-site address is https://pooriamn.github.io/pooriamn/. Publishing is a separate account setting; committing these files alone does not activate it.
