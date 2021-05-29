import secrets
import flask
from flask import request
from flask_cors import CORS

HOMEPAGE_URL = 'https://li.violet.wtf'
BASE_URL = 'https://' + ('l'*63) + '.violet.wtf/'

chars = 'lI'

app = flask.Flask(__name__)
CORS(app)


def write_byte(current_str: str, byte: int) -> str:
    for i in range(8):
        if byte & 1 << 7-i != 0:
            current_str += 'l'
        else:
            current_str += 'I'
    return current_str


def create_url(link: str, length: int) -> str:
    url = ''

    for byte in link:
        url = write_byte(url, ord(byte))

    padding = length - len(url) - len(BASE_URL)

    if padding > 0:
        url = write_byte(url, 0x0)
        padding -= 8

        if padding > 0:
            for i in range(padding):
                url += secrets.choice(chars)

    return BASE_URL + url


def read_byte(byte: str) -> int:
    return int(byte.replace('l', '1').replace('I', '0'), 2)


def read_url(link: str) -> str:
    if link.startswith(BASE_URL):
        link = link.replace(BASE_URL, '', 1)

    cursor = 0
    url = ''

    while cursor < len(link):
        byte = read_byte(link[cursor:cursor + 8])

        if byte == 0:
            return url

        url += chr(byte)

        cursor += 8

    return url


@app.route('/')
def home():
    return flask.redirect(HOMEPAGE_URL)


@app.route('/create')
def create():
    link = request.args.get('link')
    length = int(request.args.get('length'))

    if not link or not length:
        return 'bad params'

    return create_url(link, length)


@app.route('/<path:path>')
def go(path: str):
    return flask.redirect(read_url(path))
