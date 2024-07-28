from flask import Flask, request, render_template_string, make_response, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_page_content(page_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    proxy_url = f'http://localhost:5000/proxy?url={page_url}'
    try:
        response = requests.get(proxy_url, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            return response.text
        elif response.status_code in [301, 302, 303, 307, 308]:
            new_url = response.headers['Location']
            return fetch_page_content(new_url)
        else:
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def update_links(page_content, base_url):
    soup = BeautifulSoup(page_content, 'html.parser')
    
    for a in soup.find_all('a', href=True):
        a['href'] = requests.compat.urljoin(base_url, a['href'])
    
    for script in soup.find_all('script', src=True):
        script['src'] = requests.compat.urljoin(base_url, script['src'])
    
    for link in soup.find_all('link', href=True):
        link['href'] = requests.compat.urljoin(base_url, link['href'])
    
    for img in soup.find_all('img', src=True):
        img['src'] = requests.compat.urljoin(base_url, img['src'])

    return str(soup)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "URL parameter is required", 400

    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        response_headers = {key: value for key, value in response.headers.items() if key.lower() != 'transfer-encoding'}
        flask_response = Response(generate(), status=response.status_code, headers=response_headers)
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        return flask_response
    except Exception as e:
        return str(e), 500

@app.route('/render_web_view_pass_proxy')
def render_web_view_pass_proxy():
    page_url = request.args.get('url')
    
    if not page_url:
        return "No URL provided", 400
    
    page_title, og_image, meta_string, link_string = fetch_page_details(page_url)
    
    page_content = fetch_page_content(page_url)
    if not page_content:
        return "Failed to fetch page content", 500
    
    updated_content = update_links(page_content, page_url)
    
    response = make_response(render_template_string(f"""
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
    """))
    
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

def fetch_page_details(page_url):
    page_title = "Sample Title"
    og_image = ""
    meta_string = ""
    link_string = ""
    return page_title, og_image, meta_string, link_string

if __name__ == '__main__':
    app.run(debug=True)
