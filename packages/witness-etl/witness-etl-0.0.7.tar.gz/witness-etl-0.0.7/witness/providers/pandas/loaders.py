#  Copyright (c) 2022.  Eugene Popov.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from witness.providers.pandas.core import PandasLoader
import pandas as pd


class PandasSQLLoader(PandasLoader):
    """
    Loader that uses Pandas DataFrame.to_sql method for loading data.

    :param engine: sqlalchemy engine;
    :param table: name of the destination table;
    :param schema: name of the destination schema, None if not defined.
    """

    def __init__(
        self, engine, table: str, schema: str or None = None, method: str or None = None
    ):
        self.engine = engine
        self.schema = schema
        self.table = table
        self.method = method
        uri = f"{schema}.{table}"
        super().__init__(uri)

    def load(self):
        self.output.to_sql(
            name=self.table,
            con=self.engine,
            schema=self.schema,
            if_exists="append",
            method=self.method,
        )
        return self


class PandasExcelLoader(PandasLoader):
    def __init__(self, uri, sheet_name="Sheet1", add_index=True):

        self.sheet_name = sheet_name
        self.add_index = add_index
        super().__init__(uri)

    def __load_single_sheet(self, **writer_kwargs):
        with pd.ExcelWriter(path=self.uri, **writer_kwargs) as writer:
            self.output.to_excel(
                excel_writer=writer, sheet_name=self.sheet_name, index=self.add_index
            )
        return self

    def __load_multiple_sheets(self, **writer_kwargs):
        with pd.ExcelWriter(path=self.uri, **writer_kwargs) as writer:
            for sheet_name, df in self.output.items():
                df.to_excel(
                    excel_writer=writer,
                    sheet_name=self.sheet_name,
                    index=self.add_index,
                )
        return self

    def load(self, **writer_kwargs):
        if isinstance(self.output, pd.DataFrame):
            return self.__load_single_sheet(**writer_kwargs)
        elif isinstance(self.output, dict):
            return self.__load_multiple_sheets(**writer_kwargs)
        return self


class PandasFeatherLoader(PandasLoader):
    def __init__(self, uri):
        super().__init__(uri)

    def load(self):
        self.output.to_feather(self.uri)
        return self
