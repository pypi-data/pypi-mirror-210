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

import pandas as pd
import logging

from witness.providers.pandas.core import PandasExtractor

log = logging.getLogger(__name__)


class PandasFeatherExtractor(PandasExtractor):
    def extract(self):
        df = pd.read_feather(self.uri)
        setattr(self, "output", df)
        super().extract()

        return self


class PandasExcelExtractor(PandasExtractor):
    def __init__(self, uri, sheet_name=0, header=0, dtype=None):
        self.sheet_name: str or int or None = sheet_name
        self.header: int = header
        self.dtype: str or dict or None = dtype
        super().__init__(uri)

    def extract(self):
        df = pd.read_excel(
            self.uri, sheet_name=self.sheet_name, header=self.header, dtype=self.dtype
        )
        setattr(self, "output", df)
        super().extract()

        return self
