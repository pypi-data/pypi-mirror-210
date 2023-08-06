import unittest
from jupyterlab_training import handlers


class HandlerTest(unittest.TestCase):

    codes_and_result = [
        (
            "import os\nprint(os.path.sep)",
            "\n# flake8: OK",
        ),
        (
            "import os\nprint(os.path.sep)\nprint('OK')\n",
            "\n# flake8: OK",
        ),
        (
            "import os",
            ("\n# flake8: ---------------------------------------"
             "\n# flake8: 1:1: F401 'os' imported but unused"),
        ),
        (
            "print(os.path.sep)",
            ("\n# flake8: ---------------------------------------"
             "\n# flake8: 1:7: F821 undefined name 'os'"),
        ),
        (
            ("print(os.path.sep)"
             "\n# flake8: ---------------------------------------"
             "\n# flake8: 1:7: F821 undefined name 'os'"),
            ""
        ),
    ]

    def test_run_flake8_on_good_code(self):
        for code, result in self.codes_and_result:
            new_code = handlers.run_flake8(code)
            self.assertEqual(new_code, code + result)


if __name__ == '__main__':
    unittest.main()
