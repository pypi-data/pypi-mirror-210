""" Module w.r.t. Azure table storage logic."""

from azure.core.exceptions import (
    HttpResponseError,
    ServiceResponseError,
    ServiceResponseTimeoutError,
)
from azure.data.tables import TableServiceClient

from warpzone.healthchecks import HealthCheckResult, HealthStatus
from warpzone.tablestorage.operations import TableOperations


class WarpzoneTableClient:
    """Class to interact with Azure Table"""

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

    def execute_table_operations(
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
        for batch in operations:
            table_client.submit_transaction(batch)

    def query(
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
        entities = [record for record in table_client.query_entities(query)]

        return entities

    def check_health(self) -> HealthCheckResult:
        """
        Pings the connection to the client's associated table storage in Azure.
        """

        try:
            table_iterator = self._table_service_client.list_tables()
            next(table_iterator, None)
        except (
            ServiceResponseError,
            ServiceResponseTimeoutError,
            HttpResponseError,
            # An unhandled bug in Azure causes an AttributeError to be raised
            # when authentication fails. Once fixed, this can be removed.
            # See https://github.com/Azure/azure-sdk-for-python/issues/21416
            AttributeError,
        ) as ex:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                description="Unable to connect to table storage.",
                exception=ex,
            )

        return HealthCheckResult.healthy()
