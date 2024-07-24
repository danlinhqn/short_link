import json
import hashlib
from flask import Flask, request, render_template_string, redirect

# Đường dẫn đến tệp JSON
json_file_path = 'data.json'

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

def make_short_link( title, description, image_url, link_url):
    """Tạo liên kết rút gọn."""
    # Tạo mã hash cho URL
    url_hash = hashlib.md5(link_url.encode()).hexdigest()[:6]
    
    # Load dữ liệu hiện tại từ tệp JSON
    data = load_data()

    # Kiểm tra xem mã hash đã tồn tại trong dữ liệu chưa
    if url_hash in data:
        return f"/{url_hash}"

    # Nếu chưa tồn tại, lưu URL và các thuộc tính khác vào dữ liệu
    data[url_hash] = {
        'title': title,
        'description': description,
        'image_url': image_url,
        'link_url': link_url
    }
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
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        link_url = request.form.get('link_url')
        if title and description and image_url and link_url:
            short_link = make_short_link(title, description, image_url, link_url)
        else:
            short_link = "Please enter all fields"
    
    # HTML template cho giao diện web
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tạo Link Bán Hàng & Hình Ảnh</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Tạo Link Bán Hàng & Hình Ảnh</h1>
            <form method="post">
                <label for="title">Tiêu đề:</label>
                <input type="text" id="title" name="title" required>
                <label for="description">Mô tả cơ bản:</label>
                <input type="text" id="description" name="description" required>
                <label for="image_url">Link Hình Ảnh URL:</label>
                <input type="text" id="image_url" name="image_url" required>
                <label for="link_url">Link Sản Phẩm Tiếp Thị Liên Kết:</label>
                <input type="text" id="link_url" name="link_url" required>
                <button type="submit">Bấm Tạo Link</button>
            </form>
            {% if short_link %}
            <div class="result">
                <p class="result-link-label">Link đã được tạo:</p>
                <a href="{{ short_link }}" target="_blank" class="result-link">
                    http://thaoviet.realdealvn.click{{ short_link }}
                </a>
                <div class="result-details">
                    <h2 class="result-title">{{ data[short_link[1:]].title }}</h2>
                    <p class="result-description">{{ data[short_link[1:]].description }}</p>
                    <img src="{{ data[short_link[1:]].image_url }}" alt="{{ data[short_link[1:]].title }}" class="result-image">
                </div>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    '''
    # Load dữ liệu để hiển thị
    data = load_data()
    return render_template_string(html, short_link=short_link, data=data)

@app.route('/<url_hash>')
def redirect_to_url(url_hash):
    """Chuyển hướng đến URL gốc dựa trên mã hash."""
    # Load dữ liệu từ tệp JSON
    data = load_data()

    # Kiểm tra mã hash trong dữ liệu
    item = data.get(url_hash)
    if item:
        return redirect(item['link_url'])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
