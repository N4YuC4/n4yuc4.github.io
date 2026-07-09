import os
import shutil
import json
import markdown
import feedparser
import time
import sys
import re
import requests
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup

# Auto-detect weasyprint; re-execute via venv if needed
try:
    import weasyprint
except ImportError:
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python')
    if os.path.exists(venv_python):
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print("Warning: weasyprint not available. CV PDF will not be generated.")

class BuildConfig:
    """Configuration paths and settings for static site compilation."""
    BUILD_DIR = 'docs'
    TEMPLATES_DIR = 'templates'
    DATA_DIR = 'data'
    STATIC_DIR = 'static'
    PORTFOLIO_CONTENT_DIR = 'portfolio'
    POSTS_REDIRECT_DIR = os.path.join(BUILD_DIR, 'posts')
    MEDIUM_RSS_URL = 'https://medium.com/feed/@n4yuc4'
    LANGUAGES = ['en', 'tr']

class FeedFetcher:
    """Handles fetching and parsing of external RSS feeds."""
    @staticmethod
    def fetch_medium_posts(rss_url, max_posts=5):
        print(f"Fetching Medium posts from: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"Warning: feedparser reported a problem with the feed: {feed.bozo_exception}")

        posts = []
        entries = feed.entries if feed.entries else []
        for entry in entries[:max_posts]:
            try:
                published_date = time.strftime("%d %B %Y", entry.published_parsed)
            except (AttributeError, TypeError):
                published_date = "No date information"

            image_url = None
            content = entry.get('content', [{}])[0].get('value', entry.get('summary', ''))
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                img_tag = soup.find('img')
                if img_tag:
                    image_url = img_tag.get('src')

            posts.append({
                'title': entry.get('title', 'Untitled Post'),
                'link': entry.get('link', '#'),
                'published': published_date,
                'summary': entry.get('summary', ''),
                'imageUrl': image_url
            })
        print(f"Found {len(posts)} posts.")
        return posts

class PublicationMetadataFetcher:
    """Fetches academic publication metadata from Crossref or arXiv APIs with local caching."""
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.cache_dirty = False

    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load publications cache: {e}")
        return {}

    def save_cache(self):
        if self.cache_dirty:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=4)
                print("Publications cache updated.")
                self.cache_dirty = False
            except Exception as e:
                print(f"Warning: Failed to save publications cache: {e}")

    def fetch_metadata(self, url):
        if url in self.cache:
            return self.cache[url]

        print(f"Fetching metadata for: {url}")
        data = {'title': 'Unknown Title', 'authors': 'Unknown Authors', 'abstract': '', 'journal': '', 'year': '', 'link': url}

        try:
            if 'doi.org' in url:
                doi = url.split('doi.org/')[-1]
                response = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10)
                if response.status_code == 200:
                    item = response.json().get('message', {})
                    data['title'] = item.get('title', ['Unknown Title'])[0]
                    authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get('author', [])]
                    data['authors'] = ", ".join(authors)
                    data['journal'] = item.get('container-title', [''])[0]
                    try:
                        data['year'] = str(item.get('published-print', item.get('published-online', {})).get('date-parts', [['']])[0][0])
                    except (IndexError, AttributeError):
                        data['year'] = ''
                    abstract = item.get('abstract', '')
                    if abstract:
                        data['abstract'] = re.sub('<[^<]+?>', '', abstract).strip()
            
            elif 'arxiv.org' in url:
                arxiv_id = url.split('/abs/')[-1].split('/pdf/')[-1]
                response = requests.get(f"http://export.arxiv.org/api/query?id_list={arxiv_id}", timeout=10)
                if response.status_code == 200:
                    root = ET.fromstring(response.text)
                    entry = root.find('{http://www.w3.org/2005/Atom}entry')
                    if entry is not None:
                        title_el = entry.find('{http://www.w3.org/2005/Atom}title')
                        data['title'] = title_el.text.strip().replace('\n', ' ') if title_el is not None else 'Unknown Title'
                        authors = [a.find('{http://www.w3.org/2005/Atom}name').text for a in entry.findall('{http://www.w3.org/2005/Atom}author')]
                        data['authors'] = ", ".join(authors)
                        summary_el = entry.find('{http://www.w3.org/2005/Atom}summary')
                        data['abstract'] = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else ''
                        published_el = entry.find('{http://www.w3.org/2005/Atom}published')
                        data['year'] = published_el.text[:4] if published_el is not None else ''
                        data['journal'] = 'ArXiv'
            
            self.cache[url] = data
            self.cache_dirty = True
            return data
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return data

class PDFGenerator:
    """Handles CV PDF compilation from templates using WeasyPrint with optimization."""
    def __init__(self, jinja_env):
        self.env = jinja_env

    def generate_cv_pdf(self, cv_data, social_links, lang='en', t={}):
        try:
            from weasyprint import HTML
            from PIL import Image as PILImage
            
            project_root = os.path.dirname(os.path.abspath(__file__))
            
            # Pre-optimize profile image
            profile_src = cv_data.get('personalInfo', {}).get('profileImage', '')
            cv_profile_path = None
            if profile_src:
                src_path = os.path.join(project_root, BuildConfig.STATIC_DIR, profile_src)
                if os.path.exists(src_path):
                    cv_profile_path = os.path.join(project_root, BuildConfig.STATIC_DIR, 'images', '_cv_profile.jpg')
                    os.makedirs(os.path.dirname(cv_profile_path), exist_ok=True)
                    with PILImage.open(src_path) as img:
                        img.convert('RGB').save(cv_profile_path, 'JPEG', quality=90, optimize=True)
            
            template = self.env.get_template('cv_pdf.html')
            html_content = template.render({'cv': cv_data, 'socialLinks': social_links, 'lang': lang, 't': t})
            
            if cv_profile_path and profile_src:
                html_content = html_content.replace(
                    f'static/{profile_src}',
                    'static/images/_cv_profile.jpg'
                )
            
            if lang == 'en':
                pdf_path = os.path.join(BuildConfig.BUILD_DIR, 'Nazmi-Yucel-Can_CV_EN.pdf')
            else:
                pdf_path = os.path.join(BuildConfig.BUILD_DIR, lang, f'Nazmi-Yucel-Can_CV_{lang.upper()}.pdf')
                
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            HTML(string=html_content, base_url=project_root).write_pdf(
                pdf_path,
                pdf_tags=True,
                custom_metadata=True,
            )
            
            if cv_profile_path and os.path.exists(cv_profile_path):
                os.remove(cv_profile_path)
            
            self._set_source_mtime(pdf_path, 'templates/cv_pdf.html', 'data/cvData.json', 'data/socialLinks.json')
            pdf_size = os.path.getsize(pdf_path)
            print(f"Generated CV PDF ({lang}): {os.path.relpath(pdf_path)} ({pdf_size / 1024:.0f} KB)")
            return True
        except Exception as e:
            print(f"Warning: CV PDF generation failed for {lang}: {e}")
            return False

    def _set_source_mtime(self, output_path, *extra_sources):
        sources = ['templates/base.html', 'templates/_macros.html'] + list(extra_sources)
        mtimes = [os.path.getmtime(p) for p in sources if os.path.exists(p)]
        mtime = max(mtimes) if mtimes else None
        if mtime:
            os.utime(output_path, (mtime, mtime))

class SiteBuilder:
    """Coordinates and executes the multi-language static site build process."""
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(BuildConfig.TEMPLATES_DIR))
        self.pdf_generator = PDFGenerator(self.env)

    def clean_build_directory(self):
        if os.path.exists(BuildConfig.BUILD_DIR):
            print(f"Cleaning build directory: '{BuildConfig.BUILD_DIR}'")
            for root, dirs, files in os.walk(BuildConfig.BUILD_DIR, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if not name.startswith('.fuse_hidden'):
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            print(f"Warning: Could not remove {file_path}: {e}")
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        os.rmdir(dir_path)
                    except OSError:
                        pass
        os.makedirs(BuildConfig.BUILD_DIR, exist_ok=True)
        print(f"Ensured build directory exists: '{BuildConfig.BUILD_DIR}'")

    def copy_static_assets(self):
        if os.path.exists(BuildConfig.STATIC_DIR):
            shutil.copytree(BuildConfig.STATIC_DIR, os.path.join(BuildConfig.BUILD_DIR, BuildConfig.STATIC_DIR), dirs_exist_ok=True)
            print("Copied 'static' directory.")
            
            try:
                from PIL import Image
                profile_img_path = os.path.join(BuildConfig.BUILD_DIR, 'static', 'images', 'profile.png')
                if os.path.exists(profile_img_path):
                    with Image.open(profile_img_path) as img:
                        img.thumbnail((800, 800))
                        img.save(profile_img_path, optimize=True)
                    print("Optimized profile image.")
            except ImportError:
                print("Pillow not installed. Skipping image optimization.")
            except Exception as e:
                print(f"Warning: Failed to optimize image: {e}")

    def generate_redirect_pages(self):
        print("Generating redirect pages...")
        redirects_file = os.path.join(BuildConfig.DATA_DIR, 'redirects.json')
        redirects_data = self._read_json_file(redirects_file)
        if redirects_data:
            os.makedirs(BuildConfig.POSTS_REDIRECT_DIR, exist_ok=True)
            redirect_template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>This page has moved</title>
    <link rel="canonical" href="{{ url }}"/>
    <meta http-equiv="refresh" content="0; url={{ url }}">
</head>
<body>
    <p>This page has moved. If you are not redirected automatically, follow this <a href="{{ url }}">link</a>.</p>
</body>
</html>
            """
            redirect_template = self.env.from_string(redirect_template_str)
            
            default_url = redirects_data.get('default', '/')
            for slug, new_url in redirects_data.get('posts', {}).items():
                target_url = new_url if new_url else default_url
                html_content = redirect_template.render(url=target_url)
                redirect_path = os.path.join(BuildConfig.POSTS_REDIRECT_DIR, f"{slug}.html")
                with open(redirect_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self._set_source_mtime(redirect_path, redirects_file)
            print(f"Generated {len(redirects_data.get('posts', {}))} redirect pages.")

    def _read_json_file(self, file_path):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}")
        return None

    def _read_md_file(self, file_path):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}")
        return ""

    def _convert_markdown_to_html(self, md_content):
        return markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])

    def _set_source_mtime(self, output_path, *extra_sources):
        sources = ['templates/base.html', 'templates/_macros.html'] + list(extra_sources)
        mtimes = [os.path.getmtime(p) for p in sources if os.path.exists(p)]
        mtime = max(mtimes) if mtimes else None
        if mtime:
            os.utime(output_path, (mtime, mtime))

    def render_template(self, template_name, output_path, context={}, sources=[], output_dir=BuildConfig.BUILD_DIR):
        template = self.env.get_template(template_name)
        html_content = template.render(context)
        
        full_path = os.path.join(output_dir, output_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self._set_source_mtime(full_path, os.path.join(BuildConfig.TEMPLATES_DIR, template_name), *sources)

    def run(self):
        print("Starting static site build...")
        self.clean_build_directory()
        self.copy_static_assets()
        
        with open(os.path.join(BuildConfig.BUILD_DIR, '.nojekyll'), 'w') as f:
            pass

        self.generate_redirect_pages()

        # Load Publications
        pub_urls_file = os.path.join(BuildConfig.DATA_DIR, 'publications.json')
        publication_urls = self._read_json_file(pub_urls_file) or []
        cache_path = os.path.join(BuildConfig.DATA_DIR, '.publications_cache.json')
        pub_fetcher = PublicationMetadataFetcher(cache_path)
        
        publications_items = []
        if publication_urls:
            print(f"Processing {len(publication_urls)} publication links...")
            for url in publication_urls:
                pub_data = pub_fetcher.fetch_metadata(url)
                publications_items.append(pub_data)
            pub_fetcher.save_cache()

        # Load Medium posts
        medium_posts = FeedFetcher.fetch_medium_posts(BuildConfig.MEDIUM_RSS_URL)

        # Load UI Translations
        ui_translations = self._read_json_file(os.path.join(BuildConfig.DATA_DIR, 'translations.json')) or {}

        # Render loop
        for lang in BuildConfig.LANGUAGES:
            print(f"\n--- Building site for language: {lang} ---")
            
            if lang == 'en':
                lang_prefix = ""
                output_dir = BuildConfig.BUILD_DIR
            else:
                lang_prefix = f"/{lang}"
                output_dir = os.path.join(BuildConfig.BUILD_DIR, lang)
                
            os.makedirs(output_dir, exist_ok=True)

            def get_lang_file(filename):
                if lang == 'en':
                    return os.path.join(BuildConfig.DATA_DIR, filename)
                lang_path = os.path.join(BuildConfig.DATA_DIR, lang, filename)
                if os.path.exists(lang_path):
                    return lang_path
                return os.path.join(BuildConfig.DATA_DIR, filename)

            # Read content files with robust fallbacks
            about_data = self._read_json_file(get_lang_file('aboutPageData.json')) or {}
            contact_data = self._read_json_file(get_lang_file('contactPageData.json')) or {}
            privacy_data = self._read_json_file(get_lang_file('privacyPolicyData.json')) or {}
            terms_data = self._read_json_file(get_lang_file('termsOfUseData.json')) or {}
            seo_data = self._read_json_file(get_lang_file('seoData.json')) or {}
            cv_data = self._read_json_file(get_lang_file('cvData.json')) or {}
            social_links = self._read_json_file(get_lang_file('socialLinks.json')) or {}
            portfolio_items = self._read_json_file(get_lang_file('portfolioItems.json')) or []

            # Auto-populate CV with projects and publications
            if cv_data:
                cv_projects = []
                for item in portfolio_items:
                    project = {
                        'title': item.get('title', ''),
                        'description': item.get('description', ''),
                        'techStack': item.get('techStack', ''),
                        'slug': item.get('slug', ''),
                        'links': item.get('links', [])
                    }
                    cv_projects.append(project)
                cv_data['projects'] = cv_projects
                cv_data['publications'] = publications_items

            t = ui_translations.get(lang, {})
            common_context = {
                'lang': lang,
                'lang_prefix': lang_prefix,
                't': t,
                'socialLinks': social_links,
                'build_time': int(time.time())
            }

            def render_lang_template(template_name, output_path, page_context={}, sources=[]):
                full_context = common_context.copy()
                full_context.update(page_context)
                full_context['current_page'] = output_path
                self.render_template(template_name, output_path, full_context, sources=sources, output_dir=output_dir)

            print(f"Rendering templates for {lang}...")
            render_lang_template('home.html', 'index.html', {
                'about': about_data,
                'portfolio': portfolio_items,
                'posts': medium_posts[:3],
                'publications': publications_items[:3],
                'seo': seo_data.get('home', {}),
            }, sources=[get_lang_file('aboutPageData.json'), get_lang_file('portfolioItems.json'), 'data/socialLinks.json', get_lang_file('seoData.json')])
            
            render_lang_template('about.html', 'about.html', {
                'data': about_data,
                'seo': seo_data.get('about', {}),
            }, sources=[get_lang_file('aboutPageData.json'), 'data/socialLinks.json', get_lang_file('seoData.json')])
            
            render_lang_template('contact.html', 'contact.html', {
                'data': contact_data,
                'seo': seo_data.get('contact', {}),
            }, sources=[get_lang_file('contactPageData.json'), 'data/socialLinks.json', get_lang_file('seoData.json')])
            
            render_lang_template('portfolio.html', 'portfolio.html', {
                'items': portfolio_items,
                'seo': seo_data.get('portfolio', {}),
            }, sources=[get_lang_file('portfolioItems.json'), get_lang_file('seoData.json')])
            
            render_lang_template('publications.html', 'publications.html', {
                'items': publications_items,
                'seo': seo_data.get('publications', {}),
            }, sources=['data/publications.json', get_lang_file('seoData.json')])
            
            render_lang_template('blog.html', 'blog.html', {
                'posts': medium_posts,
                'seo': seo_data.get('blog', {}),
            }, sources=[get_lang_file('seoData.json')])

            # Legal pages
            legal_pages = [
                ('privacy', privacy_data, 'privacy-policy-section', get_lang_file('privacyPolicyData.json'), get_lang_file('privacy.md')),
                ('terms', terms_data, 'terms-of-use-section', get_lang_file('termsOfUseData.json'), get_lang_file('terms.md')),
            ]
            for page_key, page_data, section_id, data_json, content_md in legal_pages:
                if page_data and 'contentFile' in page_data:
                    md_content = self._read_md_file(content_md)
                    html_content = self._convert_markdown_to_html(md_content)
                    render_lang_template('_legal_page.html', f'{page_key}.html', {
                        'data': {'title': page_data.get('title', 'Legal Page'), 'content': html_content},
                        'section_id': section_id,
                        'seo': seo_data.get(page_key, {}),
                    }, sources=[data_json, content_md, get_lang_file('seoData.json')])

            # CV PDF
            print(f"Generating CV PDF for {lang}...")
            if cv_data:
                self.pdf_generator.generate_cv_pdf(cv_data, social_links, lang=lang, t=t)

            # Portfolio details
            print(f"Rendering portfolio detail pages for {lang}...")
            for item in portfolio_items:
                slug = item.get('slug')
                md_file_path = item.get('detailFile')
                if slug and md_file_path:
                    if os.path.exists(md_file_path):
                        full_md_path = md_file_path
                    else:
                        fallback_path = os.path.join('portfolio', os.path.basename(md_file_path))
                        print(f"Warning: {md_file_path} not found, falling back to {fallback_path}")
                        full_md_path = fallback_path
                        
                    portfolio_md_content = self._read_md_file(full_md_path)
                    item['content'] = self._convert_markdown_to_html(portfolio_md_content)
                    
                    render_lang_template(
                        'portfolio_detail.html',
                        os.path.join('portfolio', f"{slug}.html"),
                        {'item': item, 'seo': seo_data.get('portfolio', {})},
                        sources=[full_md_path, get_lang_file('portfolioItems.json'), get_lang_file('seoData.json')]
                    )
            print(f"Rendered {len(portfolio_items)} portfolio detail pages for {lang}.")

        # Generate Sitemap programmatically
        print("\nGenerating sitemap...")
        try:
            from sitemap_generator import Sitemap
            Sitemap()
            print("sitemap.xml successfully generated.")
        except Exception as e:
            print(f"Error during sitemap generation: {e}")

        print("\nBuild process complete.")
        print(f"Static site is available in '{BuildConfig.BUILD_DIR}' folder.")

if __name__ == "__main__":
    builder = SiteBuilder()
    builder.run()
