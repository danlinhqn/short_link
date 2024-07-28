import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup

app = Flask(__name__)

# Hàm cập nhật các liên kết trong nội dung trang web
def update_links(page_content, base_url):
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Update all anchor tags
    for a in soup.find_all('a', href=True):
        a['href'] = requests.compat.urljoin(base_url, a['href'])
    
    # Update all script tags
    for script in soup.find_all('script', src=True):
        script['src'] = requests.compat.urljoin(base_url, script['src'])
    
    # Update all link tags
    for link in soup.find_all('link', href=True):
        link['href'] = requests.compat.urljoin(base_url, link['href'])
    
    # Update all img tags
    for img in soup.find_all('img', src=True):
        img['src'] = requests.compat.urljoin(base_url, img['src'])

    return str(soup)

# Hàm tải nội dung trang web
def fetch_page_content(page_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(page_url, headers=headers, allow_redirects=False)
        if response.status_code == 200:
            return response.text
        elif response.status_code in (301, 302, 303, 307, 308):
            return f"<h1>Redirected to {response.headers['Location']}</h1>"
        else:
            return None
    except requests.RequestException as e:
        return f"<h1>Failed to fetch page content: {e}</h1>"

# Hàm lấy thông tin trang web (giả định có các hàm này)
def fetch_page_details(page_url):
    # Ví dụ giả định lấy thông tin trang web
    page_title = "Web Page Title"
    og_image = "URL_to_image"
    meta_string = '<meta charset="UTF-8">'
    link_string = '<link rel="stylesheet" href="URL_to_stylesheet">'
    return page_title, og_image, meta_string, link_string

# Hàm render web view qua proxy
@app.route('/view')
def render_web_view_pass_proxy():
    page_url = request.args.get('url')
    if not page_url:
        return "No URL provided", 400
    
    # Thêm giao thức nếu thiếu
    if not page_url.startswith('http://') and not page_url.startswith('https://'):
        page_url = 'http://' + page_url
    
    page_content = fetch_page_content(page_url)
    if not page_content:
        return "Failed to fetch page content", 500
    
    updated_content = update_links(page_content, page_url)
    
    # Lấy thông tin trang web
    page_title, og_image, meta_string, link_string = fetch_page_details(page_url)
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        {meta_string}
        {link_string}
        <title>{page_title}</title>
        <style>
            .content {{
                overflow: auto;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            {updated_content}
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
