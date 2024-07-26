import json

def convert_private_key_to_pem(json_file_path, pem_file_path):
    # Đọc nội dung từ file JSON
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Lấy giá trị của trường private_key
    private_key = data.get('private_key', '')

    if private_key:
        # Ghi giá trị private_key vào file PEM
        with open(pem_file_path, 'w') as pem_file:
            pem_file.write(private_key)
        print(f"Private key has been written to {pem_file_path}")
    else:
        print("No private_key found in the JSON file")

# Sử dụng hàm
json_file_path = 'pro-core-430614-r5-8c450393be49.json'
pem_file_path = 'private_key.pem'
convert_private_key_to_pem(json_file_path, pem_file_path)
