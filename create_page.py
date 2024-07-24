def generate_html_page(title, description, image_url, link_url):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:image" content="{image_url}">
        <meta property="og:url" content="{link_url}">
        <meta property="og:type" content="website">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{title}">
        <meta name="twitter:description" content="{description}">
        <meta name="twitter:image" content="{image_url}">
    </head>
    <body>
        <h1>{title}</h1>
        <p>{description}</p>
        <img src="{image_url}" alt="{title}">
        <p><a href="{link_url}">Click here to visit the page</a></p>
    </body>
    </html>
    """
    return html_content

# Example usage
title = "Sản phẩm bán chạy nhất"
description = "This is a description of the sample page."
image_url = "https://lh3.googleusercontent.com/pw/AP1GczNxyGq9EG_Q56VnZ4BdkhL_YdqMl2t4FCklefAz7FnYnW770g-xy54F55c5Y3RXbxeQsa_POt5mMw7iIMeBnQQAG6kRLG_NJSyFw3xJJWYGmb8R3HwlBWJnaJ9TVSW2kXnJqFPrY4EtFx6l4LrszqZlzg=w318-h424-s-no-gm?authuser=0"
link_url = "https://www.google.com.vn/"

html_page = generate_html_page(title, description, image_url, link_url)

# Save the HTML content to a file
with open("sample_page.html", "w") as file:
    file.write(html_page)
