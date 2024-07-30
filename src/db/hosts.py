from pathlib import Path

from aiotinydb import AIOTinyDB
from environs import Env

ENV = Env()
ENV.read_env("./.env")


class HostsDb:
    PATH = ENV.path("HOSTS_PATH")

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        Path(self.PATH).parent.mkdir(exist_ok=True)

    @property
    def db(self):
        return AIOTinyDB(self.PATH)

    async def add_host(self, alias: str, address: str):
        async with self.db as db:
            return db.insert({"alias": alias, "address": address})

    async def remove(self, doc_id: int):
        async with self.db as db:
            return db.remove(doc_ids=[doc_id])

    async def read_all(self):
        async with self.db as db:
            return db.all()

    async def read_one(self, doc_id: int):
        async with self.db as db:
            return db.get(doc_id=doc_id)
