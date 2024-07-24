from flask import Flask, request, render_template_string

app = Flask(__name__)

# Ví dụ dữ liệu chứa thông tin URL và image_url theo ID
data = {
    '159753': {
        'title': 'Sản phẩm bán chạy nhất',
        'description': 'This is a description of the sample page.',
        'image_url': 'https://lh3.googleusercontent.com/pw/AP1GczM7-5Pwv_S9meZ-z4j-ptIkYbevCkD7RNdD1hV8X6pZSHMhar9QT2RxF5J3vJj8B3_LDydAmHaumTT3rQaM9CiZA0TRrlClW_DPby8fBMWd6FReXD0SqMChuGdXvnw9YRj-_rK8fBsxMv60OG7keP8=w768-h564-s-no-gm?authuser=0',
        'link_url': 'https://s.shopee.vn/7Kcp346PkJ'
    }
    # Thêm các mục khác nếu cần
}

@app.route('/index.html')
def index():
    id = request.args.get('id')
    if id in data:
        item = data[id]
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
            <h1>{item['title']}</h1>
            <p>{item['description']}</p>
            <img src='{item['image_url']}' alt='{item['title']}'>
            <p><a href='{item['link_url']}'>Click here to visit the page</a></p>
        </body>
        </html>
        """
        return render_template_string(html_content)
    else:
        return "ID not found", 404

if __name__ == '__main__':
    app.run(debug=True)
