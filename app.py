from flask import Flask, request, jsonify, render_template_string, send_from_directory
from bs4 import BeautifulSoup, NavigableString
import json
from urllib.parse import urljoin
import requests
import tiktoken
import openai
import os

app = Flask(__name__, static_folder='static')

enc = tiktoken.encoding_for_model("text-ada-001")


openai.api_key = os.getenv("OPENAI_API_KEY")



def my_ml_function(text_batch):


    return text_batch


def modify_text_nodes(node, batch=[]):
    if node.name in {'script', 'style'}:
        return

    if isinstance(node, NavigableString):
        batch.append(node)
        
        # If we've reached our batch size, process the batch
        if len(batch) >= 20:
            # Assume my_ml_function can handle batches as well
            results = my_ml_function([str(n) for n in batch])

            # Replace the text nodes with the modified text
            for text_node, modified_text in zip(batch, results):
                text_node.replace_with(modified_text)
            
            # Clear the batch
            batch.clear()
    else:
        for child in node.contents:
            modify_text_nodes(child, batch)



def convert_relative_urls(html, base):
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all():
        for attr in ['href', 'src', 'action']:
            url = tag.get(attr)
            if url:
                tag[attr] = urljoin(base, url)

    for a in soup.find_all('a'):
        original_link = a.get('href')
        a['href'] = f"http://localhost:5000/browse?url={original_link}"

    return soup



@app.route('/modify-html', methods=['POST'])
def modify_html():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL not provided'}), 400

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as err:
        return jsonify({'error': str(err)}), 400

    soup = convert_relative_urls(response.text, url)
    batch = []
    modify_text_nodes(soup, batch)

    if batch:
        results = my_ml_function([str(n) for n in batch])
        for text_node, modified_text in zip(batch, results):
            text_node.replace_with(modified_text)

    modified_html = str(soup)

    return jsonify({'modifiedHtml': modified_html})


@app.route('/browse')
def browse():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL not provided'}), 400

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as err:
        return jsonify({'error': str(err)}), 400

    soup = convert_relative_urls(response.text, url)
    batch = []
    modify_text_nodes(soup, batch)

    if batch:
        results = my_ml_function([str(n) for n in batch])
        for text_node, modified_text in zip(batch, results):
            text_node.replace_with(modified_text)

    modified_html = str(soup)

    return render_template_string(modified_html)


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')







# """
# A sample Hello World server.
# """
# import os

# from flask import Flask, render_template

# # pylint: disable=C0103
# app = Flask(__name__)


# @app.route('/')
# def hello():
#     """Return a friendly HTTP greeting."""
#     message = "It's running!"

#     """Get Cloud Run environment variables."""
#     service = os.environ.get('K_SERVICE', 'Unknown service')
#     revision = os.environ.get('K_REVISION', 'Unknown revision')

#     return render_template('index.html',
#         message=message,
#         Service=service,
#         Revision=revision)


