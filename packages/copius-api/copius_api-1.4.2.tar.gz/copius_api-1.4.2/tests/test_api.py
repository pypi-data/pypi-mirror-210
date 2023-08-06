from copius_api import api
import unittest

class Test1(unittest.TestCase):

    def test_transcribe(self):
        self.assertEqual(api.transcribe("ke̮"), "kɘ")
        self.assertEqual(api.transcribe("lol","kom","lc"), "лол")
        self.assertEqual(api.transcribe("kiki","mns","9c"), "кики")
        self.assertEqual(api.transcribe("буба","mns","c9"), "buba")

if __name__ == "__main__":
    unittest.main()
