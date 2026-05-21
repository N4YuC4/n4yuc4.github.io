#!/usr/bin/python
import os
import time
import email.utils as eut
from lxml import etree

BASE_URL = 'https://n4yuc4.dev/'
SITEMAP_PATH = 'docs/sitemap.xml'


class Sitemap:
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'

    def __init__(self):
        self.sitemap_entries = []
        self._discover_local_files()
        self._write_xml()

    def _discover_local_files(self):
        docs_dir = 'docs'
        exclude_dirs = {
            os.path.join(docs_dir, 'posts'),
            os.path.join(docs_dir, 'static'),
        }
        if not os.path.exists(docs_dir):
            print(f"Error: Directory '{docs_dir}' not found.")
            return
        for root, _, files in os.walk(docs_dir):
            if root in exclude_dirs:
                continue
            for file in files:
                if not file.endswith('.html'):
                    continue
                path = os.path.relpath(os.path.join(root, file), docs_dir)
                url = BASE_URL if path == 'index.html' else BASE_URL + path
                mtime = os.path.getmtime(os.path.join(root, file))
                self.sitemap_entries.append({'url': url, 'lastmod': mtime})

    def _write_xml(self):
        urlset = etree.Element('urlset', xmlns=self.xmlns)
        for entry in self.sitemap_entries:
            url_el = etree.SubElement(urlset, 'url')
            etree.SubElement(url_el, 'loc').text = entry['url']
            etree.SubElement(url_el, 'lastmod').text = _format_date(time.ctime(entry['lastmod']))
            etree.SubElement(url_el, 'changefreq').text = 'weekly'
            etree.SubElement(url_el, 'priority').text = '0.8'
        os.makedirs(os.path.dirname(SITEMAP_PATH), exist_ok=True)
        with open(SITEMAP_PATH, 'w') as f:
            print(etree.tostring(urlset, pretty_print=True, encoding="unicode", method="xml"), file=f)
        print('Sitemap saved in:', SITEMAP_PATH)


def _format_date(datetime_str):
    parsed = eut.parsedate_tz(datetime_str)
    if parsed is None:
        return None
    y, m, d, h, mi, s, _, _, tz, _ = parsed
    date = f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}"
    if tz is not None:
        return date + ('Z' if tz == 0 else f"{'+' if tz >= 0 else '-'}{abs(tz) // 3600:02d}:{abs(tz) % 3600 // 60:02d}")
    return date


if __name__ == '__main__':
    Sitemap()
