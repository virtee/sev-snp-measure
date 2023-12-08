#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import unittest
import base64
from sevsnpmeasure import id_block

# Generate test id_key
# openssl ecparam -name secp384r1 -genkey -noout -out keyfile/id_key_test.pem

# Generate test author_key
# openssl ecparam -name secp384r1 -genkey -noout -out keyfile/author_key_test.pem


class TestIdBlock(unittest.TestCase):
    def test_id_block(self):
        ld = base64.b64decode("B28FLQi9p6cAqipgjFyqawDrrSl7bWioWkWx5mmlWLZ+G5HShKMB/mPE+gdQRn7t")
        block = id_block.snp_calc_id_block(
            ld,
            "tests/keyfile/id_key_test.pem",
            "tests/keyfile/author_key_test.pem"
        )
        self.assertIn(
            'id-block=B28FLQi9p6cAqipgjFyqawDrrSl7bWioWkWx5mmlWLZ+G5HShKMB/mPE+gdQRn7t'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAwAAAAAA',
            block
        )
        self.assertIn(
            "id_key_hash: hwt+NcU/inLQ0yL3WrKvgmJ5Kq9leWIs5BMcPyHyied8sFYKXjuQs5MuZ07HCcsU",
            block
        )
        self.assertIn(
            "author_key: YxEcNLv8Ckk4+aAJvQdJgNgXIyPmFZnJ/TNtqGcySOHcqY0L6PdjdqEGuK/UwKBX",
            block
        )
