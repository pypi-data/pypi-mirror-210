import json
import logging
from typing import Optional
from urllib.parse import urlparse

import tomli

from .activitypub.authorization_wrapper import AuthorizationWrapper
from .activitypub.collection_helper import CollectionHelper, all_collection_elements
from .activitystreams import Collection
from .activitystreams.activity_factory import ActivityFactory
from .activitystreams.object_factory import ObjectFactory

logger = logging.getLogger(__name__)


class BovineClient(AuthorizationWrapper):
    """BovineClient is meant to serve as the basis of building ActivityPub Clients.
    It defines methods for interacting with the endpoints defined by the corresponding
    ActivityPub Actor: inbox, outbox, and proxyUrl.

    Usage is either:

    .. code-block:: python

        async with BovineClient(config) as actor:
            await do_something(actor)

    or

    .. code-block:: python

        actor = await BovineClient(config)
        await actor.init()
        await do_something(actor)

    I still call the variable actor as it represents the ActivityPub Actor through
    a client.

    :param config:

        * Moo-Auth-1: keys "host" and "private_key"
        * HTTP Signatures: keys "account_url", "public_key_url", and "private_key"
        * Bearer Authorization: keys "account_url", "access_token"

    """

    def __init__(self, config):
        super().__init__()

        self.actor_id = None
        self.information: Optional[dict] = None
        self._activity_factory = None
        self._object_factory = None
        self.config = config

    async def get(self, target):
        assert self.client

        response = await self.client.get(target)
        response.raise_for_status()
        return json.loads(await response.text())

    async def init(self, session=None):
        """Manually initializes the BovineClient for cases when
        not used within async with. Also loads the actor information.

        :param session:
            can be used to specify an existing aiohttp.ClientSession. Otherwise a new
            one is created.
        """

        await super().init(session=session)

        if self.client is None:
            raise Exception("Client not set in BovineClient")
        self.information = await self.get(self.actor_id)

        logger.debug("Retrieved information %s", self.information)

        if any(required not in self.information for required in ["inbox", "outbox"]):
            raise Exception("Retrieved incomplete actor data")

    async def send_to_outbox(self, data: dict):
        """sends data to outbox of actor

        :param data: The data to send as python dict

        :return:
            The aiohttp.ClientResponse object. This means
            return_value.headers["location"] will contain the id of the
            posted activity.
        """
        if self.information is None:
            await self.init()

        assert self.client

        return await self.client.post(self.information["outbox"], json.dumps(data))

    async def proxy_element(self, target: str):
        """Retrieve's an element through the actos' proxyUrl endpoint
        as specified in ActivityPub.

            :param target: The URL of the object to retrieve"""
        response = await self.client.post(
            self.information["endpoints"]["proxyUrl"],
            f"id={target}",
            content_type="application/x-www-form-urlencoded",
        )
        response.raise_for_status()
        return await response.json()

    async def event_source(self):
        """Returns an EventSource corresponding to the actor's

        The syntax for this will probably change"""
        if self.information is None:
            await self.load()

        event_source_url = self.information["endpoints"]["eventSource"]
        return self.client.event_source(event_source_url)

    async def simplify_collection(self, collection):
        """Returns a Collection containing all items from the passed collection
        or collection id"""
        items = await all_collection_elements(self, collection)

        if isinstance(collection, str):
            collection_id = collection
        else:
            collection_id = collection.get("id")
        return Collection(id=collection_id, items=items).build()

    @property
    def activity_factory(self):
        """Returns an ActivityFactory for objects corresponding to the client's actor"""
        if self._activity_factory is None:
            self._activity_factory = ActivityFactory(self.information)
        return self._activity_factory

    @property
    def object_factory(self):
        """Returns an ObjectFactory for objects corresponding to the client's actor"""
        if self._object_factory is None:
            self._object_factory = ObjectFactory(client=self)
        return self._object_factory

    @property
    def factories(self):
        return self.activity_factory, self.object_factory

    @property
    def host(self):
        """The host the actor is on"""
        return urlparse(self.actor_id).netloc

    @property
    def followers(self) -> str:
        """The id of the follows collection"""
        return self.information["followers"]

    async def inbox(self):
        """Provides a CollectionHelper for the Actors inbox"""
        inbox_collection = CollectionHelper(self.information["inbox"], self)
        await inbox_collection.refresh()
        return inbox_collection

    async def outbox(self):
        """Provides a CollectionHelper for the Actors outbox"""
        inbox_collection = CollectionHelper(self.information["outbox"], self)
        await inbox_collection.refresh()
        return inbox_collection

    @staticmethod
    def from_file(config_file: str):
        """Initializes the BovineClient from a toml config file"""
        with open(config_file, "rb") as fp:
            config = tomli.load(fp)

        return BovineClient(config)


class BovineActor(AuthorizationWrapper):
    r"""Defines the Bovine version of an ActivityPub Actor. This class is meant
    to be used when implementing an ActivityPub Server in order to handle the
    HTTP requests to another server.

    Currently most of these interactions use HTTP Signatures.

    Usage is either:

    .. code-block:: python

        async with BovineActor(config) as actor:
            await do_something(actor)

    or

    .. code-block:: python

        actor = await BovineActor(config)
        await actor.init()
        await do_something(actor)




    :param config:
        Configuration with keys "host" and "private_key" -> Moo-Auth-1;
        with keys "account_url", "public_key_url", and "private_key" -> HTTP Signatures

    """

    def __init__(self, config):
        super().__init__()

        self.config: dict = config

    async def init(self, session=None):
        """Manually initializes the BovineActor for cases when not used
        within async with

        :param session:
            can be used to specify an existing aiohttp.ClientSession. Otherwise a new
            one is created.
        """

        await super().init(session=session)

    async def post(self, target: str, data: dict):
        """Send a signed post with data to target"""
        response = await self.client.post(target, json.dumps(data))
        response.raise_for_status()

        return response

    async def get(self, target: str, fail_silently: bool = False):
        """Retrieve target with a get. An exception is raised if the request fails

        :param target: The URL of the object to retrieve
        :param fail_silently: do not raise an exception if the request fails
        """
        response = await self.client.get(target)
        if fail_silently and response.status >= 400:
            return None

        response.raise_for_status()
        return json.loads(await response.text())

    async def get_ordered_collection(self, url: str, max_items: Optional[int] = None):
        """Retrieve target ordered collection

        :param url: url of the ordered collection
        :param max_items: maximal number of items to retrieve, use None for all
        """
        result = await self.client.get(url)
        result.raise_for_status()

        data = json.loads(await result.text())

        total_number_of_items = data["totalItems"]
        items = []

        if "orderedItems" in data:
            items = data["orderedItems"]

        if len(items) == total_number_of_items:
            return {"total_items": total_number_of_items, "items": items}

        if "first" in data:
            page_data = await self.get(data["first"])

            items = page_data["orderedItems"]

            while "next" in page_data and len(page_data["orderedItems"]) > 0:
                if max_items and len(items) > max_items:
                    return {"total_items": total_number_of_items, "items": items}

                page_data = await self.get(page_data["next"])

                items += page_data["orderedItems"]

        return {"total_items": total_number_of_items, "items": items}

    @staticmethod
    def from_file(config_file: str):
        with open(config_file, "rb") as fp:
            config = tomli.load(fp)

        return BovineActor(config)
