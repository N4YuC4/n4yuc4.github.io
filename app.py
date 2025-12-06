
from flask import Flask, render_template, send_from_directory, request, abort, make_response
import json
import os
from markdown import markdown

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/sitemap.xml')
def sitemap():
    # Dosyayı static klasöründen al
    response = make_response(send_from_directory(app.static_folder, 'sitemap.xml'))
    # Header'ı açıkça XML olarak belirt
    response.headers['Content-Type'] = 'application/xml' 
    return response

@app.route('/robots.txt')
def robots():
    # robots.txt dosyasının static klasöründe olduğundan emin olun
    response = make_response(send_from_directory(app.static_folder, 'robots.txt'))
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/')
def index():
    with open('data/blogPostsMetadata.json', encoding='utf-8') as f:
        posts = json.load(f)
    return render_template('home.html', posts=posts)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('images', 'icon.png')

# CSS statik dosyaları
@app.route('/css/<path:filename>')
def static_css(filename):
    return send_from_directory('css', filename)

# JS statik dosyaları
@app.route('/js/<path:filename>')
def static_js(filename):
    return send_from_directory('js', filename)

# Images statik dosyaları
@app.route('/images/<path:filename>')
def static_images(filename):
    return send_from_directory('images', filename)

# Tekil blog yazısı
@app.route('/posts/<slug>')
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
    html_content = markdown(content, extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    return render_template('post.html', post={'content': html_content, **post})

# Portfolyo listesi
@app.route('/portfolio')
def portfolio_list():
    with open('data/portfolioItems.json', encoding='utf-8') as f:
        items = json.load(f)
    return render_template('portfolio.html', items=items)

# Portfolyo detay
@app.route('/portfolio/<slug>')
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
    html_content = markdown(content, extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    return render_template('portfolio_detail.html', item={'content': html_content, **item})

# Hakkımda sayfası
@app.route('/about')
def about():
    with open('data/aboutPageData.json', encoding='utf-8') as f:
        data = json.load(f)
    # Assuming aboutPageData.json contains a list and we need the first item
    about_data = data[0] if isinstance(data, list) and data else {}
    # Convert markdown content if present
    if 'content' in about_data:
        about_data['content'] = markdown(about_data['content'], extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    return render_template('about.html', about=about_data)

# İletişim sayfası
@app.route('/contact')
def contact():
    with open('data/contactPageData.json', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('contact.html', contact=data)

# Gizlilik Politikası sayfası
@app.route('/privacy')
def privacy():
    with open('data/privacyPolicyData.json', encoding='utf-8') as f:
        data = json.load(f)
    content_path = data['contentFile']
    if not os.path.exists(content_path):
        abort(404)
    with open(content_path, encoding='utf-8') as f_md:
        content = f_md.read()
    html_content = markdown(content, extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    return render_template('privacy.html', privacy={'content': html_content, 'title': data['title']})

# Kullanım Koşulları sayfası
@app.route('/terms')
def terms():
    with open('data/termsOfUseData.json', encoding='utf-8') as f:
        data = json.load(f)
    content_path = data['contentFile']
    if not os.path.exists(content_path):
        abort(404)
    with open(content_path, encoding='utf-8') as f_md:
        content = f_md.read()
    html_content = markdown(content, extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'footnotes', 'attr_list', 'admonition'])
    return render_template('terms.html', terms={'content': html_content, 'title': data['title']})

# Statik dosyalar (CSS, JS, images) - general static folder
@app.route('/static/<path:filename>')
def static_general(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
