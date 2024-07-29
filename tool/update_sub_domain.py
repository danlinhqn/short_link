import sys
sys.path.append('..')
from function import *

def save_domain_approved_redis(hash_name, key):
    """Lấy giá trị từ key trong một hash, lưu vào hash khác và xóa key khỏi hash ban đầu."""
    # Lấy giá trị từ hash_name
    value = redis_client_15.hget(hash_name, key)
    
    if value is not None:
        # Lưu giá trị vào hash 'domain_approved'
        redis_client_15.hset('domain_approved', key, value)
        
        # Xóa key khỏi hash_name
        redis_client_15.hdel(hash_name, key)
        
        return True  # Thành công
    else:
        return False  # Key không tồn tại trong hash_name
    
# Duyệt Sub domain
save_domain_approved_redis("domains", "trum.riviu.online")