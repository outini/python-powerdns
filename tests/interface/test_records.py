from unittest import TestCase

from powerdns import RRSet


class TestRRSetRecords(TestCase):

    def test_dict_correct(self):

        rrset = RRSet("test", "TXT", [{"content": "foo"},
                                      {"content": "bar", "disabled": False},
                                      {"content": "baz", "disabled": True}])

        self.assertEqual(rrset["records"][0],
                         {"content": "foo", "disabled": False})
        self.assertEqual(rrset["records"][1],
                         {"content": "bar", "disabled": False})
        self.assertEqual(rrset["records"][2],
                         {"content": "baz", "disabled": True})

    def test_dict_additional_key(self):

        with self.assertRaises(ValueError):
            RRSet("test", "TXT", [{"content": "baz",
                                   "disabled": False,
                                   "foo": "bar"}])

    def test_dict_missing_key(self):

        with self.assertRaises(ValueError):
            RRSet("test", "TXT", [{"content": "baz",
                                   "disabled": False,
                                   "foo": "bar"}])
