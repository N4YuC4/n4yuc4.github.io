import os
import shutil
import json
import markdown
import feedparser
import time
import subprocess
import sys
from jinja2 import Environment, FileSystemLoader

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
        # Format the date like '27 Ekim 2025'
        try:
            # The 'published_parsed' is a time.struct_time
            published_date = time.strftime("%d %B %Y", entry.published_parsed)
            # A simple way to translate month names to Turkish
            tr_months = {
                'January': 'Ocak', 'February': 'Şubat', 'March': 'Mart', 'April': 'Nisan',
                'May': 'Mayıs', 'June': 'Haziran', 'July': 'Temmuz', 'August': 'Ağustos',
                'September': 'Eylül', 'October': 'Ekim', 'November': 'Kasım', 'December': 'Aralık'
            }
            for en, tr in tr_months.items():
                published_date = published_date.replace(en, tr)
        except AttributeError:
            published_date = "Tarih bilgisi yok"

        posts.append({
            'title': entry.title,
            'link': entry.link,
            'published': published_date,
            'summary': entry.get('summary', '')
        })
    print(f"Found {len(posts)} posts.")
    return posts

def render_template(template_name, output_path, context={}):
    """Renders a Jinja2 template to a file."""
    template = env.get_template(template_name)
    html_content = template.render(context)
    
    full_path = os.path.join(BUILD_DIR, output_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    # print(f"Rendered: {output_path}")

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

def build():
    """Main function to build the static site."""
    print("Starting static site build...")

    # 1. Clean and recreate build directory
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)
    print(f"Cleaned and created build directory: '{BUILD_DIR}'")

    # 2. Copy static files
    if os.path.exists(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(BUILD_DIR, 'static'))
        print("Copied 'static' directory.")

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
            with open(os.path.join(POSTS_REDIRECT_DIR, f"{slug}.html"), 'w', encoding='utf-8') as f:
                f.write(html_content)
        print(f"Generated {len(redirects_data.get('posts', {}))} redirect pages.")

    # 5. Load all data into memory
    print("Loading data from JSON files...")
    portfolio_items = read_json_file(os.path.join(DATA_DIR, 'portfolioItems.json'))
    about_data_list = read_json_file(os.path.join(DATA_DIR, 'aboutPageData.json'))
    about_data = about_data_list[0] if isinstance(about_data_list, list) and about_data_list else {}
    contact_data = read_json_file(os.path.join(DATA_DIR, 'contactPageData.json'))
    privacy_data = read_json_file(os.path.join(DATA_DIR, 'privacyPolicyData.json'))
    terms_data = read_json_file(os.path.join(DATA_DIR, 'termsOfUseData.json'))
    
    # 6. Fetch Medium Posts
    medium_posts = fetch_medium_posts(MEDIUM_RSS_URL)

    # 7. Render main pages
    print("Rendering main pages...")
    render_template('home.html', 'index.html', {'about': about_data, 'portfolio': portfolio_items})
    render_template('about.html', 'about.html', {'data': about_data})
    render_template('contact.html', 'contact.html', {'data': contact_data})
    render_template('portfolio.html', 'portfolio.html', {'items': portfolio_items})
    render_template('blog.html', 'blog.html', {'posts': medium_posts})

    if privacy_data and 'contentFile' in privacy_data:
        privacy_md_content = read_md_file(privacy_data['contentFile'])
        privacy_html = convert_markdown_to_html(privacy_md_content)
        render_template('privacy.html', 'privacy.html', {'data': {'title': privacy_data['title'], 'content': privacy_html}})

    if terms_data and 'contentFile' in terms_data:
        terms_md_content = read_md_file(terms_data['contentFile'])
        terms_html = convert_markdown_to_html(terms_md_content)
        render_template('terms.html', 'terms.html', {'data': {'title': terms_data['title'], 'content': terms_html}})
    
    # 8. Render portfolio detail pages
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
                    {'item': item}
                )
        print(f"Rendered {len(portfolio_items)} portfolio detail pages.")

    # 9. Generate Sitemap
    print("Generating sitemap...")
    try:
        # Use sys.executable to ensure we're using the same python interpreter
        subprocess.run([sys.executable, 'python-sitemap-generator.py'], check=True)
        print("sitemap.xml successfully generated.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error during sitemap generation: {e}")

    # 10. Final message
    print("\nBuild process complete.")
    print(f"Static site is available in '{BUILD_DIR}' folder.")

if __name__ == "__main__":
    build()
