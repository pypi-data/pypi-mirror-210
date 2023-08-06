import logging
from typing import Optional

import aiohttp

from bovine.clients import lookup_did_with_webfinger
from bovine.clients.bearer import BearerAuthClient
from bovine.clients.moo_auth import MooAuthClient
from bovine.clients.signed_http import SignedHttpClient
from bovine.crypto import private_key_to_did_key

logger = logging.getLogger(__name__)


class AuthorizationWrapper:
    def __init__(self):
        self.config: Optional[dict] = None
        self.actor_id: Optional[str] = None
        self.client = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self.init()
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def init(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        if session is None:
            self.session = aiohttp.ClientSession()

        assert self.config

        if self._has_moo_auth():
            await self.with_host_and_ed25519_private_key(
                self.config["host"], self.config["private_key"], session=self.session
            )
        elif self._has_http_signature():
            self.actor_id = self.config["account_url"]
            self.with_http_signature(
                self.config["public_key_url"],
                self.config["private_key"],
                session=self.session,
            )
        elif self._has_bearer_auth():
            self.actor_id = self.config["account_url"]
            self.with_bearer_token(self.config["access_token"], session=self.session)
        else:
            raise Exception("No known authorization method available")

    async def with_host_and_ed25519_private_key(
        self,
        host: str,
        private_key: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        if session is None:
            session = aiohttp.ClientSession()
        did_key = private_key_to_did_key(private_key)

        self.actor_id = await lookup_did_with_webfinger(session, host, did_key)

        if not isinstance(self.actor_id, str):
            logger.error("Failed to lookup actor id")
            raise Exception("Failed to create Moo Auth Client")

        self.client = MooAuthClient(session, did_key, private_key)

        return self

    def with_actor_id(self, actor_id: str):
        self.actor_id = actor_id
        return self

    def with_http_signature(
        self,
        public_key_url: str,
        private_key: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        if session is None:
            session = aiohttp.ClientSession()

        self.client = SignedHttpClient(session, public_key_url, private_key)

        return self

    def with_bearer_token(
        self,
        access_token: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        if session is None:
            session = aiohttp.ClientSession()

        self.client = BearerAuthClient(session, access_token)

        return self

    def _has_http_signature(self):
        return self._has_keys(["account_url", "public_key_url", "private_key"])

    def _has_moo_auth(self):
        return self._has_keys(["host", "private_key"])

    def _has_bearer_auth(self):
        return self._has_keys(["account_url", "access_token"])

    def _has_keys(self, key_list: list):
        for key in key_list:
            if key not in self.config:
                return False

        return True
