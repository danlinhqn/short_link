from flask import Flask, render_template_string
import json

# App này là phụ trách xử lý chuyển link qua shop muốn và tạo hình ảnh cho link khi post bài lên facebook
app = Flask(__name__)

# Đọc dữ liệu từ file JSON
with open('create_link/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

@app.route('/<item_id>')
def index(item_id):
    # Lấy thông tin theo ID từ URL
    item = data.get(item_id)
    
    # Kiểm tra nếu item tồn tại
    if not item:
        return "Không tìm thấy thông tin cho ID này", 404
    
    # Tạo nội dung HTML với dữ liệu từ item
    html_content = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>{item['title']}</title>
        <meta property='og:title' content='{item['title']}'>
        <meta property='og:description' content='{item['description']}'>
        <meta property='og:image' content='{item['image_url']}'>
        <meta property='og:url' content='{item['link_url']}'>
        <meta property='og:type' content='website'>
        <meta name='twitter:card' content='summary_large_image'>
        <meta name='twitter:title' content='{item['title']}'>
        <meta name='twitter:description' content='{item['description']}'>
        <meta name='twitter:image' content='{item['image_url']}'>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                window.location.href = "{item['link_url']}";
            }});
        </script>
    </head>
    <body>
     
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
