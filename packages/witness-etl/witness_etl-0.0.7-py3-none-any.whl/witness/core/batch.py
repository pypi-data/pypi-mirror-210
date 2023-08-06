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

from witness.core.abstract import AbstractBatch
from witness.core.meta import MetaData
from typing import Optional
import pickle
import os


class Batch(AbstractBatch):
    """
    Central class of entire lib.
    Able to store standardized data structure
    containing data in form of records and metadata dictionary.
    """

    __slots__ = ('data', 'meta')

    def __init__(self, data=None, meta=None):

        self.data: Optional[list] = data
        self.meta: Optional[MetaData] = MetaData(**meta) if meta is not None else None
        self.is_restored = False

    def __repr__(self):
        return '{}(meta={}, data={})'.format(self.__class__.__name__, self.meta, self.data)

    def info(self):

        if self.meta is None and self.data is None:
            return 'Batch object is not containing any data.'

        message = 'Batch INFO'

        if self.data is not None:
            number_of_records = len(self.data)
            data_msg = f"""
            --Data--
            Current number of records: {number_of_records}
            """
            message = message + data_msg

        if self.meta is not None:
            meta_msg = f"""--Meta--
            Was {'restored from dump ' + f"{self.meta.dump_uri}" if self.is_restored else 'originally extracted'}
            Source: {self.meta.record_source}
            Extraction datetime: {self.meta.extraction_timestamp}
            """
            message = message + meta_msg

        try:
            message = message + f"Tags: {self.meta.tags}\n"
        except AttributeError:
            pass

        return message

    def fill(self, extractor):
        """
        Fills batch internal datastructures using
        the extractor passed in.
        """

        if extractor.output is not None:
            if extractor.extraction_timestamp is None:
                extractor.set_extraction_timestamp()
            output = extractor.output if extractor.is_unified else extractor.unify().output
        else:
            output = extractor.extract().unify().output
        setattr(self, 'data', output['data'])
        setattr(self, 'meta', MetaData(**output['meta']))
        return self

    def push(self, loader, meta_elements: Optional[list[str]] = None):
        """
        Pushes data, with the appropriate meta attached,
        to the store defined by the loader passed in.
        """
        loader.prepare(self).attach_meta(meta_elements).load()
        return self

    def _register_dump(self, uri: str):
        setattr(self.meta, 'dump_uri', uri)

    def render_dump_name(self, name: Optional[str] = None):
        if name is None:
            root, tail = os.path.split(self.meta.record_source)
            name, ext = os.path.splitext(tail)
        ts_string = self.meta.extraction_timestamp.strftime('%Y-%m-%d_%H-%M-%S_%f')
        dump_name = f'dump_{name}_{ts_string}'
        return dump_name

    def dump(self, uri: Optional[str] = None):
        """
        Dumps batch data to pickle file with defined uri.
        """

        if self.data is None:
            print('Nothing to dump.')
            return None

        if uri is None:
            dump_uri = self.render_dump_name()
        elif os.path.isdir(uri):
            dump_uri = f'{uri}/{self.render_dump_name()}'
        else:
            dump_uri = uri

        with open(dump_uri, 'wb') as file:
            pickle.dump(self.data, file)
        self._register_dump(dump_uri)
        return dump_uri

    def restore(self, uri: Optional[str] = None):
        """
        Fills batch with data from dump.
        If no dump uri provided it'll try search in batch meta.
        """
        uri = self.meta.dump_uri if uri is None else uri
        with open(uri, 'rb') as file:
            output = pickle.load(file)
        setattr(self, 'data', output)
        self.meta.is_restored = True
        return self
