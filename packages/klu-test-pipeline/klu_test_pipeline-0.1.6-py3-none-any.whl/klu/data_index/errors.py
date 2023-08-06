from klu.common.errors import BaseKluError


class DataIndexNotFoundError(BaseKluError):
    data_index_id: int

    def __init__(self, data_index_id):
        self.data_index_id = data_index_id
        self.message = f"DataIndex with id {data_index_id} was not found."
        super().__init__(self.message)
