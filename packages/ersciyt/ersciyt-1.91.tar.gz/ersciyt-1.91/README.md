Erscipcard
=========

Quick start
-----------
1.Add "ersciyt" to your INSTALLED_APPS in your project setting.py file:
```
INSTALLED_APPS = [
...,
'ersciyt',
]
```

2.Include the erscipcard URLconf in your project urls.py like this:

```
path('yt/', include('ersciyt.urls')),
```

3.Visit http://127.0.0.1:8000/yt/ to create users and its cards.
