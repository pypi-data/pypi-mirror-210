# macos-application-location.py

## Installation

```sh
pip install macos_application_location
```

## Usage

```py
import pathlib

import macos_application_location


app_path: pathlib.Path = macos_application_location.get()
```