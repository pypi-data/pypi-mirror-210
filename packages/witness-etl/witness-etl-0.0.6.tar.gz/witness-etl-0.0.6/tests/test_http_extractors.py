

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

import httpretty

from witness import Batch

httpretty.enable(verbose=True, allow_net_connect=False)

def register_fxtr_uri(fxtr):
    httpretty.register_uri(
        method=httpretty.GET,
        uri=fxtr['uri'],
        body=fxtr['body'],
        status=fxtr['status'],
        content_type=fxtr['content_type']
    )

@httpretty.activate
def test_extract(fxtr_extractor, fxtr_get_uri):
    register_fxtr_uri(fxtr_get_uri)
    extractor = fxtr_extractor(uri=fxtr_get_uri['uri'])
    extractor.extract()


@httpretty.activate
def test_serialize_to_batch(fxtr_extractor, fxtr_get_uri, fxtr_web_serializer):
    serializer = fxtr_web_serializer()
    register_fxtr_uri(fxtr_get_uri)
    extractor = fxtr_extractor(uri=fxtr_get_uri['uri'], serializer=serializer)
    serialized_output = extractor.extract().unify().output
    print(f'Raw output: {extractor.output}')
    assert serialized_output['data'] == {'success': True}


@httpretty.activate
def test_unify(fxtr_extractor, fxtr_get_uri):
    register_fxtr_uri(fxtr_get_uri)
    extractor = fxtr_extractor(uri=fxtr_get_uri['uri'])
    extractor.extract().unify()
    assert extractor.is_unified


@httpretty.activate
def test_fill_batch_with_full_extractor(fxtr_extractor, fxtr_get_uri):
    register_fxtr_uri(fxtr_get_uri)
    full_extractor = fxtr_extractor(uri=fxtr_get_uri['uri']).extract()
    assert full_extractor.is_unified == False
    full_extractor.unify()
    assert full_extractor.output is not None
    print(full_extractor.output)
    batch = Batch()
    batch.fill(extractor=full_extractor)
    assert batch.data == full_extractor.output['data']
    assert full_extractor.output['meta'] in batch.meta
    assert batch.meta['extraction_timestamp'] is not None

