#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['OMARTESTPY4_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['OMARTESTPY4_MONGOALCHEMY_SERVER'] = ''
    os.environ['OMARTESTPY4_MONGOALCHEMY_PORT'] = ''
    os.environ['OMARTESTPY4_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.omartestpy4 import omartestpy4
    from qube.src.services.omartestpy4service import omartestpy4Service
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, omartestpy4ServiceError


class Testomartestpy4Service(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.omartestpy4Service = omartestpy4Service(context)
        self.omartestpy4_api_model = self.createTestModelData()
        self.omartestpy4_data = self.setupDatabaseRecords(self.omartestpy4_api_model)
        self.omartestpy4_someoneelses = \
            self.setupDatabaseRecords(self.omartestpy4_api_model)
        self.omartestpy4_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.omartestpy4_someoneelses.save()
        self.omartestpy4_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.omartestpy4_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.omartestpy4_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, omartestpy4_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            omartestpy4_data = omartestpy4(name='test_record')
            for key in omartestpy4_api_model:
                omartestpy4_data.__setattr__(key, omartestpy4_api_model[key])

            omartestpy4_data.description = 'my short description'
            omartestpy4_data.tenantId = "23432523452345"
            omartestpy4_data.orgId = "987656789765670"
            omartestpy4_data.createdBy = "1009009009988"
            omartestpy4_data.modifiedBy = "1009009009988"
            omartestpy4_data.createDate = str(int(time.time()))
            omartestpy4_data.modifiedDate = str(int(time.time()))
            omartestpy4_data.save()
            return omartestpy4_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_omartestpy4(self, *args, **kwargs):
        result = self.omartestpy4Service.save(self.omartestpy4_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.omartestpy4_api_model['name'])
        omartestpy4.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_omartestpy4(self, *args, **kwargs):
        self.omartestpy4_api_model['name'] = 'modified for put'
        id_to_find = str(self.omartestpy4_data.mongo_id)
        result = self.omartestpy4Service.update(
            self.omartestpy4_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.omartestpy4_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_omartestpy4_description(self, *args, **kwargs):
        self.omartestpy4_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.omartestpy4_data.mongo_id)
        result = self.omartestpy4Service.update(
            self.omartestpy4_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.omartestpy4_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy4_item(self, *args, **kwargs):
        id_to_find = str(self.omartestpy4_data.mongo_id)
        result = self.omartestpy4Service.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy4_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(omartestpy4ServiceError):
            self.omartestpy4Service.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_omartestpy4_list(self, *args, **kwargs):
        result_collection = self.omartestpy4Service.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.omartestpy4_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy4_data.mongo_id)
        with self.assertRaises(omartestpy4ServiceError) as ex:
            self.omartestpy4Service.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy4_data.mongo_id)
        self.omartestpy4Service.auth_context.is_system_user = True
        self.omartestpy4Service.delete(id_to_delete)
        with self.assertRaises(omartestpy4ServiceError) as ex:
            self.omartestpy4Service.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.omartestpy4Service.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.omartestpy4_someoneelses.mongo_id)
        with self.assertRaises(omartestpy4ServiceError):
            self.omartestpy4Service.delete(id_to_delete)
