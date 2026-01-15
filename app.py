
from flask import Flask, render_template, send_from_directory, request, abort, make_response
import json
import os
from markdown import markdown
from PIL import Image

app = Flask(__name__, static_folder='static', template_folder='templates')

THUMBNAIL_DIR = 'static/images/thumbnails'
THUMBNAIL_SIZE = (200, 200) # Default thumbnail size

# Ensure thumbnail directory exists
if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

def generate_thumbnail(image_path, size=THUMBNAIL_SIZE):
    """
    Generates a thumbnail for a given image path.
    Args:
        image_path (str): The path to the original image (e.g., 'static/images/blog-images/image.jpg').
        size (tuple): The desired size of the thumbnail (width, height).
    Returns:
        str: The URL path to the generated thumbnail (e.g., '/static/images/thumbnails/thumb_image.jpg').
             Returns the original image path if thumbnail generation fails or if the image is an SVG.
    """
    if not os.path.exists(image_path):
        print(f"Original image not found: {image_path}")
        return '/' + image_path # Return original path if not found (or a placeholder image URL)

    # For SVG files, return the original path as Pillow doesn't handle them directly for resizing
    if image_path.lower().endswith('.svg'):
        return '/' + image_path

    # Create a unique filename for the thumbnail
    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    thumbnail_filename = f"thumb_{name}_{size[0]}x{size[1]}{ext}"
    thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)
    thumbnail_url = '/' + thumbnail_path.replace('\\', '/') # For URL usage

    if os.path.exists(thumbnail_path):
        return thumbnail_url

    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            # Ensure the thumbnail directory exists before saving
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            img.save(thumbnail_path)
        return thumbnail_url
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return '/' + image_path # Fallback to original image if thumbnail generation fails

@app.route('/sitemap.xml')
def sitemap():
    # Artık build.py dinamik üretiyor ama local dev için static'ten varsa sunsun yoksa 404
    try:
        return send_from_directory('docs', 'sitemap.xml')
    except:
        return "Sitemap build işleminden sonra docs klasöründe oluşacaktır.", 404

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/')
def index():
    # About Verisi
    with open('data/aboutPageData.json', encoding='utf-8') as f:
        about_data_list = json.load(f)
    about_data = about_data_list[0] if isinstance(about_data_list, list) and about_data_list else {}
    if 'content' in about_data:
        html_content = markdown(about_data['content'], extensions=['fenced_code', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
        # Resim yollarını düzelt
        html_content = html_content.replace('src="images/', 'src="/static/images/')
        html_content = html_content.replace('src="../images/', 'src="/static/images/')
        about_data['content'] = html_content

    # Son 3 Blog Yazısı
    with open('data/blogPostsMetadata.json', encoding='utf-8') as f:
        posts = json.load(f)
    for post in posts:
        if 'image' in post and post['image']:
            # Convert URL to file path
            image_file_path = post['image'].lstrip('/')
            post['thumbnail_url'] = generate_thumbnail(image_file_path)
        else:
            post['thumbnail_url'] = '' # No image, no thumbnail
    latest_posts = posts[:3] 

    # Son 3 Portfolyo Öğesi
    with open('data/portfolioItems.json', encoding='utf-8') as f:
        portfolio_items = json.load(f)
    for item in portfolio_items:
        if 'image' in item and item['image']:
            # Convert URL to file path
            image_file_path = item['image'].lstrip('/')
            item['thumbnail_url'] = generate_thumbnail(image_file_path)
        else:
            item['thumbnail_url'] = '' # No image, no thumbnail
    latest_portfolio = portfolio_items[:3]

    return render_template('home.html', about=about_data, posts=latest_posts, portfolio=latest_portfolio)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/images', 'icon.png')

# Tekil blog yazısı
@app.route('/posts/<slug>.html')
def post_detail(slug):
    with open('data/blogPostsMetadata.json', encoding='utf-8') as f:
        posts = json.load(f)
    post = next((p for p in posts if p['slug'] == slug), None)
    if not post:
        abort(404)
    content_path = post['contentFile']
    if not os.path.exists(content_path):
        abort(404)
    with open(content_path, encoding='utf-8') as f:
        content = f.read()
    html_content = markdown(content, extensions=['fenced_code', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    
    # Resim yollarını düzelt
    html_content = html_content.replace('src="images/', 'src="/static/images/')
    html_content = html_content.replace('src="../images/', 'src="/static/images/')
    
    return render_template('post.html', post={'content': html_content, **post})

# Portfolyo listesi
@app.route('/portfolio.html')
def portfolio_list():
    with open('data/portfolioItems.json', encoding='utf-8') as f:
        items = json.load(f)
    for item in items:
        if 'image' in item and item['image']:
            image_file_path = item['image'].lstrip('/')
            item['thumbnail_url'] = generate_thumbnail(image_file_path)
        else:
            item['thumbnail_url'] = ''
    return render_template('portfolio.html', items=items)

# Portfolyo detay
@app.route('/portfolio/<slug>.html')
def portfolio_detail(slug):
    with open('data/portfolioItems.json', encoding='utf-8') as f:
        items = json.load(f)
    item = next((i for i in items if i['slug'] == slug), None)
    if not item:
        abort(404)
    detail_path = item['detailFile']
    if not os.path.exists(detail_path):
        abort(404)
    with open(detail_path, encoding='utf-8') as f:
        content = f.read()
    html_content = markdown(content, extensions=['fenced_code', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    
    # Resim yollarını düzelt
    html_content = html_content.replace('src="images/', 'src="/static/images/')
    html_content = html_content.replace('src="../images/', 'src="/static/images/')
    
    return render_template('portfolio_detail.html', item={'content': html_content, **item})



    # Tüm Blog Yazıları Listesi

@app.route('/blog.html')

def blog_list():

    with open('data/blogPostsMetadata.json', encoding='utf-8') as f:

        posts = json.load(f)

    for post in posts:

        if 'image' in post and post['image']:

            # Convert URL to file path

            image_file_path = post['image'].lstrip('/')

            post['thumbnail_url'] = generate_thumbnail(image_file_path)

        else:

            post['thumbnail_url'] = '' # No image, no thumbnail

    return render_template('blog.html', posts=posts)



# Hakkımda sayfası

@app.route('/about.html')

def about():

    with open('data/aboutPageData.json', encoding='utf-8') as f:

        data = json.load(f)

    about_data = data[0] if isinstance(data, list) and data else {}

    if 'content' in about_data:

        html_content = markdown(about_data['content'], extensions=['fenced_code', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])

        # Resim yollarını düzelt

        html_content = html_content.replace('src="images/', 'src="/static/images/')

        html_content = html_content.replace('src="../images/', 'src="/static/images/')

        about_data['content'] = html_content

        

    return render_template('about.html', about=about_data)



# İletişim sayfası

@app.route('/contact.html')

def contact():

    with open('data/contactPageData.json', encoding='utf-8') as f:

        data = json.load(f)

    return render_template('contact.html', contact=data)



# Gizlilik Politikası sayfası

@app.route('/privacy.html')

def privacy():

    with open('data/privacyPolicyData.json', encoding='utf-8') as f:

        data = json.load(f)

    content_path = data['contentFile']

    if not os.path.exists(content_path):

        abort(404)

    with open(content_path, encoding='utf-8') as f_md:

        content = f_md.read()

    html_content = markdown(content, extensions=['fenced_code', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])

    

    # Resim yollarını düzelt

    html_content = html_content.replace('src="images/', 'src="/static/images/')

    html_content = html_content.replace('src="../images/', 'src="/static/images/')

    

    return render_template('privacy.html', privacy={'content': html_content, 'title': data['title']})



# Kullanım Koşulları sayfası

@app.route('/terms.html')

def terms():

    with open('data/termsOfUseData.json', encoding='utf-8') as f:

        data = json.load(f)

    content_path = data['contentFile']

    if not os.path.exists(content_path):

        abort(404)

    with open(content_path, encoding='utf-8') as f_md:

        content = f_md.read()

    html_content = markdown(content, extensions=['fenced_code', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])

    

    # Resim yollarını düzelt

    html_content = html_content.replace('src="images/', 'src="/static/images/')

    html_content = html_content.replace('src="../images/', 'src="/static/images/')

    

    return render_template('terms.html', terms={'content': html_content, 'title': data['title']})



if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)


