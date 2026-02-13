#!/usr/bin/python

# Python Sitemap Generator
# Version: 0.4.2

# Przemek Wiejak
# GitHub: https://github.com/wiejakp/python-sitemap-generator

import os
import time
from urllib.parse import urlparse
import email.utils as eut
from lxml import etree

# sudo apt-get install python-beautifulsoup
# sudo apt-get install python-pip
# sudo apt-get install python3-pip
# pip3 install setuptools
# pip3 install var_dump



# DEFINE YOUR URL - CUSTOM URL!
InitialURL = 'https://n4yuc4.dev/'
InitialURLBase = InitialURL



filename = 'docs/sitemap.xml'








class Sitemap:
    urlset = None
    encoding = 'UTF-8'
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    sitemap_entries = [] # To store {'url': ..., 'lastmod': ...}

    def __init__(self):
        self._discover_local_files()
        self.root()
        self.children()
        self.xml()

    def done(self):
        print ('Done')

    def _discover_local_files(self):
        docs_dir = 'docs'
        posts_redirect_dir = os.path.join(docs_dir, 'posts') # Exclude this directory
        
        if not os.path.exists(docs_dir):
            print(f"Error: Directory '{docs_dir}' not found.")
            return

        for root, _, files in os.walk(docs_dir):
            # Skip the posts_redirect_dir
            if root == posts_redirect_dir:
                continue

            for file in files:
                if file.endswith('.html'):
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, docs_dir)
                    
                    # Construct URL
                    if relative_path == 'index.html':
                        url = InitialURLBase
                    else:
                        url = InitialURLBase + relative_path

                    
                    # Get modification time
                    mod_time_timestamp = os.path.getmtime(local_file_path)
                    
                    self.sitemap_entries.append({
                        'url': url,
                        'lastmod': mod_time_timestamp
                    })



    def root(self):
        self.urlset = etree.Element('urlset')
        self.urlset.attrib['xmlns'] = self.xmlns

    def children(self):
        for entry in self.sitemap_entries:
            url = etree.Element('url')
            loc = etree.Element('loc')
            lastmod = etree.Element('lastmod')
            changefreq = etree.Element('changefreq')
            priority = etree.Element('priority')

            loc.text = entry['url']
            
            # Format the local modification time
            lastmod.text = FormatDate(time.ctime(entry['lastmod'])) # Convert timestamp to string before formatting

            # Add default changefreq and priority
            changefreq.text = 'weekly'
            priority.text = '0.8'

            url.append(loc)
            url.append(lastmod)
            url.append(changefreq)
            url.append(priority)
            
            self.urlset.append(url)

    def xml(self):

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        f = open(filename, 'w')
        
        print (etree.tostring(self.urlset, pretty_print=True, encoding="unicode", method="xml"), file=f)
        f.close()

        print ('Sitemap saved in: ', filename)








def FormatDate(datetime_str):
    parsed_date = eut.parsedate_tz(datetime_str) # Use parsedate_tz for timezone info
    if parsed_date is None:
        return None

    # (year, month, day, hour, minute, second, weekday, dayofyear, tz_offset)
    year, month, day, hour, minute, second, _, _, tz_offset, _ = parsed_date

    # Format date part
    date_part = f"{year:04d}-{month:02d}-{day:02d}"

    # Format time part
    time_part = f"{hour:02d}:{minute:02d}:{second:02d}"

    # Format timezone offset
    if tz_offset is not None:
        if tz_offset == 0:
            tz_part = "Z" # UTC
        else:
            # Convert tz_offset from seconds to hours and minutes
            tz_hours = abs(tz_offset) // 3600
            tz_minutes = (abs(tz_offset) % 3600) // 60
            tz_sign = '+' if tz_offset >= 0 else '-'
            tz_part = f"{tz_sign}{tz_hours:02d}:{tz_minutes:02d}"
    else:
        tz_part = "" # No timezone info

    return f"{date_part}T{time_part}{tz_part}"




Sitemap()
