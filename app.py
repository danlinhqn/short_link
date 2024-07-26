from flask import Flask, request, render_template, redirect, render_template_string
import json
import os
from werkzeug.utils import secure_filename
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from dotenv import load_dotenv
import random
import string
import hashlib
import redis
import time

# Tải biến môi trường từ tệp .env
load_dotenv()

# Cấu hình upload hình ảnh
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Kết nối tới Redis
redis_client = redis.StrictRedis(
    host='54.252.162.111', 
    port=8080, 
    db=15, 
    password='shortlink123456!', 
    decode_responses=True
)

def generate_random_string(length=3):
    """Tạo chuỗi ngẫu nhiên với độ dài được chỉ định."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def load_data_from_redis_with_hash(hash_name):
    """Tải dữ liệu từ Redis DB 15 dưới dạng hash."""
    return redis_client.hgetall(hash_name) or {}

# def load_data_from_redis_have_key(hash_name, key):
#     """Tải dữ liệu từ Redis theo hash_name và key."""
#     data = redis_client.hget(hash_name, key)
#     if data:
#         return json.loads(data)  # Nếu dữ liệu là chuỗi JSON
#     return {}


def load_data_from_redis_have_key(hash_name, key):
    """Tải dữ liệu từ Redis theo hash_name và key và định dạng lại dữ liệu."""
    data = redis_client.hget(hash_name, key)
    
    if data:
        # Chuyển đổi dữ liệu JSON thành từ điển Python
        data_dict = json.loads(data)
        
        # Định dạng lại dữ liệu theo cấu trúc yêu cầu
        formatted_data = {
            key: {
                'post_link': data_dict.get('post_link', ''),
                'title': data_dict.get('title', ''),
                'description': data_dict.get('description', ''),
                'image_url': data_dict.get('image_url', ''),
                'link_url': data_dict.get('link_url', '')
            }
        }
        return formatted_data
    
    return {}

def save_data_to_redis(hash_name, key, value):
    """Lưu dữ liệu vào Redis DB 15 dưới dạng hash."""
    redis_client.hset(hash_name, key, value)

def allowed_file(filename):
    """Kiểm tra xem tệp có phải là loại được phép không."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def make_short_link(title, description, image_url, link_url):
    """Tạo liên kết rút gọn và lưu vào Redis."""
    # Tạo mã hash cho URL
    url_hash = hashlib.md5(link_url.encode()).hexdigest()[:3] + generate_random_string()

    # Kiểm tra xem mã hash đã tồn tại trong dữ liệu chưa
    data = load_data_from_redis_with_hash('short_link')
    if url_hash in data:
        return f"/{url_hash}"

    # Nếu chưa tồn tại, lưu URL và các thuộc tính khác vào dữ liệu
    short_link_data = json.dumps({
        'post_link': f"https://trum-riviu.realdealvn.click/{url_hash}",
        'title': title,
        'description': description,
        'image_url': image_url,
        'link_url': link_url,
    })

    
    save_data_to_redis('short_link', url_hash, short_link_data)

    return f"/{url_hash}"

def upload_image_to_drive(image_path, image_name):
    """Tải hình ảnh lên Google Drive và trả về URL thumbnail."""
    # Đọc nội dung của tệp private_key.pem
    with open('private_key.pem', 'r') as pem_file:
        private_key = pem_file.read()
    
    # Đọc thông tin đăng nhập từ biến môi trường
    service_account_info = {
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }

    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No such file or directory: '{image_path}'")
    
    # Đặt thông tin tệp tin
    file_metadata = {'name': image_name}
    media = MediaFileUpload(image_path, mimetype='image/jpeg')
    
    # Tải tệp tin lên Google Drive
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Lấy ID của tệp tin vừa tải lên
    file_id = file.get('id')
    
    # Cài đặt chia sẻ công khai cho tệp tin
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    # Tạo đường dẫn thumbnail cho hình ảnh
    return f"https://lh3.googleusercontent.com/d/{file_id}"

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
