#!/usr/bin/env python3
import errno
from typing import List

import requests
from nubia import argument
from nubia import command
from requests import HTTPError
from termcolor import cprint

from seqslab.auth.commands import BaseAuth as Auth
from seqslab.organization.resource.base import BaseResource

import yarl

"""
Copyright (C) 2023, Atgenomix Incorporated.

All Rights Reserved.

This program is an unpublished copyrighted work which is proprietary to
Atgenomix Incorporated and contains confidential information that is not to
be reproduced or disclosed to any other person or entity without prior
written consent from Atgenomix, Inc. in each and every instance.

Unauthorized reproduction of this program as well as unauthorized
preparation of derivative works based upon the program or distribution of
copies by sale, rental, lease or lending are violations of federal copyright
laws and state trade secret laws, punishable by civil and criminal penalties.
"""


class BaseOrg:

    @command
    @argument("id",
              type=str,
              positional=False,
              description="Specify an organization ID (required).")
    @argument("uri",
              type=List[str],
              positional=False,
              description="Specify the redirect URI for auth code flow (optional). If no URI is provided, "
                          "all existing registered URIs will be removed.")
    def redirect_uri(self, id: str, uri: List[str] = [], **kwargs) -> int:
        """
        Register redirect URI(s) for auth code flow.
        """
        for u in uri:
            o = yarl.URL(u)
            if not o.scheme or not o.host:
                cprint(f"Invalid URI '{u}'", "red")
                return -1

        try:
            token = Auth.get_token().get("tokens").get("access")
            BaseResource.request_wrapper(
                callback=requests.post,
                url=BaseResource.MGMT_ORG_URL.format(organization=id),
                headers={"Authorization": f"Bearer {token}"},
                data={"redirect_uris": uri},
                status=[requests.codes.ok])
        except HTTPError as e:
            cprint(str(e), "red")
            return errno.EPROTO
        else:
            return 0


@command
class Org(BaseOrg):
    """Organization commands"""

    def __init__(self):
        super().__init__()
