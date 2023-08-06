# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""The module is used to import/export from/to the CampusOnline System."""

from flask import Flask


class InvenioCampusonline:
    """invenio-campusonline extension."""

    def __init__(self, app: Flask = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        app.extensions["invenio-campusonline"] = self
