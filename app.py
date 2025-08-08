
from flask import Flask, jsonify, send_from_directory, request
import json
import os
from markdown import markdown

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('images', 'icon.png')

# CSS statik dosyaları
@app.route('/css/<path:filename>')
def css_static(filename):
    return send_from_directory('css', filename)

# JS statik dosyaları
@app.route('/js/<path:filename>')
def js_static(filename):
    return send_from_directory('js', filename)

# Sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

# Robots.txt
@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')

# Images statik dosyaları
@app.route('/images/<path:filename>')
def images_static(filename):
    return send_from_directory('images', filename)

# Blog yazıları metadata
@app.route('/api/posts')
def get_posts():
    with open('data/blogPostsMetadata.json', encoding='utf-8') as f:
        posts = json.load(f)
    return jsonify(posts)

# Tekil blog yazısı (markdown içeriğiyle birlikte)
@app.route('/api/posts/<slug>')
def get_post_content(slug):
    with open('data/blogPostsMetadata.json', encoding='utf-8') as f:
        posts = json.load(f)
    post = next((p for p in posts if p['slug'] == slug), None)
    if not post:
        return jsonify({'error': 'Not found'}), 404
    content_path = post['contentFile']
    if not os.path.exists(content_path):
        return jsonify({'error': 'Content file not found'}), 404
    with open(content_path, encoding='utf-8') as f:
        content = f.read()
    html_content = markdown(content, extensions=['fenced_code', 'codehilite'])
    return jsonify({'content': html_content, **post})

# Portfolyo verileri
@app.route('/api/portfolio')
def get_portfolio():
    with open('data/portfolioItems.json', encoding='utf-8') as f:
        items = json.load(f)
    return jsonify(items)

# Portfolyo detay (markdown)
@app.route('/api/portfolio/<slug>')
def get_portfolio_detail(slug):
    with open('data/portfolioItems.json', encoding='utf-8') as f:
        items = json.load(f)
    item = next((i for i in items if i['slug'] == slug), None)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    detail_path = item['detailFile']
    if not os.path.exists(detail_path):
        return jsonify({'error': 'Detail file not found'}), 404
    with open(detail_path, encoding='utf-8') as f:
        content = f.read()
    html_content = markdown(content, extensions=['fenced_code', 'codehilite'])
    return jsonify({'content': html_content, **item})

# Hakkımda, iletişim, gizlilik, kullanım koşulları (JS dosyalarındaki dict'ler Python'a taşınmalı)
@app.route('/api/about')
def get_about():
    with open('data/aboutPageData.json', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/contact')
def get_contact():
    with open('data/contactPageData.json', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/privacy')
def get_privacy():
    with open('data/privacyPolicyData.json', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/terms')
def get_terms():
    with open('data/termsOfUseData.json', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

# Statik dosyalar (CSS, JS, images)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
