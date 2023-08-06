from bovine.activitystreams.utils.print import print_activity

from .collection_iterator import CollectionIterator


async def all_collection_elements(client, collection):
    result = []
    if isinstance(collection, str):
        collection = await client.proxy_element(collection)

    if "items" in collection:
        result = collection["items"]
        if isinstance(result, str):
            result = [result]

    if "first" in collection:
        return result + await all_collection_elements(client, collection["first"])

    if "next" in collection:
        return result + await all_collection_elements(client, collection["next"])

    return result


class CollectionHelper:
    def __init__(self, collection_id, actor):
        self.collection_id = collection_id
        self.actor = actor

        self.basic_information = None
        self.items = None
        self.next_items = None
        self.item_index = None

        self.element_cache = {}

    async def refresh(self):
        if self.basic_information is None:
            self.basic_information = await self.actor.get(self.collection_id)

        if "first" not in self.basic_information:
            return

        response = await self.actor.get(self.basic_information["first"])

        self.items = response["orderedItems"]
        self.next_items = response["next"]
        self.item_index = 0

    async def get_element(self, element):
        if not isinstance(element, str):
            return element

        if element in self.element_cache:
            return self.element_cache[element]

        result = await self.actor.proxy_element(element)

        self.element_cache[element] = result

        return result

    async def next_item(self, do_print=False):
        if self.item_index >= len(self.items):
            response = await self.actor.get(self.next_items)
            self.items += response["orderedItems"]
            self.next_items = response["next"]

        result = self.items[self.item_index]
        self.item_index += 1

        result = await self.get_element(result)

        if do_print:
            print_activity(result)

        return result

    def iterate(self, max_number=10):
        return CollectionIterator(self, max_number)
