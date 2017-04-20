#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class Testomartestpy4Model(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_omartestpy4_model(self):
        from qube.src.models.omartestpy4 import omartestpy4
        omartestpy4_data = omartestpy4(name='testname')
        omartestpy4_data.tenantId = "23432523452345"
        omartestpy4_data.orgId = "987656789765670"
        omartestpy4_data.createdBy = "1009009009988"
        omartestpy4_data.modifiedBy = "1009009009988"
        omartestpy4_data.createDate = str(int(time.time()))
        omartestpy4_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            omartestpy4_data.save()
            self.assertIsNotNone(omartestpy4_data.mongo_id)
            omartestpy4_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
