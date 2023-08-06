import pytest

from bovine import BovineClient

from .collection_helper import all_collection_elements


@pytest.mark.skip("Network requests")
async def test_collections():
    remote = "https://indieweb.social/@tchambers/109993434359560479"
    async with BovineClient.from_file("h.toml") as client:
        result = await client.proxy_element(remote)

        replies = result["replies"]

        replies = await all_collection_elements(client, replies)

        assert isinstance(replies, list)
