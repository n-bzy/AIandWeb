# %%
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')


def crawl(start_link):
    # Initalize stack, visited list and index
    stack = []
    visited = []
    index = {}
    # Get first list of urls from the start link and append to list
    server = requests.get(start_link, timeout=3)
    soup = BeautifulSoup(server.text, 'html.parser')
    stack = get_href(start_link, soup)
    while stack:
        url = stack.pop()
        if url in visited:
            continue
        server = requests.get(url, timeout=3)
        soup = BeautifulSoup(server.text, 'html.parser')
        # Get the content and update index
        content = get_content(soup.get_text())
        update_index(url, index, content)
        # Add url to visited list, get new urls and add them to stack
        visited.append(url)
        urls = get_href(url, soup)
        for url in urls:
            stack.append(url)

    return index


def get_href(url, soup):
    urls = []
    for href in soup.find_all('a'):
        # Combine the relative url with the main url
        abs_link = urljoin(url, href['href'])
        # Only append links with the same netloc to the list
        if urlsplit(url).netloc == urlsplit(abs_link).netloc:
            urls.append(abs_link)
    return urls


# TODO: New function: crawl page, take content split into dict / list,
# update index
def get_content(soup):
    # Tokenize page content with nltk
    tokens = nltk.word_tokenize(soup)
    # Converts tokens to lower case, filter tokens for stop words with nltk
    filtered_tokens = [w.lower() for w in tokens
                       if not w.lower() in stopwords.words('english')]
    # Remove special characters
    filtered_tokens = [word for word in filtered_tokens if word.isalnum()]
    return filtered_tokens


def update_index(url, index, content):
    for word in content:
        if word in index:
            for k in index[word]:
                # Var j is needed to not add multiple
                # instances of a new url to the index
                j = 0
                if k['url'] == url:
                    k['freq'] += 1
                    j += 11
            if j == 0:
                index[word].append({'url': url, 'freq': 1})
        else:
            index[word] = [{'url': url, 'freq': 1}]


def search(word_list, index):
    output = []
    # Tokenize entry
    filtered_search = get_content(word_list)
    for word in filtered_search:
        if word in index:
            for entry in index[word]:
                output.append(entry)
    sorted_output = sorted(output, key=lambda x: x['freq'], reverse=True)
    output_url = [url['url'] for url in sorted_output]
    return output_url


# %%
if __name__ == "__main__":
    entry = "What is a Platypus?"
    index = crawl("https://vm009.rz.uos.de/crawl/index.html")
    output = search(entry, index)
# %%
