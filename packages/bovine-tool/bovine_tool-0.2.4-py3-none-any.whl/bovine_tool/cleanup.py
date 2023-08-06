import asyncio
from tortoise import Tortoise

from .store import InlineBovineStore


async def cleanup():
    async with InlineBovineStore():
        client = Tortoise.get_connection("default")

        sql_query = """
        delete from storedjsonobject
           where object_type='REMOTE'
             and updated < (current_date - interval '3 day')
        """

        await client.execute_query(sql_query)


def main():
    asyncio.run(cleanup())


if __name__ == "__main__":
    main()
