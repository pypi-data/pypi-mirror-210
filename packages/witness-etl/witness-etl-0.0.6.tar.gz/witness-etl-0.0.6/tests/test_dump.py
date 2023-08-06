#  Copyright (c) 2023.  Eugene Popov.
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

from tests import files_dir, conftest

default_dump_uri = f'{files_dir}/std_dump'
calibration_meta = conftest.batch_meta
calibration_data = conftest.batch_data


def test_dump(fxtr_batch):
    fxtr_batch.dump(default_dump_uri)

def test_dump_no_uri(fxtr_batch):
    fxtr_batch.dump()
    print(fxtr_batch.meta.dump_uri)

def test_dump_to_dir(fxtr_batch):
    fxtr_batch.dump(files_dir)
    print(fxtr_batch.meta.dump_uri)

def test_restore_no_uri(fxtr_batch):
    fxtr_batch.restore()

def test_attached_meta_after_restore(fxtr_batch):
    fxtr_batch.restore(default_dump_uri)
    assert fxtr_batch.meta.extraction_timestamp == calibration_meta['extraction_timestamp']
    assert fxtr_batch.meta.record_source == calibration_meta['record_source']

def test_persist(fxtr_batch):
    fxtr_batch.dump(default_dump_uri)
    fxtr_batch.restore()
    assert fxtr_batch.meta.record_source == calibration_meta['record_source']
    assert fxtr_batch.meta.extraction_timestamp == calibration_meta['extraction_timestamp']
    assert fxtr_batch.meta.dump_uri == default_dump_uri

def test_render_dump_name(fxtr_batch, fxtr_record_source):
    fxtr_batch.meta.record_source = fxtr_record_source
    dump_name = fxtr_batch.render_dump_name()
    print(dump_name)