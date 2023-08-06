# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-campusonline is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE
# file for more details.

"""Command line interface to interact with the CampusOnline-Connector module."""
from datetime import datetime
from pathlib import Path
from shutil import copyfileobj
from xml.etree.ElementTree import Element, fromstring

from requests import get, post

from .types import URL, CampusOnlineID, CampusOnlineToken, Embargo, FilePath


def create_request_body_metadata(
    token: CampusOnlineToken,
    campusonline_id: CampusOnlineID,
) -> str:
    """Build Request."""
    body = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
      <soapenv:Header/>
      <soapenv:Body>
        <bas:getMetadataByThesisIDRequest>
          <bas:token>TOKEN</bas:token>
          <bas:ID>CAMPUSONLINE_ID</bas:ID>
          <bas:attr key="ALL"/>
          <bas:classAttrKeySet>
            <bas:name>text</bas:name>
            <bas:attr key="ALL"/>
          </bas:classAttrKeySet>
          <bas:classAttrKeySet>
            <bas:name>author</bas:name>
            <bas:attr key="ALL"/>
          </bas:classAttrKeySet>
          <bas:classAttrKeySet>
            <bas:name>supervisor</bas:name>
            <bas:attr key="ALL"/>
          </bas:classAttrKeySet>
        </bas:getMetadataByThesisIDRequest>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    return body.replace("TOKEN", token).replace("CAMPUSONLINE_ID", campusonline_id)


def create_request_body_download(
    token: CampusOnlineToken,
    campusonline_id: CampusOnlineID,
) -> str:
    """Build Request."""
    body = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
      <soapenv:Header/>
      <soapenv:Body>
        <bas:getDocumentByThesisIDRequest>
          <bas:token>TOKEN</bas:token>
          <bas:ID>CAMPUSONLINE_ID</bas:ID>
          <bas:docType>VOLLTEXT</bas:docType>
        </bas:getDocumentByThesisIDRequest>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    return body.replace("TOKEN", token).replace("CAMPUSONLINE_ID", campusonline_id)


def create_request_body_ids(
    token: CampusOnlineToken,
    theses_filter: list[Element],
) -> str:
    """Build request."""
    body = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:bas="http://www.campusonline.at/thesisservice/basetypes">
      <soapenv:Header/>
      <soapenv:Body>
        <bas:getAllThesesMetadataRequest>
          <bas:token>TOKEN</bas:token>
          FILTER
        </bas:getAllThesesMetadataRequest>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    return body.replace("TOKEN", token).replace("FILTER", "\n".join(theses_filter))


def create_request_header(service: str) -> dict:
    """Create request header."""
    return {
        "Content-Type": "application/xml",
        "SOAPAction": f"urn:service#{service}",
    }


def get_embargo_range(thesis: Element) -> Element:
    """Extract the embargo range."""
    ns = "http://www.campusonline.at/thesisservice/basetypes"
    xpath_start = f".//{{{ns}}}attr[@key='SPVON']"
    xpath_end = f".//{{{ns}}}attr[@key='SPBIS']"
    start = thesis.find(xpath_start)
    end = thesis.find(xpath_end)

    if start is None or end is None:
        return Embargo()

    if start.text is None or end.text is None:
        return Embargo()

    in_format = "%Y-%m-%d %H:%M:%S"
    start_embargo = datetime.strptime(start.text, in_format)
    end_embargo = datetime.strptime(end.text, in_format)

    return Embargo(start_embargo, end_embargo)


def get_metadata(
    endpoint: URL,
    token: CampusOnlineToken,
    campusonline_id: CampusOnlineID,
) -> Element:
    """Get Metadata."""
    body = create_request_body_metadata(token, campusonline_id)
    headers = create_request_header("getMetadataByThesisID")
    response = post(endpoint, data=body, headers=headers, timeout=10)

    root = fromstring(response.text)

    xpath = "{http://www.campusonline.at/thesisservice/basetypes}thesis"
    return list(root.iter(xpath))[0]  # TODO: fix it


def get_file_url(
    endpoint: URL,
    token: CampusOnlineToken,
    campusonline_id: CampusOnlineID,
) -> str:
    """Get file URL."""
    body = create_request_body_download(token, campusonline_id)
    headers = create_request_header("getDocumentByThesisID")
    response = post(endpoint, data=body, headers=headers, timeout=10)

    root = fromstring(response.text)
    xpath = "{http://www.campusonline.at/thesisservice/basetypes}docUrl"
    file_url = list(root.iter(xpath))[0]  # TODO: make it more nice
    return file_url.text


def store_file_temporarily(file_url: URL, file_path: FilePath) -> None:
    """Store the file referenced by url to the local file path."""
    with get(file_url, stream=True, timeout=10) as response:  # noqa: SIM117
        with Path(file_path).open("wb") as fp:
            copyfileobj(response.raw, fp)


def download_file(
    endpoint: URL,
    token: CampusOnlineToken,
    campusonline_id: CampusOnlineID,
) -> FilePath:
    """Download files from campus online by campusonline_id."""
    file_url = get_file_url(endpoint, token, campusonline_id)
    file_url = f"{file_url}{token}"
    file_path = f"/tmp/{campusonline_id}.pdf"  # noqa: S108
    store_file_temporarily(file_url, file_path)
    return file_path
