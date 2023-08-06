"""
    This module will build the client
"""
from reva.lib.client.graphql_client import GraphQlClient

class ClientBuilder:
    """
        This class build the client
    """
    def __init__(self, conf : dict):
        self.conf = conf

    def graphql_client(self):
        """
            This function return the grqphql client
        """
        return GraphQlClient(self.conf).get_client()
