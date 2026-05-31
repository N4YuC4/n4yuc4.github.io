import os
import shutil
import json
import markdown
import feedparser
import time
import subprocess
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

# --- CONFIGURATION ---
BUILD_DIR = 'docs'
TEMPLATES_DIR = 'templates'
DATA_DIR = 'data'
STATIC_DIR = 'static'
PORTFOLIO_CONTENT_DIR = 'portfolio'
POSTS_REDIRECT_DIR = os.path.join(BUILD_DIR, 'posts')
MEDIUM_RSS_URL = 'https://medium.com/feed/@n4yuc4'

# --- JINJA2 SETUP ---
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def fetch_medium_posts(rss_url, max_posts=5):
    """Fetches and parses the latest posts from a Medium RSS feed."""
    print(f"Fetching Medium posts from: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        print(f"Warning: feedparser reported a problem with the feed: {feed.bozo_exception}")

    posts = []
    for entry in feed.entries[:max_posts]:
        # Format the date like '27 October 2026'
        try:
            # The 'published_parsed' is a time.struct_time
            published_date = time.strftime("%d %B %Y", entry.published_parsed)
        except AttributeError:
            published_date = "No date information"

        # Try to find an image in the content
        image_url = None
        content = entry.get('content', [{}])[0].get('value', entry.get('summary', ''))
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            img_tag = soup.find('img')
            if img_tag:
                image_url = img_tag.get('src')

        posts.append({
            'title': entry.title,
            'link': entry.link,
            'published': published_date,
            'summary': entry.get('summary', ''),
            'imageUrl': image_url
        })
    print(f"Found {len(posts)} posts.")
    return posts

def _max_mtime(paths):
    mtimes = [os.path.getmtime(p) for p in paths if os.path.exists(p)]
    return max(mtimes) if mtimes else None

def _set_source_mtime(output_path, *extra_sources):
    sources = ['templates/base.html', 'templates/_macros.html'] + list(extra_sources)
    mtime = _max_mtime(sources)
    if mtime:
        os.utime(output_path, (mtime, mtime))

def render_template(template_name, output_path, context={}, sources=[]):
    """Renders a Jinja2 template to a file."""
    template = env.get_template(template_name)
    html_content = template.render(context)
    
    full_path = os.path.join(BUILD_DIR, output_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    _set_source_mtime(full_path, os.path.join(TEMPLATES_DIR, template_name), *sources)

def read_json_file(file_path):
    """Reads and parses a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {file_path}: {e}")
        return None

def read_md_file(file_path):
    """Reads a Markdown file and returns its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error reading {file_path}: File not found.")
        return ""

def convert_markdown_to_html(md_content):
    """Converts a Markdown string to HTML."""
    return markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])

def generate_cv_pdf(cv_data, social_links):
    """Generates docs/Nazmi-Yucel-Can_CV.pdf from the cv_pdf.html template using WeasyPrint."""
    try:
        from weasyprint import HTML
        template = env.get_template('cv_pdf.html')
        html_content = template.render({'cv': cv_data, 'socialLinks': social_links})
        pdf_path = os.path.join(BUILD_DIR, 'Nazmi-Yucel-Can_CV.pdf')
        project_root = os.path.dirname(os.path.abspath(__file__))
        HTML(string=html_content, base_url=project_root).write_pdf(pdf_path)
        _set_source_mtime(pdf_path, 'templates/cv_pdf.html', 'data/cvData.json', 'data/socialLinks.json', 'data/portfolioItems.json', 'data/publications.json', 'data/.publications_cache.json')
        print(f"Generated CV PDF: {os.path.relpath(pdf_path)}")
        return True
    except Exception as e:
        print(f"Warning: CV PDF generation failed: {e}")
        return False

def fetch_publication_metadata(url, cache):
    """Fetches publication metadata from DOI or ArXiv APIs."""
    if url in cache:
        # print(f"Using cached data for: {url}")
        return cache[url]

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
                data['year'] = str(item.get('published-print', item.get('published-online', {})).get('date-parts', [[ '']])[0][0])
                # Crossref abstracts are often absent or in weird XML-like format
                abstract = item.get('abstract', '')
                if abstract:
                    # Remove JATS XML tags if present
                    data['abstract'] = re.sub('<[^<]+?>', '', abstract).strip()
        
        elif 'arxiv.org' in url:
            arxiv_id = url.split('/abs/')[-1].split('/pdf/')[-1]
            response = requests.get(f"http://export.arxiv.org/api/query?id_list={arxiv_id}", timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                entry = root.find('{http://www.w3.org/2005/Atom}entry')
                if entry is not None:
                    data['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
                    authors = [a.find('{http://www.w3.org/2005/Atom}name').text for a in entry.findall('{http://www.w3.org/2005/Atom}author')]
                    data['authors'] = ", ".join(authors)
                    data['abstract'] = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ')
                    data['year'] = entry.find('{http://www.w3.org/2005/Atom}published').text[:4]
                    data['journal'] = 'ArXiv'
        
        cache[url] = data
        return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return data

def build():
    """Main function to build the static site."""
    print("Starting static site build...")

    # 1. Clean and recreate build directory
    if os.path.exists(BUILD_DIR):
        print(f"Cleaning build directory: '{BUILD_DIR}'")
        for root, dirs, files in os.walk(BUILD_DIR, topdown=False):
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
                    # Dirs might not be empty due to .fuse_hidden files
                    pass
    
    os.makedirs(BUILD_DIR, exist_ok=True)
    print(f"Ensured build directory exists: '{BUILD_DIR}'")

    # 2. Copy static files
    if os.path.exists(STATIC_DIR):
        # Using dirs_exist_ok=True to handle cases where directories remain 
        # due to busy files.
        shutil.copytree(STATIC_DIR, os.path.join(BUILD_DIR, 'static'), dirs_exist_ok=True)
        print("Copied 'static' directory.")
        
        # Optimize profile image if it exists
        try:
            from PIL import Image
            profile_img_path = os.path.join(BUILD_DIR, 'static', 'images', 'profile.png')
            if os.path.exists(profile_img_path):
                with Image.open(profile_img_path) as img:
                    img.thumbnail((800, 800))
                    img.save(profile_img_path, optimize=True)
                print("Optimized profile image.")
        except ImportError:
            print("Pillow not installed. Skipping image optimization.")
        except Exception as e:
            print(f"Warning: Failed to optimize image: {e}")

    # 3. Create .nojekyll for GitHub Pages
    with open(os.path.join(BUILD_DIR, '.nojekyll'), 'w') as f:
        pass

    # 4. Generate redirect pages for old blog posts
    print("Generating redirect pages...")
    redirects_data = read_json_file(os.path.join(DATA_DIR, 'redirects.json'))
    if redirects_data:
        os.makedirs(POSTS_REDIRECT_DIR, exist_ok=True)
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
        redirect_template = env.from_string(redirect_template_str)
        
        default_url = redirects_data.get('default', '/')
        for slug, new_url in redirects_data.get('posts', {}).items():
            target_url = new_url if new_url else default_url
            html_content = redirect_template.render(url=target_url)
            redirect_path = os.path.join(POSTS_REDIRECT_DIR, f"{slug}.html")
            with open(redirect_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            _set_source_mtime(redirect_path, os.path.join(DATA_DIR, 'redirects.json'))
        print(f"Generated {len(redirects_data.get('posts', {}))} redirect pages.")

    # 5. Load all data into memory
    print("Loading data from JSON files...")
    portfolio_items = read_json_file(os.path.join(DATA_DIR, 'portfolioItems.json'))
    publication_urls = read_json_file(os.path.join(DATA_DIR, 'publications.json'))
    
    # Cache management for publications
    cache_path = os.path.join(DATA_DIR, '.publications_cache.json')
    publications_cache = read_json_file(cache_path) or {}
    
    publications_items = []
    if publication_urls:
        print(f"Processing {len(publication_urls)} publication links...")
        for url in publication_urls:
            pub_data = fetch_publication_metadata(url, publications_cache)
            publications_items.append(pub_data)
        
        # Save cache back
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(publications_cache, f, ensure_ascii=False, indent=4)

    about_data = read_json_file(os.path.join(DATA_DIR, 'aboutPageData.json')) or {}
    contact_data = read_json_file(os.path.join(DATA_DIR, 'contactPageData.json'))
    privacy_data = read_json_file(os.path.join(DATA_DIR, 'privacyPolicyData.json'))
    terms_data = read_json_file(os.path.join(DATA_DIR, 'termsOfUseData.json'))
    seo_data = read_json_file(os.path.join(DATA_DIR, 'seoData.json'))
    cv_data = read_json_file(os.path.join(DATA_DIR, 'cvData.json'))
    social_links = read_json_file(os.path.join(DATA_DIR, 'socialLinks.json'))
    
    # Auto-populate CV with portfolio items and publications
    if cv_data:
        # Add portfolio items as projects
        if portfolio_items:
            cv_projects = []
            for item in portfolio_items:
                project = {
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'techStack': item.get('techStack', ''),
                    'slug': item.get('slug', ''),
                }
                # Extract GitHub link from the detail markdown
                md_path = item.get('detailFile', '')
                if md_path:
                    md_content = read_md_file(md_path)
                    gh_links = re.findall(r'https://github\.com/\S+', md_content)
                    if gh_links:
                        project['links'] = [{'label': 'GitHub', 'url': gh_links[0]}]
                cv_projects.append(project)
            cv_data['projects'] = cv_projects
        
        # Add publications
        if publications_items:
            cv_data['publications'] = publications_items
    
    # 6. Fetch Medium Posts
    medium_posts = fetch_medium_posts(MEDIUM_RSS_URL)

    # 7. Render main pages
    print("Rendering main pages...")
    render_template('home.html', 'index.html', {
        'about': about_data,
        'portfolio': portfolio_items,
        'posts': medium_posts[:3],
        'publications': publications_items[:3],
        'seo': seo_data.get('home', {}),
        'socialLinks': social_links
    }, sources=['data/aboutPageData.json', 'data/portfolioItems.json', 'data/socialLinks.json', 'data/seoData.json'])
    render_template('about.html', 'about.html', {
        'data': about_data,
        'seo': seo_data.get('about', {}),
        'socialLinks': social_links
    }, sources=['data/aboutPageData.json', 'data/socialLinks.json', 'data/seoData.json'])
    render_template('contact.html', 'contact.html', {
        'data': contact_data,
        'seo': seo_data.get('contact', {}),
        'socialLinks': social_links
    }, sources=['data/contactPageData.json', 'data/socialLinks.json', 'data/seoData.json'])
    render_template('portfolio.html', 'portfolio.html', {
        'items': portfolio_items,
        'seo': seo_data.get('portfolio', {}),
        'socialLinks': social_links
    }, sources=['data/portfolioItems.json', 'data/seoData.json'])
    render_template('publications.html', 'publications.html', {
        'items': publications_items,
        'seo': seo_data.get('publications', {}),
        'socialLinks': social_links
    }, sources=['data/publications.json', 'data/.publications_cache.json', 'data/seoData.json'])
    render_template('blog.html', 'blog.html', {
        'posts': medium_posts,
        'seo': seo_data.get('blog', {}),
        'socialLinks': social_links
    }, sources=['data/seoData.json'])

    legal_pages = [
        ('privacy', privacy_data, 'privacy-policy-section', 'data/privacyPolicyData.json', 'data/privacy.md'),
        ('terms', terms_data, 'terms-of-use-section', 'data/termsOfUseData.json', 'data/terms.md'),
    ]
    for page_key, page_data, section_id, data_json, content_md in legal_pages:
        if page_data and 'contentFile' in page_data:
            md_content = read_md_file(page_data['contentFile'])
            html_content = convert_markdown_to_html(md_content)
            render_template('_legal_page.html', f'{page_key}.html', {
                'data': {'title': page_data['title'], 'content': html_content},
                'section_id': section_id,
                'seo': seo_data.get(page_key, {}),
                'socialLinks': social_links
            }, sources=[data_json, content_md, 'data/seoData.json'])
    
    # 8. Generate CV PDF (no separate CV page anymore)
    print("Generating CV PDF...")
    if cv_data:
        generate_cv_pdf(cv_data, social_links)
    
    # 9. Render portfolio detail pages
    print("Rendering portfolio detail pages...")
    if portfolio_items:
        for item in portfolio_items:
            slug = item.get('slug')
            md_file_path = item.get('detailFile')
            if slug and md_file_path:
                portfolio_md_content = read_md_file(md_file_path)
                item['content'] = convert_markdown_to_html(portfolio_md_content)
                render_template(
                    'portfolio_detail.html',
                    os.path.join('portfolio', f"{slug}.html"),
                    {'item': item, 'seo': seo_data.get('portfolio', {}), 'socialLinks': social_links},
                    sources=[md_file_path, 'data/portfolioItems.json', 'data/seoData.json']
                )
        print(f"Rendered {len(portfolio_items)} portfolio detail pages.")

    # 10. Generate Sitemap
    print("Generating sitemap...")
    try:
        # Use sys.executable to ensure we're using the same python interpreter
        subprocess.run([sys.executable, 'python-sitemap-generator.py'], check=True)
        print("sitemap.xml successfully generated.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error during sitemap generation: {e}")

    # 11. Final message
    print("\nBuild process complete.")
    print(f"Static site is available in '{BUILD_DIR}' folder.")

if __name__ == "__main__":
    build()
