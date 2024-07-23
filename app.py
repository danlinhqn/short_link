import json
import hashlib
from flask import Flask, request, render_template_string, redirect, url_for

# Đường dẫn đến tệp JSON
json_file_path = 'urls.json'

def load_data():
    """Đọc dữ liệu từ tệp JSON."""
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data):
    """Lưu dữ liệu vào tệp JSON."""
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def make_short_link(original_url):
    """Tạo liên kết rút gọn."""
    # Tạo mã hash cho URL
    url_hash = hashlib.md5(original_url.encode()).hexdigest()[:6]
    
    # Load dữ liệu hiện tại từ tệp JSON
    data = load_data()

    # Kiểm tra xem mã hash đã tồn tại trong dữ liệu chưa
    if url_hash in data:
        return f"/{url_hash}"

    # Nếu chưa tồn tại, lưu URL vào dữ liệu
    data[url_hash] = original_url
    save_data(data)
    
    # Tạo link rút gọn
    short_link = f"/{url_hash}"
    return short_link

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Hiển thị giao diện người dùng và xử lý yêu cầu."""
    short_link = ""
    if request.method == 'POST':
        original_url = request.form.get('url')
        if original_url:
            short_link = make_short_link(original_url)
        else:
            short_link = "Please enter a URL"
    
    # HTML template cho giao diện web
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Shortener</title>
    </head>
    <body>
        <h1>URL Shortener</h1>
        <form method="post">
            <label for="url">Enter URL:</label>
            <input type="text" id="url" name="url" required>
            <button type="submit">Generate Short Link</button>
        </form>
        <p>http://thaoviet.realdealvn.click{{ short_link }}</p>
    </body>
    </html>
    '''
    return render_template_string(html, short_link=short_link)

@app.route('/<url_hash>')
def redirect_to_url(url_hash):
    """Chuyển hướng đến URL gốc dựa trên mã hash."""
    # Load dữ liệu từ tệp JSON
    data = load_data()

    # Kiểm tra mã hash trong dữ liệu
    original_url = data.get(url_hash)
    if original_url:
        return redirect(original_url)
    else:
        return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
