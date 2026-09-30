#!/usr/bin/python
"""
Sitemap Generator for static HTML deployment.
Discovers generated HTML pages and builds an XML sitemap adhering to sitemaps.org standards.
"""
import os
from datetime import datetime, timezone
import email.utils as eut
from lxml import etree

BASE_URL = 'https://n4yuc4.github.io/'
SITEMAP_PATH = 'docs/sitemap.xml'


def format_timestamp(timestamp):
    """
    Formats a UNIX epoch timestamp into an ISO 8601 UTC string.
    Example: 1700000000 -> '2023-11-14T22:13:20Z'
    """
    try:
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return _format_date(str(timestamp))
    except Exception:
        return None


def _format_date(datetime_str):
    """Legacy date string formatter using email.utils (kept for backward compatibility)."""
    try:
        parsed = eut.parsedate_tz(datetime_str)
        if parsed is None:
            return None
        y, m, d, h, mi, s, _, _, tz, _ = parsed
        date = f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}"
        if tz is not None:
            return date + ('Z' if tz == 0 else f"{'+' if tz >= 0 else '-'}{abs(tz) // 3600:02d}:{abs(tz) % 3600 // 60:02d}")
        return date
    except Exception:
        return None


class Sitemap:
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'

    def __init__(self, docs_dir='docs', base_url=BASE_URL, sitemap_path=SITEMAP_PATH, auto_build=True):
        self.docs_dir = docs_dir
        self.base_url = base_url
        self.sitemap_path = sitemap_path
        self.sitemap_entries = []

        if auto_build:
            self.build()

    def discover_local_files(self):
        """Discovers HTML files in docs directory excluding static and redirect folders."""
        self.sitemap_entries = []
        exclude_dirs = {
            os.path.join(self.docs_dir, 'posts'),
            os.path.join(self.docs_dir, 'static'),
        }

        if not os.path.exists(self.docs_dir):
            print(f"Error: Directory '{self.docs_dir}' not found.")
            return self.sitemap_entries

        for root, _, files in os.walk(self.docs_dir):
            if root in exclude_dirs:
                continue
            for file in files:
                if not file.endswith('.html'):
                    continue
                path = os.path.relpath(os.path.join(root, file), self.docs_dir)
                url = self.base_url if path == 'index.html' else self.base_url + path
                mtime = os.path.getmtime(os.path.join(root, file))
                self.sitemap_entries.append({'url': url, 'lastmod': mtime})

        return self.sitemap_entries

    def generate_xml_element(self):
        """Constructs an lxml ElementTree for the sitemap."""
        urlset = etree.Element('urlset', xmlns=self.xmlns)
        for entry in self.sitemap_entries:
            url_el = etree.SubElement(urlset, 'url')
            etree.SubElement(url_el, 'loc').text = entry['url']
            formatted_date = format_timestamp(entry['lastmod'])
            etree.SubElement(url_el, 'lastmod').text = formatted_date
            etree.SubElement(url_el, 'changefreq').text = 'weekly'
            etree.SubElement(url_el, 'priority').text = '0.8'
        return urlset

    def save(self):
        """Writes the generated XML sitemap to the configured sitemap_path."""
        urlset = self.generate_xml_element()
        os.makedirs(os.path.dirname(self.sitemap_path), exist_ok=True)
        xml_content = etree.tostring(urlset, pretty_print=True, encoding="unicode", method="xml")
        with open(self.sitemap_path, 'w', encoding='utf-8') as f:
            f.write(xml_content + '\n')
        print('Sitemap saved in:', self.sitemap_path)
        return self.sitemap_path

    def build(self):
        """Convenience method to discover files and write sitemap."""
        self.discover_local_files()
        return self.save()


if __name__ == '__main__':
    Sitemap()
