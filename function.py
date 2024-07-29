import json
import os
from bs4 import BeautifulSoup
import requests
from werkzeug.utils import secure_filename
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from dotenv import load_dotenv
import random
import string
import hashlib
import redis
import re
from flask import Flask, render_template_string
from flask import Flask, jsonify, request, render_template, redirect, render_template_string, url_for
import json
import os
import requests
from flask_caching import Cache

# Cấu hình cache + flask
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Cấu hình upload hình ảnh
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Tải biến môi trường từ tệp .env
load_dotenv()

# Kết nối tới Redis
redis_client_15 = redis.StrictRedis(
    host='54.252.162.111', 
    port=8080, 
    db=15, 
    password='shortlink123456!', 
    decode_responses=True
)

# Kết nối tới Redis
redis_client_14 = redis.StrictRedis(
    host='54.252.162.111', 
    port=8080, 
    db=14, 
    password='shortlink123456!', 
    decode_responses=True
)

# Hàm tạo chuỗi ngẫu nhiên
def generate_random_string(length=3):
    """Tạo chuỗi ngẫu nhiên với độ dài được chỉ định."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

# Hàm tải dữ liệu từ Redis
def load_data_from_redis_with_hash(hash_name):
    """Tải dữ liệu từ Redis DB 15 dưới dạng hash."""
    return redis_client_15.hgetall(hash_name) or {}

# Hàm tải dữ liệu từ Redis theo hash_name và key
def load_data_from_redis_have_key(hash_name, key):
    """Tải dữ liệu từ Redis theo hash_name và key và định dạng lại dữ liệu."""
    data = redis_client_15.hget(hash_name, key)
    
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

# Hàm lưu dữ liệu vào Redis
def save_data_to_redis(hash_name, key, value):
    """Lưu dữ liệu vào Redis DB 15 dưới dạng hash."""
    redis_client_15.hset(hash_name, key, value)
    
# Hàm lưu dữ liệu vào Redis
def save_data_to_redis_register_domain(hash_name, key, value):
    """Lưu dữ liệu vào Redis DB 15 dưới dạng hash."""
    if redis_client_15.hexists(hash_name, key):
        return False  # Key already exists
    redis_client_15.hset(hash_name, key, json.dumps(value))
    return True  # Key successfully added

# Hàm lưu dữ liệu vào Redis
def save_data_to_redis_register_sub_shop(hash_name, key, value):
    """Lưu dữ liệu vào Redis DB 15 dưới dạng hash."""
    if redis_client_15.hexists(hash_name, key):
        return False  # Key already exists
    redis_client_14.hset(hash_name, key, json.dumps(value))
    return True  # Key successfully added

# Hàm kiểm tra key trong hash
def check_key_in_hash_db_15(hash_name, key):
    """Kiểm tra giá trị của key trong một hash trong Redis."""
    return redis_client_15.hexists(hash_name, key)

# Kiểm tra xem tệp có phải là loại được phép không.
def allowed_file(filename):
    """Kiểm tra xem tệp có phải là loại được phép không."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hàm tạo liên kết rút gọn
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

# Hàm tải hình ảnh lên Google Drive
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

# Hàm xử lý URL clear
def clean_url(url):
    """Loại bỏ các phần tử như https://, http://, và www. khỏi URL."""
    # Sử dụng regex để loại bỏ các phần tử không mong muốn
    cleaned_url = re.sub(r'^https?://(www\.)?', '', url)
    return cleaned_url

# Lấy tất cả các key trong một hash từ Redis và trả về dưới dạng một danh sách.
def get_keys_in_hash(hash_name):
    """Lấy tất cả các key trong một hash từ Redis và trả về dưới dạng một danh sách."""
    return redis_client_14.hkeys(hash_name)

# Hàm kiểm tra hash có tồn tại hay không
def check_hash_exists_db_14(hash_name):
    """Kiểm tra xem một hash có tồn tại trong Redis hay không."""
    return redis_client_14.exists(hash_name)

# Hàm kiểm tra số lượng key trong hash
def count_keys_in_hash(hash_name):
    """Đếm số lượng key trong hash Redis."""
    try:
        key_count = redis_client_14.hlen(hash_name)
        return key_count
    except Exception as e:
        print(f"Lỗi khi đếm số lượng key trong hash: {e}")
        return None

# Lấy giá trị của 'shop_link' từ một hash trong Redis.
def get_shop_link_from_hash_db_15(hash_name, key):
    """
    Lấy giá trị của 'shop_link' từ một hash trong Redis.

    :param hash_name: Tên của hash trong Redis.
    :param key: Key trong hash.
    :return: Giá trị của 'shop_link' nếu tồn tại, ngược lại trả về None.
    """
    value = redis_client_15.hget(hash_name, key)
    
    if value:
        value_dict = json.loads(value)
        return value_dict.get("shop_link")
    
    return None

# Lấy giá trị của 'shop_link' từ một hash trong Redis.
def get_connect_link_from_hash_db_14(hash_name, key):
    """
    Lấy giá trị của 'shop_link' từ một hash trong Redis.

    :param hash_name: Tên của hash trong Redis.
    :param key: Key trong hash.
    :return: Giá trị của 'shop_link' nếu tồn tại, ngược lại trả về None.
    """
    value = redis_client_14.hget(hash_name, key)
    
    if value:
        value_dict = json.loads(value)
        return value_dict.get("connect_link")
    
    return None

# Hàm lấy title, thumbnail và các thẻ meta khác của trang web
def fetch_page_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else "Default Title"
        
        og_image_tag = soup.find('meta', property='og:image')
        og_image = og_image_tag['content'] if og_image_tag else None
        
        meta_tags = soup.find_all('meta')
        link_tags = soup.find_all('link')

        
        meta_string = ""
        for tag in meta_tags:
            meta_string += str(tag) + "\n"
        
        link_string = ""
        for tag in link_tags:
            link_string += str(tag) + "\n"
        

        return title, og_image, meta_string, link_string
        
    return "Default Title", None, "", ""

# Hàm render web view qua proxy
@cache.cached(timeout=600, query_string=True) # Cache 10 Phút
def render_web_view(page_url):
    
    try:
        # Thử tải trang để kiểm tra lỗi X-Frame-Options
        response = requests.get(page_url)
        if 'X-Frame-Options' in response.headers and response.headers['X-Frame-Options'].lower() in ['deny', 'sameorigin']:
            return redirect(page_url)
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return redirect(page_url)
    
    page_title, og_image, meta_string, link_string = fetch_page_details(page_url)
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        {meta_string}
        {link_string}
        <title>{page_title}</title>
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        </style>
    </head>
    <body>
        <iframe src="{page_url}"></iframe>
    </body>
    </html>
    """)
    
# Thumnail Web can post to Facebook, ...
def render_thumnail_short_link(item):
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
            }}); 
        </script>
    </body>
    </html>
    """
    
    return html_content

# Hàm xóa khoản trắng trong string
def remove_whitespace(input_string):
    """
    Hàm xóa tất cả dấu cách và khoảng trắng trong chuỗi.
    
    Parameters:
    input_string (str): Chuỗi đầu vào cần xóa khoảng trắng.

    Returns:
    str: Chuỗi đã xóa khoảng trắng.
    """
    # Xóa tất cả các khoảng trắng, bao gồm dấu cách, tab, newline, v.v.
    return ''.join(input_string.split())

# Hàm kiểm tra các Domain được phép hiển thị dưới dạng webview
def recheck_link_can_show_web_view(url):

    # Domain được phép hiển thị webview
    domain_can_show_web_view = ["linkbio.co"]

    if clean_url(url) not in domain_can_show_web_view:
        # Tại đây kiểm tra nếu link này không nằm trong danh sách domain_can_show_web_view thì trả về False
        return False
