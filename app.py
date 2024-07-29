
from function  import *

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Chuyển hướng short đến URL 
@app.route('/<item_id>')
@cache.cached(timeout=600, query_string=True) # Cache 10 Phút
def redirect_to_url_shop_sell_product(item_id):
    # Tại đây sẽ kiểm item_id có thuộc giá trị ở sub shop hay không
    # Kiểm tra subdomain có trong domain_approved không
    # Tại đây sẽ kiểm tra lấy subdmain của domain trước khi chuyển hướng
    host = request.host
    # Tách subdomain ra nếu có
    subdomain = host.split('.')[0] if '.' in host else None
    
    if subdomain:
        # Kiểm tra subdomain có trong domain_approved không
        full_domain = subdomain + "." + os.getenv("DOMAIN_CAN_REGISTER_SUBDOMAINS")
        if check_key_in_hash_db_15("domain_approved", full_domain):
            # print("Có subdmain -> Đã được phê duyệt")
            
            # Rồi sau đó kiểm tra tiếp key trong hash dựa theo domain lấy được
            if check_hash_exists_db_14(full_domain):
                # print("Shop này có shop phụ")
                # Khi có shop phụ rồi mới kiểm tra shop phụ này nằm ở key nào 
                # Lây đường link để chuyển hướng luôn
                link_connect = (get_connect_link_from_hash_db_14(full_domain, full_domain + "/" + item_id))

                if recheck_link_can_show_web_view(link_connect) == False:
                    return redirect(link_connect) 
                
                # Ngược lại có thể hiển thị webview
                else: return render_web_view(link_connect)
            
    # ---------------------------------------------------------------------- //
    """Chuyển hướng đến URL dựa trên mã rút gọn."""
    data = load_data_from_redis_with_hash('short_link')
    item_data = data.get(item_id)
    
    # Các trường khác thì return ra trang thông thường
    if not item_data:
        return "Không tìm thấy thông tin cho ID này", 404

    # Dữ liệu đã được lưu dưới dạng chuỗi JSON, không cần parse lại
    item = json.loads(item_data)
    
    return render_template_string(render_thumnail_short_link(item))

# Làm short link -> Tab1
@app.route('/', methods=['GET', 'POST'])
def index():
    # Tại đây sẽ kiểm tra lấy subdmain của domain trước khi chuyển hướng
    host = request.host
    # Tách subdomain ra nếu có
    subdomain = host.split('.')[0] if '.' in host else None
    
    #if subdomain and subdomain !=  os.getenv("SUB_DOMAIN_MAIN"):
    if subdomain:
        # Kiểm tra subdomain có trong domain_approved không
        full_domain = subdomain + "." + os.getenv("DOMAIN_CAN_REGISTER_SUBDOMAINS")
        if check_key_in_hash_db_15("domain_approved", full_domain):
            # print("Subdomain đã được phê duyệt -> Chuyển hướng đến trang shop")
            link_connect = get_shop_link_from_hash_db_15("domain_approved", full_domain)
            # Chuyển hướng render trang của shop liên kết
            return render_web_view(link_connect)

    # Nếu không có subdomain thì chuyển hướng đến trang chính
    """Hiển thị giao diện người dùng và xử lý yêu cầu."""
    short_link = ""
    link_domain_shop = ""
    error_message = None
    if request.method == 'POST':
        
        link_domain_shop =  get_domain(request.form.get('link_domain_shop'))
        title = request.form.get('title')
        description = request.form.get('description')
        link_url = request.form.get('link_url')
        image = request.files.get('image')
        
        # Tại đây check xem link_domain_shop có trong domain_approved không, nếu không trả lỗi
        if check_key_in_hash_db_15("domain_approved", link_domain_shop) == False:
            error_message = "Domain shop này chưa được phê duyệt! Vui lòng đăng ký tại Menu [Đăng Ký Tên Miền]"
            return render_template('index.html', short_link=short_link, data_link_domain_shop=link_domain_shop, error_message=error_message)

        if title and description and link_url and image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                image.save(image_path)

                # Upload hình ảnh lên Google Drive và lấy link thumbnail
                image_url = upload_image_to_drive(image_path, filename)

                # Xóa tệp sau khi upload thành công
                os.remove(image_path)

                short_link = make_short_link(title, description, image_url, link_url, link_domain_shop)

            except Exception as e:
                error_message = f"Đã xảy ra lỗi khi tải ảnh lên Google Drive: {e}"
        else:
            error_message = "Vui lòng nhập tất cả các trường và chọn hình ảnh hợp lệ"

    if  link_domain_shop:
        link_domain_shop =  link_domain_shop
        
    # Load dữ liệu để hiển thị
    data = load_data_from_redis_have_key('short_link', short_link.replace('/', ''))

    return render_template('index.html', short_link=short_link, data=data, data_link_domain_shop=link_domain_shop,  error_message=error_message)

# Đăng ký tên miền -> Tab2
@app.route('/register-domain', methods=['POST'])
def register_domain():
    """Xử lý đăng ký tên miền."""
    shop_link = (request.form.get('shop_link'))
    domain_name = (request.form.get('domain_name'))
    email = (request.form.get('email'))
    error_message = None
    
    if domain_name.replace(".riviu.online","") == "":
        error_message = "Tên Domain đăng ký bị để trống!"
        return jsonify(success=False, error=error_message)
        

    if shop_link and domain_name and email:
        try:
            # Lưu thông tin vào Redis
            if not save_data_to_redis_register_domain('domains', domain_name, {
                'shop_link': shop_link,
                'domain_name': domain_name,
                'email': email
            }):
                error_message = "Domain này đã tồn tại"
                return jsonify(success=False, error=error_message)
            return jsonify(success=True)
        except Exception as e:
            error_message = f"Đã xảy ra lỗi khi lưu thông tin: {e}"
            return jsonify(success=False, error=error_message)
    else:
        error_message = "Vui lòng nhập tất cả các trường"
        return jsonify(success=False, error=error_message)
    
# Đăng ký cửa hàng con -> Tab3
@app.route('/register-sub-shop', methods=['POST'])
def register_sub_shop():
    """Xử lý đăng ký cửa hàng con."""
    main_shop_link = (clean_url(request.form.get('main_shop_link')))
    sub_shop_link = (clean_url(request.form.get('sub_shop_link')))
    connect_link = (request.form.get('connect_link'))

     # Tại đây kiểm tra số lượng cửa hàng con đã đạt giới hạn chưa = 10
    if count_keys_in_hash(main_shop_link) > 10: 
        error_message = "Số lượng cửa hàng con đã đạt giới hạn!"
        return jsonify(success=False, error=error_message)
    
    if sub_shop_link.replace("/","") == main_shop_link:
        error_message = "Link shop phụ không được giống với link shop chính."
        return jsonify(success=False, error=error_message)
    
    if main_shop_link and sub_shop_link:
        try:
            # Kiểm tra xem domain đã tồn tại chưa
            key_exists = check_key_in_hash_db_15("domain_approved", main_shop_link)
            if key_exists == False:
                error_message = "Domain shop này chưa tồn tại!"
                return jsonify(success=False, error=error_message)
            
            # Lưu thông tin vào Redis
            if not save_data_to_redis_register_sub_shop(main_shop_link, sub_shop_link, {
                'connect_link': connect_link
            }):
                error_message = "Sub Shop này đã tồn tại"
                return jsonify(success=False, error=error_message)
            return jsonify(success=True)
        
        except Exception as e:
            error_message = f"Đã xảy ra lỗi khi lưu thông tin: {e}"
            return jsonify(success=False, error=error_message)
    else:
        error_message = "Vui lòng nhập tất cả các trường"
        return jsonify(success=False, error=error_message)  

# Hàm tìm kiếm cửa hàng con -> Tab4
@app.route('/search-sub-shop', methods=['POST'])
def get_sub_shop():
    # Lấy dữ liệu từ form
    search_main_shop_link = clean_url(request.form.get('search_main_shop_link'))
    try:
        # Tại đây kiểm tra hash này có tồn tại không 
        if check_hash_exists_db_14(search_main_shop_link):
           
            # Tìm kiếm cửa hàng con
            shops = get_keys_in_hash(search_main_shop_link)
            if shops:  # Nếu có giá trị trong shops
                return jsonify(success=True, shops=shops)
            else:  # Nếu không có giá trị trong shops
                return jsonify(success=False, error="Không có giá trị tim thấy")
        else:
            return jsonify(success=False, error="Không có giá trị tim thấy")
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Main API Run -------------------------- //
if __name__ == '__main__':
    app.run(debug=True, port=5000)