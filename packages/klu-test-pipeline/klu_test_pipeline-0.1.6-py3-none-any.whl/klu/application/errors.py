from klu.common.errors import BaseKluError


class ApplicationNotFoundError(BaseKluError):
    application_id: str

    def __init__(self, application_id):
        self.application_id = application_id
        self.message = f"Application with id {application_id} was not found."
        super().__init__(self.message)
