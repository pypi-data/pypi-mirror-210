from setuptools import setup

name = "types-PyAutoGUI"
description = "Typing stubs for PyAutoGUI"
long_description = '''
## Typing stubs for PyAutoGUI

This is a PEP 561 type stub package for the `PyAutoGUI` package. It
can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`PyAutoGUI`. The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/PyAutoGUI. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `a4e33d4053e3c3310459f480890cee1b1bb97753`.
'''.lstrip()

setup(name=name,
      version="0.9.3.6",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/PyAutoGUI.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-Pillow', 'types-PyScreeze'],
      packages=['pyautogui-stubs'],
      package_data={'pyautogui-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
