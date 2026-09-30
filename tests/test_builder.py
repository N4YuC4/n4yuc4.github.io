import unittest
import os
import tempfile
import json
import time
from build import SiteBuilder, BuildConfig, sync_source_mtime

class TestSiteBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = SiteBuilder()

    def test_convert_markdown_to_html_basic(self):
        md = "# Hello World\n\nThis is a **test**."
        html = self.builder._convert_markdown_to_html(md)
        self.assertIn("<h1>Hello World</h1>", html)
        self.assertIn("<strong>test</strong>", html)

    def test_convert_markdown_to_html_image_png_to_jpg(self):
        md = "![Diagram](/static/images/portfolio-images/screenshot.png)"
        html = self.builder._convert_markdown_to_html(md)
        self.assertIn("/static/images/portfolio-images/screenshot.jpg", html)
        self.assertNotIn("/static/images/portfolio-images/screenshot.png", html)

    def test_remap_image_to_jpg(self):
        self.assertEqual(SiteBuilder._remap_image_to_jpg("images/photo.png"), "images/photo.jpg")
        self.assertEqual(SiteBuilder._remap_image_to_jpg("images/photo.jpg"), "images/photo.jpg")
        self.assertEqual(SiteBuilder._remap_image_to_jpg(""), "")
        self.assertIsNone(SiteBuilder._remap_image_to_jpg(None))

    def test_calculate_canonical_urls(self):
        # Index URLs
        res_en_index = SiteBuilder._calculate_canonical_urls('index.html', 'en')
        self.assertEqual(res_en_index['canonical_url'], f"{BuildConfig.BASE_SITE_URL}/")
        self.assertEqual(res_en_index['canonical_en_url'], f"{BuildConfig.BASE_SITE_URL}/")
        self.assertEqual(res_en_index['canonical_tr_url'], f"{BuildConfig.BASE_SITE_URL}/tr/")

        res_tr_index = SiteBuilder._calculate_canonical_urls('index.html', 'tr')
        self.assertEqual(res_tr_index['canonical_url'], f"{BuildConfig.BASE_SITE_URL}/tr/")

        # Subpage URLs
        res_en_sub = SiteBuilder._calculate_canonical_urls('about.html', 'en')
        self.assertEqual(res_en_sub['canonical_url'], f"{BuildConfig.BASE_SITE_URL}/about.html")
        self.assertEqual(res_en_sub['canonical_tr_url'], f"{BuildConfig.BASE_SITE_URL}/tr/about.html")

    def test_sync_source_mtime(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as src, tempfile.NamedTemporaryFile("w", delete=False) as target:
            src_path = src.name
            target_path = target.name

        try:
            # Set target to past
            past_time = time.time() - 1000
            os.utime(target_path, (past_time, past_time))
            # Touch src
            src_mtime = os.path.getmtime(src_path)
            
            sync_source_mtime(target_path, src_path)
            new_target_mtime = os.path.getmtime(target_path)
            self.assertEqual(int(new_target_mtime), int(src_mtime))
        finally:
            if os.path.exists(src_path):
                os.remove(src_path)
            if os.path.exists(target_path):
                os.remove(target_path)

    def test_read_json_file_existing_and_missing(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump({"test_key": "test_val"}, tmp)
            tmp_path = tmp.name

        try:
            data = self.builder._read_json_file(tmp_path)
            self.assertEqual(data, {"test_key": "test_val"})

            missing_data = self.builder._read_json_file("/non/existent/path/fake.json")
            self.assertIsNone(missing_data)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_read_md_file_existing_and_missing(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
            tmp.write("# Content Sample")
            tmp_path = tmp.name

        try:
            content = self.builder._read_md_file(tmp_path)
            self.assertEqual(content, "# Content Sample")

            missing_content = self.builder._read_md_file("/non/existent/path/fake.md")
            self.assertEqual(missing_content, "")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
