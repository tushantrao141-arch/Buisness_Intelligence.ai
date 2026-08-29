"""Streamlit smoke tests that execute every product surface."""

from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StreamlitPageTests(unittest.TestCase):
    def test_every_page_renders_without_exception(self) -> None:
        pages = [PROJECT_ROOT / "app.py", *sorted((PROJECT_ROOT / "pages").glob("*.py"))]
        for page in pages:
            with self.subTest(page=page.name):
                app = AppTest.from_file(str(page), default_timeout=20).run()
                self.assertEqual(list(app.exception), [], f"{page.name}: {list(app.exception)}")


if __name__ == "__main__":
    unittest.main()

