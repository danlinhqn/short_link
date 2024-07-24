from flask import Flask, request, render_template_string

app = Flask(__name__)

# Ví dụ dữ liệu chứa thông tin URL và image_url theo ID
data = {
    '159753': {
        'title': 'Sản phẩm bán chạy nhất',
        'description': 'This is a description of the sample page.',
        'image_url': 'https://lh3.googleusercontent.com/pw/AP1GczPF_BD-tqkwaqJeq7XnFoMpN9B3Je03K8bvQ3qWSgqa2-4G1TQ1MxztDp4IH7LbmvTuPQEklhK8_JPYkzlf_NDu_bsuj9r5cNNlVu_HPVrp8VNfe_s5xNzNDk5OSm2-bUJS4KLaSjYxfXMcbO4CY2fFUYq5y4BEaffjKFkjB3eIzg0C8xLDNTy2Ci3hD5UTJD4PJibaBIbHuV7mZauuGqLKCCFir5bKkW_XWbscNeAyVs8XzFQXf1FXnChOukDY1BsPgsX8iFRdYpELBdhGAxhOSVEXl3OGAoYmP2v8C1TDtWe6GfKTXJH0NQqIR8mOXwvimZQ7Zoq5MJ4LNRhSr4KfpPEmpiWHnb9PDeDiTtMc-C5QfY5eAgeGvDT8xRAj8vRjgzwVR6TRdws4w0IRyuKKlbyHuXrErrtfivzXVSriEo4Er5x3ATH509iu7xNSp8IN4LJIhZM6gW7vfI_QhZ5VOM8PqOByQym1_zYHDSjMzNVrBHB-yVDTTE_IF4PPNh9aPZUdNoFd13uSCJL59t9nrjWz6MXGnVCd1uJz4iYXeYXSVmUmu8_mDMKX9-GjAODeTElVc6uuZjJ4ytQ3NH-K3rrnyYhOC4pltcujTIxxejTt9IWVRxK6ltmg5x02EEhimJPum44uQ4wJ93Us-7WZQT8KPJidm9iAm7tSCOTsqCXsa-zesdXvWWP26tHXOpD8KSqJ8ptH5NfJ7vumzld14y7sowzff0Uu3NyNXdpxL6ZfvbRtk_pwMuU7cNzugANVyVaFLDOa-18AtQVMa0730K25TDcVYOiQR-qjeVhl4lBd2gMLmQk-nrIo7yVykWwa-C1Shbs9nFT3NCdD-KwBDAfV9NO1OzXHvbw-y1bAzeELe8rGrlzjfCCMrtNIgA_3IxgpIGaiB4bdBeNq1irfkVePAMM1h6hpeLBbQo-0C2E4pSCd7mljXNK48XugRY9KI05i7Cjjw4vvPU6fYii4dFg9c6yuN__7nVeO7EFl8OoL58Kp2xOduHoE0Hih9FMJQK1KretDO2mxsKYVX0CTwctFoOsuTzXNxrixP8WOTSs42NMs5b4QtYwe19cj3WKHtcHfL-M-nA86Aqx8dkSKgAyPp78DFxNmkPyNbP1SuqhAVP6IttW8wCOAO8t-Qs7-=w292-h632-no?authuser=0',
        'link_url': 'https://www.google.com.vn/'
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
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{item['title']}</title>
            <meta property="og:title" content="{item['title']}">
            <meta property="og:description" content="{item['description']}">
            <meta property="og:image" content="{item['image_url']}">
            <meta property="og:url" content="{item['link_url']}">
            <meta property="og:type" content="website">
            <meta name="twitter:card" content="summary_large_image">
            <meta name="twitter:title" content="{item['title']}">
            <meta name="twitter:description" content="{item['description']}">
            <meta name="twitter:image" content="{item['image_url']}">
        </head>
        <body>
            <h1>{item['title']}</h1>
            <p>{item['description']}</p>
            <img src="{item['image_url']}" alt="{item['title']}">
            <p><a href="{item['link_url']}">Click here to visit the page</a></p>
        </body>
        </html>
        """
        return render_template_string(html_content)
    else:
        return "ID not found", 404

if __name__ == '__main__':
    app.run(debug=True)
