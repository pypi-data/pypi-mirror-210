""" Module w.r.t. Azure table storage logic."""

import asyncio

from azure.data.tables.aio import TableServiceClient

from warpzone.tablestorage.operations import TableOperations


class WarpzoneTableClientAsync:
    """Class to interact with Azure Table asyncronously."""

    def __init__(self, table_service_client: TableServiceClient):
        self._table_service_client = table_service_client

    @classmethod
    def from_connection_string(cls, conn_str: str):
        """Get table client from connection string

        Args:
            conn_str (str): Connection string to table service
        """
        table_service_client = TableServiceClient.from_connection_string(conn_str)
        return cls(table_service_client)

    async def execute_table_operations(
        self,
        table_name: str,
        operations: TableOperations,
    ):
        """Perform table storage operations from a operation set.

        Args:
            table_name (str): Table name
            operations (TableOperations): Iterable of lists of table operations (dicts)
        """
        table_client = self._table_service_client.get_table_client(
            table_name=table_name,
        )
        tasks = []
        async with table_client:
            for batch in operations:
                task = table_client.submit_transaction(batch)
                tasks.append(task)

            await asyncio.gather(*tasks)

    async def query(
        self,
        table_name: str,
        query: str,
    ) -> list[dict]:
        """Retrieve data from Table Storage using linq query

        Args:
            table_name (str): Table name
            query (str): Linq query.

        Returns:
            typing.List[typing.Dict]: List of entities.
        """
        table_client = self._table_service_client.get_table_client(
            table_name=table_name,
        )
        async with table_client:
            async_records = table_client.query_entities(query)
            entities = [entity async for entity in async_records]

        return entities

    async def query_partition(self, table_name: str, partition_key: str) -> list[dict]:
        """Retrieve data from Table Storage using partition key

        Args:
            table_name (str): Table name
            partition_key (str): Partion key.

        Returns:
            typing.List[typing.Dict]: List of entities.
        """
        query = f"PartitionKey eq '{partition_key}'"

        return await self.query(table_name, query)
