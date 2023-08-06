# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the CampusOnline-Connector module."""


from click import STRING, group, option, secho
from click_params import URL
from flask import current_app
from flask.cli import with_appcontext

from .api import fetch_all_ids, import_from_campusonline
from .types import CampusOnlineConfigs, Color


@group()
def campusonline() -> None:
    """Campusonline CLI."""


@campusonline.command()
@with_appcontext
@option("--endpoint", type=URL)
@option("--campusonline-id", type=STRING)
@option("--token", type=STRING)
@option("--user-email", type=STRING, default="cms@tugraz.at")
@option("--no-color", is_flag=True, default=False)
def import_thesis(
    endpoint: str,
    campusonline_id: str,
    token: str,
    user_email: str,
    no_color: bool,  # noqa: FBT001
) -> None:
    """Import metadata and file (aka one thesis) from campusonline."""
    import_func = current_app.config["CAMPUSONLINE_IMPORT_FUNC"]
    theses_filters = current_app.config["CAMPUSONLINE_THESES_FILTERS"]
    recipients = current_app.config["CAMPUSONLINE_ERROR_MAIL_RECIPIENTS"]
    sender = current_app.config["CAMPUSONLINE_ERROR_MAIL_SENDER"]

    configs = CampusOnlineConfigs(
        endpoint,
        token,
        user_email,
        theses_filters,
        recipients,
        sender,
    )
    record = import_from_campusonline(import_func, campusonline_id, configs)

    color = Color.success if not no_color else Color.neutral
    secho(f"record.id: {record.id}", fg=color)


@campusonline.command()
@with_appcontext
@option("--endpoint", type=URL)
@option("--token", type=STRING)
@option("--no-color", is_flag=True)
def fetch_ids(
    endpoint: str,
    token: str,
    no_color: bool,  # noqa: FBT001
) -> None:
    """Fetch all to import ids."""
    theses_filters = current_app.config["CAMPUSONLINE_THESES_FILTERS"]
    ids = fetch_all_ids(endpoint, token, theses_filters)

    color = Color.success if not no_color else Color.neutral
    secho(f"ids: {ids}", fg=color)
