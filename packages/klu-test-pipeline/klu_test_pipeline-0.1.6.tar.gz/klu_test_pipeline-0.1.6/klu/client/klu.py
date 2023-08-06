from klu.action.client import ActionsClient
from klu.api.sse_client import SSEClient
from klu.application.client import ApplicationsClient
from klu.data.client import DataClient
from klu.data_index.client import DataIndexClient
from klu.model.client import ModelsClient
from klu.session.client import SessionClient
from klu.workspace.client import WorkspaceClient


class KluClient:
    def __init__(self, api_key: str):
        self.sse_client = SSEClient()

        self.data = DataClient(api_key)
        self.models = ModelsClient(api_key)
        self.actions = ActionsClient(api_key)
        self.sessions = SessionClient(api_key)
        self.workspace = WorkspaceClient(api_key)
        self.data_index = DataIndexClient(api_key)
        self.applications = ApplicationsClient(api_key)
