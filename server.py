import os
import sys
import uuid
from base64 import urlsafe_b64decode as b64decode
from functools import lru_cache

from flask import Flask, redirect, abort, url_for, render_template, flash, request
from flask import make_response, jsonify
from flask_bootstrap import Bootstrap


path = os.getcwd()
join = os.path.join
base = os.path.dirname(os.path.abspath(__file__))
tempf = os.path.join(base, 'temps')

app = Flask(__name__, template_folder=tempf, static_folder=path)
app.config['SECRET_KEY'] = uuid.uuid1().hex
bootstrap = Bootstrap(app)

render = render_template

@app.route('/favicon.ico')
def icon():
    with open(os.path.join(base, 'favicon.ico'), 'rb') as f:
        return f.read()

@app.route('/', methods='GET POST'.split())
def index():
    return render('index.html')

@app.route('/data', methods=['post'])
def recv():
    file = bytes([int(i) for i in request.values.get('file').split(',')])
    name = request.values.get('name')
    print('Bytes got! Save at', name)
    with open(name, 'wb') as f:
        f.write(file)
    return jsonify({'code': 200, 'upload': True})

@app.route('/form', methods=['get','post'])
def form():
    if request.method == "POST":
        file = request.files.get("File")
        file.save(file.filename)
        flash("Upload success!")
        return redirect(url_for('form'))
    else:
        return render('form.html')


@app.route('/path/<path:stcp>')
def download(stcp):
    viewp = os.path.join(path, stcp)
    return check(viewp, stcp)


@app.route('/path')
def downloadm():
    return check(path, '')


def check(stcp, start):
    dirs = os.listdir(stcp)
    d = []
    ad = d.append
    f = []
    af = f.append
    isf = os.path.isfile
    absp = os.path.abspath
    j = os.path.join
    for i in dirs:
        a = absp(j(start, i))
        p = os.path.join(start, i) if start else i
        if isf(a):
            af((i, url_for('stc', filename=p)))
        else:
            ad((i, url_for('download', stcp=p)))
    return render('files.html', dirs=d, files=f, index = False if start else True)

@app.route('/stc/<path:filename>')
@lru_cache()
def stc(filename):
    with open(join(path, filename), 'rb') as f:
        con = f.read()
    rsp = make_response(con)
    rsp.headers['Content-Type'] = "application/octet-stream"
    rsp.headers['Content-Disposition'] = (b"attachment;filename=%s" % (filename.encode('utf-8'))).decode('latin-1')
    return rsp

if __name__ == '__main__':
    def run_app(iapp, host, port):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        f = io.StringIO()
        with redirect_stderr(f), redirect_stdout(f):
            iapp.run(host, port)

    if '-q' in sys.argv or '--quiet' in  sys.argv:
        run_app(app, '0.0.0.0', 5050)
    else:
        app.run('0.0.0.0', 5050)
        #app.run(port = 5050)
