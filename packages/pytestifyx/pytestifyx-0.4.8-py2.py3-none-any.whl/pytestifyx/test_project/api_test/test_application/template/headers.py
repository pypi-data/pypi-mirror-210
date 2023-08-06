import time

headers = {
    'Content-Type': 'application/json;charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Signature-Type': 'RSA',
    'Signature-Data': '',
    'timestamp': time.strftime("%Y%m%d%H%M%S", time.localtime()),
}
