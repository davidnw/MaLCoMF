import unittest
from utterance_cache import UtteranceCache
import uuid

class TestUtteranceCache(unittest.TestCase):

    def setUp(self):
        self.uc = UtteranceCache()
        utterace_elements = [
            {'element_name':'Personality', 'element_data':'I am a robot'},
            {'element_name':'Constitution', 'element_data':'It is wrong to use toxic language'}
            ]
        self.test_record_id = self.uc.create(utterace_elements)
        self.assertIsInstance(self.test_record_id,str)
        self.assertEqual(len(self.test_record_id),len(str(uuid.uuid4())))

    def tearDown(self):
        self.uc = None

    def test_create(self):
        utterace_elements = [
            {'element_name':'Personality', 'element_data':'I am a professional footballer'},
            {'element_name':'Constitution', 'element_data':'It is wrong to con the referee'}
            ]
        new_id = self.uc.create(utterace_elements)
        
        unrequested_elements = self.uc.unrequested_elements(new_id)

        self.assertEqual(len(unrequested_elements), 2)
        self.assertIn('Personality', unrequested_elements)
        self.assertIn('Constitution', unrequested_elements)

        # Test create an empty record
        empty_id = self.uc.create()
        unrequested_elements = self.uc.unrequested_elements(empty_id)
        self.assertEqual(len(unrequested_elements), 0)
       
        

    def test_unrequested_elements(self):
        unrequested_elements = self.uc.unrequested_elements(self.test_record_id)
        self.assertEqual(len(unrequested_elements), 2)
        self.assertIn('Personality',unrequested_elements)
        self.assertIn('Constitution',unrequested_elements)


    def test_requested_elements(self):
        requested_elements = self.uc.requested_elements(self.test_record_id)
        self.assertEqual(len(requested_elements), 0)

        self.uc.mark_requested(self.test_record_id,['Personality'])
        requested_elements = self.uc.requested_elements(self.test_record_id)
        self.assertEqual(len(requested_elements), 1)

        unrequested_elements = self.uc.unrequested_elements(self.test_record_id)
        self.assertEqual(len(unrequested_elements), 1)
        self.assertNotIn('Personality',unrequested_elements)


    def test_add_recieved_data(self):
       
        new_data = {'Personality':'I am a clown'}
        self.uc.add_recieved_data(self.test_record_id, new_data)

        received_elements = self.uc.received_elements(self.test_record_id)

        self.assertEqual(len(received_elements), 1)
        self.assertEqual(received_elements[0], 'Personality')

        new_data = {'Constitution':'It is wrong to scare children', 'Context':'Interesting Context'}
        self.uc.add_recieved_data(self.test_record_id, new_data)

        received_elements = self.uc.received_elements(self.test_record_id)
        self.assertEqual(len(received_elements),3)

        new_key_data = {'a_new_key':'some_new_key_data'}
        self.uc.add_recieved_data(self.test_record_id, new_key_data)

        received_elements = self.uc.received_elements(self.test_record_id)
        self.assertEqual(len(received_elements),4)
        received_data = self.uc.recieved_element_data(self.test_record_id,['a_new_key'])
        self.assertEqual(len(received_data),1)
        self.assertTrue(received_data['a_new_key'] == 'some_new_key_data')


    def test_mark_requested(self):
        requested_to_mark = ['Personality', 'Another_Element']
        self.uc.mark_requested(self.test_record_id,requested_to_mark)
        cached_requested = self.uc.requested_elements(self.test_record_id)

        self.assertEqual(len(cached_requested), 2)
        self.assertIn('Personality', cached_requested)
        self.assertIn('Another_Element', cached_requested)


    def test_recieved_element_data(self):

        new_data = {'Personality':'I am a clown', 'Constitution':'It is wrong to scare children'}
        self.uc.add_recieved_data(self.test_record_id, new_data)
        

        requested_data = self.uc.recieved_element_data(self.test_record_id, ['Personality'])
        self.assertEqual(len(requested_data), 1)
        self.assertEqual(requested_data['Personality'], 'I am a clown')

        # Test return all data
        requested_data = self.uc.recieved_element_data(self.test_record_id)
        self.assertEqual(len(requested_data), 2)



    def test_element_data2(self):
        new_data = {'Personality':'I am a clown', 'Consitution':'It is wrong to scare children'}
        self.uc.add_recieved_data(self.test_record_id, new_data)
        received_elements = self.uc.received_elements(self.test_record_id)
        self.assertEqual(len(received_elements), 2)

        requested_data = self.uc.recieved_element_data(self.test_record_id, ['Personality', 'Consitution'])
        self.assertEqual(len(requested_data), 2)
        self.assertEqual(requested_data['Personality'], 'I am a clown')
        self.assertEqual(requested_data['Consitution'], 'It is wrong to scare children')

# test the meta data part of the cache

    def test_add_requester_id(self):
        self.uc.add_requester_id(self.test_record_id, 'some_id_1')
        id = self.uc.get_requester_id(self.test_record_id)

        print(f'meta data: {self.uc.meta_data}')

        self.assertEqual(id, 'some_id_1')

    def test_add_context(self):
        context = {'name':'fred', 'aim':'bake a cake'}
        self.uc.add_context(self.test_record_id,context)
        returned_context = self.uc.get_context(self.test_record_id)
        self.assertEqual(returned_context,context)

    def test_add_context_meta_exists(self):
        self.uc.add_requester_id(self.test_record_id, 'some_id_1')
        id = self.uc.get_requester_id(self.test_record_id)
        self.assertEqual(id, 'some_id_1')

        context = {'name':'fred', 'aim':'bake a cake'}
        self.uc.add_context(self.test_record_id,context)
        returned_context = self.uc.get_context(self.test_record_id)
        self.assertEqual(returned_context,context)

    def test_add_requester_id_meta_exists(self):
        context = {'name':'fred', 'aim':'bake a cake'}
        self.uc.add_context(self.test_record_id,context)
        returned_context = self.uc.get_context(self.test_record_id)
        self.assertEqual(returned_context,context)

        self.uc.add_requester_id(self.test_record_id, 'some_id_1')
        id = self.uc.get_requester_id(self.test_record_id)
        self.assertEqual(id, 'some_id_1')

    def test_delete_meta(self):
        context = {'name':'fred', 'aim':'bake a cake'}
        self.uc.add_context(self.test_record_id,context)
        returned_context = self.uc.get_context(self.test_record_id)
        self.assertEqual(returned_context,context)

        self.uc.delete_meta(self.test_record_id)

        returned_context = self.uc.get_context(self.test_record_id)
        self.assertEqual(returned_context,None)



if __name__ == '__main__':
    unittest.main()