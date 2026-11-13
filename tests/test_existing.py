"""已有接口的核心、边界及错误路径。"""
import unittest,tempfile
from pathlib import Path
from lake.storage import read_source,Objects,digest

class StorageTests(unittest.TestCase):
    def test_source_and_corruption(self):
        value=read_source()
        with tempfile.TemporaryDirectory() as d:
            o=Objects(d);key=o.put(value);self.assertEqual(o.get(key),value)
            self.assertEqual(o.put(value),key)
            Path(d,key).write_bytes(b'bad')
            with self.assertRaises(ValueError):o.get(key)
    def test_bad_object_identity(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):Objects(d).get('../bad')

from lake.checks import evaluate,accepted
from lake.table import Table

class FeatureTests(unittest.TestCase):
    def test_three_values(self):
        e={'op':'ge','field':'qty','value':0}
        self.assertIsNone(evaluate(e,{'qty':None}));self.assertTrue(accepted(e,{'qty':None}));self.assertFalse(accepted(e,{'qty':-1}))
    def test_cas_and_old_images(self):
        t=Table([{'row_id':'a','p':'A','qty':-1}]);old=t.snapshot()
        t.commit(0,'update',row_id='a',values={'qty':2})
        self.assertEqual(old['rows'][0]['qty'],-1);self.assertEqual(t.changes(0,1)[0]['changes'][0]['old']['qty'],-1)
        with self.assertRaises(ValueError):t.commit(0,'delete',row_id='a')
    def test_partition_replace_atomic_error(self):
        t=Table([{'row_id':'a','p':'A'},{'row_id':'b','p':'B'}])
        with self.assertRaises(ValueError):t.commit(0,'replace_partition',field='p',value='A',rows=[{'row_id':'b','p':'A'}])
        self.assertEqual(t.seq,0);self.assertEqual(len(t.snapshot()['rows']),2)
