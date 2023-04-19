from typing import Dict, List

import pymongo


class Database:
    """A class to hold all the database functions"""

    async def get_sorted_versions(
        self, collection: pymongo.collection.Collection
    ) -> List[Dict[str, int]]:
        """I have no idea how this works, but it does, thanks github copilot

        Args:
            collection (pymongo.collection.Collection): server collection

        Returns:
            list[dict[str, int]]: sorted list of versions by frequency
        """
        pipeline = [
            {"$match": {"lastOnlineVersion": {"$exists": True}}},
            {"$group": {"_id": "$lastOnlineVersion", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        result = list(collection.aggregate(pipeline))
        result = [{"version": r["_id"], "count": r["count"]} for r in result]
        return result

    async def get_total_players_online(
        self, collection: pymongo.collection.Collection
    ) -> int:
        """Gets the total number of players online across all servers via ai voodoo

        Args:
            collection (pymongo.collection.Collection): server collection

        Returns:
            int: total number of players online
        """
        pipeline = [
            {"$match": {"lastOnlinePlayers": {"$gte": 1, "$lt": 100000}}},
            {"$group": {"_id": None, "total_players": {"$sum": "$lastOnlinePlayers"}}},
        ]
        result = list(collection.aggregate(pipeline))
        if len(result) > 0:
            return result[0]["total_players"]
        else:
            return 0

    async def getPlayersLogged(self, collection: pymongo.collection.Collection) -> int:
        pipeline = [
            {"$unwind": "$lastOnlinePlayersList"},
            {"$group": {"_id": "$lastOnlinePlayersList.uuid"}},
            {"$group": {"_id": None, "count": {"$sum": 1}}},
        ]
        result = collection.aggregate(pipeline)
        try:
            return result.next()["count"]
        except StopIteration:
            return 0
