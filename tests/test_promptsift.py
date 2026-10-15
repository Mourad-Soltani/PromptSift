"""
Health tests for PromptSift.
Built by Mourad.Soltani
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import promptsift

class TestPromptSift(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.db"
        # Patch DB_PATH
        self.patcher = patch.object(promptsift, "DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_add_and_list(self):
        class Args:
            name = "test-prompt"
            content = "You are a helpful assistant."
        promptsift.cmd_add(Args())
        
        # Capture list
        from io import StringIO
        import contextlib
        f = StringIO()
        with contextlib.redirect_stdout(f):
            promptsift.cmd_list(None)
        output = f.getvalue()
        self.assertIn("test-prompt", output)
        self.assertIn("v1", output)

    def test_update_version(self):
        class Args1:
            name = "test-prompt"
            content = "Version 1"
        promptsift.cmd_add(Args1())
        
        class Args2:
            name = "test-prompt"
            content = "Version 2"
        promptsift.cmd_add(Args2())
        
        from io import StringIO
        import contextlib
        f = StringIO()
        with contextlib.redirect_stdout(f):
            promptsift.cmd_show(Args2())
        output = f.getvalue()
        self.assertIn("Version 2", output)
        self.assertIn("Version: 2", output)

    def test_search(self):
        class Args:
            name = "search-me"
            content = "Find this unique phrase: hello world"
        promptsift.cmd_add(Args())
        
        class SearchArgs:
            query = "unique phrase"
        from io import StringIO
        import contextlib
        f = StringIO()
        with contextlib.redirect_stdout(f):
            promptsift.cmd_search(SearchArgs())
        output = f.getvalue()
        self.assertIn("search-me", output)

    def test_health_db_creation(self):
        conn = promptsift.get_db()
        self.assertTrue(self.db_path.exists())
        conn.close()

if __name__ == "__main__":
    unittest.main()
