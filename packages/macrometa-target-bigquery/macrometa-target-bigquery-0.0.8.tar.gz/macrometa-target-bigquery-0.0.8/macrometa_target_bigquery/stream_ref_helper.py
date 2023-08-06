import re
from google.cloud import bigquery


class StreamRefHelper:
    def __init__(self,
                 project_id: str,
                 schema_name: str,
                 temp_schema_name: str = None):
        self.project_id = project_id
        self.schema_name = schema_name
        self.temp_schema_name = temp_schema_name if temp_schema_name else schema_name

    @classmethod
    def table_id_from_stream(cls, table_name: str) -> str:
        bad_table_name_chars = '[^a-zA-Z0-9]'
        table_id = re.sub(
                       bad_table_name_chars,
                       '_',
                       table_name
                   ).lower()
        return table_id

    def get_table_ref(self,
                      table_name: str,
                      is_temporary: bool = False) -> bigquery.TableReference:
        # get table id
        table_id = self.table_id_from_stream(table_name)

        project_id = self.project_id
        if is_temporary:
            # change dataset to temp and add suffix to table name
            dataset_id = self.temp_schema_name
            table_id = f'{table_id}_temp'
        else:
            dataset_id = self.schema_name

        table_ref = bigquery.DatasetReference(project_id, dataset_id).table(table_id)
        return table_ref
