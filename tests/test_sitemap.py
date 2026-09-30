import unittest
import os
import tempfile
import time
from sitemap_generator import _format_date, format_timestamp, Sitemap, BASE_URL

class TestSitemapGenerator(unittest.TestCase):
    def test_format_timestamp(self):
        # 1700000000 = 2023-11-14T22:13:20Z in UTC
        t = 1700000000
        formatted = format_timestamp(t)
        self.assertEqual(formatted, "2023-11-14T22:13:20Z")

    def test_format_date_legacy_invalid(self):
        self.assertIsNone(_format_date("invalid date string"))

    def test_sitemap_xml_generation_custom_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = os.path.join(tmpdir, "docs")
            os.makedirs(docs_dir, exist_ok=True)
            
            # Create a sample HTML file
            index_path = os.path.join(docs_dir, "index.html")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write("<html><body>Home</body></html>")

            about_path = os.path.join(docs_dir, "about.html")
            with open(about_path, "w", encoding="utf-8") as f:
                f.write("<html><body>About</body></html>")

            # Create an excluded directory
            posts_dir = os.path.join(docs_dir, "posts")
            os.makedirs(posts_dir, exist_ok=True)
            with open(os.path.join(posts_dir, "old-post.html"), "w", encoding="utf-8") as f:
                f.write("<html><body>Old Post</body></html>")

            sitemap_out = os.path.join(tmpdir, "sitemap.xml")
            sitemap = Sitemap(docs_dir=docs_dir, sitemap_path=sitemap_out, auto_build=False)
            entries = sitemap.discover_local_files()

            # Should find index.html and about.html, but NOT old-post.html in posts/
            urls = [e['url'] for e in entries]
            self.assertEqual(len(entries), 2)
            self.assertIn(BASE_URL, urls)
            self.assertIn(f"{BASE_URL}about.html", urls)

            # Test save
            sitemap.save()
            self.assertTrue(os.path.exists(sitemap_out))
            with open(sitemap_out, "r", encoding="utf-8") as f:
                xml_content = f.read()
            self.assertIn("<loc>https://n4yuc4.github.io/</loc>", xml_content)
            self.assertIn("<loc>https://n4yuc4.github.io/about.html</loc>", xml_content)

if __name__ == '__main__':
    unittest.main()
