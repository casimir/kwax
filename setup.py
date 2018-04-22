from setuptools import setup

OPTIONS = {
    'iconfile': 'kakoune.icns',
    'plist': {
        'CFBundleName': "kwax",
        'CFBundleIdentifier': "me.casimir.kwax",
        'CFBundleDocumentTypes': [{
            'CFBundleTypeName': "Document",
            'CFBundleTypeRole': "Editor",
            'LSItemContentTypes': ["public.content", "public.data"],
        }],
    },
}

setup(
    app=['main_app.py'],
    data_files=[],
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
