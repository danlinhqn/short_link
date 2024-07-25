from flask import Flask, request, render_template, redirect
import json
import hashlib
import os
from werkzeug.utils import secure_filename
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from dotenv import load_dotenv
import random
import string
from flask import Flask, render_template_string

# Đường dẫn đến tệp JSON
json_file_path = 'data.json'
load_dotenv()

# Cấu hình upload hình ảnh
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def generate_random_string(length=3):
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def make_short_link(title, description, image_url, link_url):
    """Tạo liên kết rút gọn."""
  
    # Tạo mã hash cho URL
    url_hash = hashlib.md5(link_url.encode()).hexdigest()[:3] + generate_random_string()
    
    # Load dữ liệu hiện tại từ tệp JSON
    data = load_data()

    # Kiểm tra xem mã hash đã tồn tại trong dữ liệu chưa
    if url_hash in data:
        return f"/{url_hash}"

    # Nếu chưa tồn tại, lưu URL và các thuộc tính khác vào dữ liệu
    data[url_hash] = {
        'post_link': "https://trum-riviu.realdealvn.click/" + url_hash,
        'title': title,
        'description': description,
        'image_url': image_url,
        'link_url': link_url,
    }
    save_data(data)

    # Tạo link rút gọn
    short_link = f"/{url_hash}"
    return short_link

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
    thumbnail_link = f"https://lh3.googleusercontent.com/d/{file_id}"
    
    return thumbnail_link

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
        if title and description and link_url and 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                try:
                    # Upload hình ảnh lên Google Drive và lấy link thumbnail
                    image_url = upload_image_to_drive(image_path, filename)
                    
                    # Xóa tệp sau khi upload thành công
                    os.remove(image_path)

                    short_link = make_short_link(title, description, image_url, link_url)
     
                except Exception as e:
                    error_message = f"Đã xảy ra lỗi khi tải ảnh lên Google Drive: {e}"
            else:
                error_message = "Loại tệp không hợp lệ"
        else:
            error_message = "Vui lòng nhập tất cả các trường và chọn hình ảnh"

    # Load dữ liệu để hiển thị
    data = load_data()
    return render_template('index.html', short_link=short_link, data=data, error_message=error_message)

# @app.route('/<url_hash>')
# def redirect_to_url(url_hash):
#     """Chuyển hướng đến URL gốc dựa trên mã hash."""
#     # Load dữ liệu từ tệp JSON
#     data = load_data()

#     # Kiểm tra mã hash trong dữ liệu
#     item = data.get(url_hash)
#     if item:
#         return redirect(item['link_url'])
#     else:
#         return "URL not found", 404

@app.route('/<item_id>')
def redirect_to_url_shop_sell_product(item_id):
    
    with open('data.json', 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    # Lấy thông tin theo ID từ URL
    item = data_json.get(item_id)
    
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
        <meta property='og:url' content='{item['post_link']}'>
        <meta property='og:type' content='website'>
        <meta name='twitter:card' content='summary_large_image'>
        <meta name='twitter:title' content='{item['title']}'>
        <meta name='twitter:description' content='{item['description']}'>
        <meta name='twitter:image' content='{item['image_url']}'>
   
    </head>
    <body>
        <p>If you are not redirected automatically, follow this <a href="{{ item['link_url'] }}">link</a>.</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
