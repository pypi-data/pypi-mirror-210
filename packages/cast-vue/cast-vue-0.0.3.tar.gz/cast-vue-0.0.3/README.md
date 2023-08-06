# Installing Vue.js Theme for Django-Cast

This document provides the instructions on how to install the Vue.js theme for Django-Cast. Please follow the steps below.

## Installation

### 1. Install the theme

To install the Vue.js theme, you will need to run the following command in your command line:

```shell
pip install cast-vue
```

### 2. Add entries to INSTALLED_APPS

You will need to add `django_vite` and `cast_vue.apps.CastVueConfig`
to your INSTALLED_APPS in your Django settings.

Then, set the DJANGO_VITE_ASSETS_PATH and DJANGO_VITE_DEV_MODE like so:

```python
INSTALLED_APPS = [
    ...
    'django_vite',
    'cast_vue.apps.CastVueConfig',
    ...
]


DJANGO_VITE_ASSETS_PATH = ROOT_DIR.path("staticfiles").path("cast_vue")  # does not matter for development
DJANGO_VITE_MANIFEST_PATH = DJANGO_VITE_ASSETS_PATH.path("manifest.json")
DJANGO_VITE_STATIC_URL_PREFIX = "/static/cast_vue/"  # really important for production!
DJANGO_VITE_DEV_MODE = DEBUG
```

### 3. Set the theme in Wagtail admin

You can set the theme to `vue` in the Wagtail admin for the
complete site or just one blog.

### End

That's it! You have successfully installed and set up the Vue.js theme
for [`django-cast`](https://github.com/ephes/django-cast).
