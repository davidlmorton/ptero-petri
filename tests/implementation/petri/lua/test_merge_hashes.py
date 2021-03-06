from ..helpers import script_test
from ...redishelpers import redistest
import copy
import unittest


class TestMergeHashesScript(redistest.RedisTest, script_test.ScriptTest):
    SCRIPT_NAME = 'merge_hashes'

    def setUp(self):
        redistest.RedisTest.setUp(self)
        script_test.ScriptTest.setUp(self)

    def test_single_source(self):
        dest_key = 'd'
        src_key = 's'

        data = {'a': '1', 'b': '2', 'c': '3'}
        self.conn.hmset(src_key, data)

        rv = self.script(keys=[dest_key, src_key])
        self.assertEqual(0, rv[0])
        self.assertEqual(data, self.conn.hgetall(dest_key))

    def test_multiple_sources_no_conflicts(self):
        dest_key = 'd'
        src_key_0 = 's0'
        src_key_1 = 's1'

        data_0 = {'a': '1', 'c': '3'}
        data_1 = {'b': '2'}
        self.conn.hmset(src_key_0, data_0)
        self.conn.hmset(src_key_1, data_1)

        rv = self.script(keys=[dest_key, src_key_0, src_key_1])

        expected_result = copy.copy(data_0)
        expected_result.update(data_1)
        self.assertEqual(0, rv[0])
        self.assertEqual(expected_result, self.conn.hgetall(dest_key))

    def test_multiple_empty_data(self):
        dest_key = 'd'
        src_key_0 = 's0'
        src_key_1 = 's1'

        data_0 = {'a': {}}
        data_1 = {'a': {}}
        self.conn.hmset(src_key_0, data_0)
        self.conn.hmset(src_key_1, data_1)

        rv = self.script(keys=[dest_key, src_key_0, src_key_1])

        expected_result = {'a': '{}'}
        self.assertEqual(0, rv[0])
        self.assertEqual(expected_result, self.conn.hgetall(dest_key))

    def test_multiple_sources_with_conflict(self):
        dest_key = 'd'
        src_key_0 = 's0'
        src_key_1 = 's1'

        data_0 = {'a': '1', 'c': '3'}
        data_1 = {'b': '2', 'c': '4'}
        self.conn.hmset(src_key_0, data_0)
        self.conn.hmset(src_key_1, data_1)

        rv = self.script(keys=[dest_key, src_key_0, src_key_1])
        self.assertEqual(-1, rv[0])


if __name__ == "__main__":
    unittest.main()
