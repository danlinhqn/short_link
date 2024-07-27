from flask import Flask, request, render_template, redirect, render_template_string
import json
import os
from werkzeug.utils import secure_filename
from function  import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    """Hiển thị giao diện người dùng và xử lý yêu cầu."""
    short_link = ""
    error_message = None
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        link_url = request.form.get('link_url')
        image = request.files.get('image')

        if title and description and link_url and image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                image.save(image_path)

                # Upload hình ảnh lên Google Drive và lấy link thumbnail
                image_url = upload_image_to_drive(image_path, filename)

                # Xóa tệp sau khi upload thành công
                os.remove(image_path)

                short_link = make_short_link(title, description, image_url, link_url)

            except Exception as e:
                error_message = f"Đã xảy ra lỗi khi tải ảnh lên Google Drive: {e}"
        else:
            error_message = "Vui lòng nhập tất cả các trường và chọn hình ảnh hợp lệ"

    # Load dữ liệu để hiển thị
    data = load_data_from_redis_have_key('short_link', short_link.replace('/', ''))
   
    return render_template('index.html', short_link=short_link, data=data, error_message=error_message)

@app.route('/<item_id>')
def redirect_to_url_shop_sell_product(item_id):
    """Chuyển hướng đến URL dựa trên mã rút gọn."""
    data = load_data_from_redis_with_hash('short_link')
    item_data = data.get(item_id)
    
    if not item_data:
        return "Không tìm thấy thông tin cho ID này", 404

    # Dữ liệu đã được lưu dưới dạng chuỗi JSON, không cần parse lại
    item = json.loads(item_data)
    
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
        <meta property='og:url' content='{item['post_link']}'>
        <meta property='og:type' content='website'>
        <meta name='twitter:card' content='summary_large_image'>
        <meta name='twitter:title' content='{item['title']}'>
        <meta name='twitter:description' content='{item['description']}'>
        <meta name='twitter:image' content='{item['image_url']}'>
    </head>
    <body>
        <script>
            setTimeout(function() {{
                window.location.href = "{item['link_url']}";
            }}); // Chuyển hướng sau 3 giây
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
