from urllib.parse import urlparse


def path_from_url(url):

    return urlparse(url).path

def authority_from_url(url):

    p = urlparse(url)
    return f'{p.scheme}://{p.netloc}'