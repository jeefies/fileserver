"""
Easy File Server

Author: jeef 付伟吉
Email: jeefy163@163.com jeefyol@outlook.com
Url: https://github.com/jeefies/fileserver.git

usage:
    fileserver (-q/--quiet) -b/--bind host -p/--port port
    
view:
    /favicon.ico (icon)
    / (index): send index page use js to upload
    /data (recv) [POST]: recv data from js
    /form (form) [POST GET]: use form to upload
    /path/<path:stcp> (download) and /path/:
        list the files of under the path
        
    /stc/<path:filename> :generate a attachment file to download.
    /nstc/<path:filename>: not attachment, just a raw data
"""
import os # to list all files
import sys # get sys argv
import uuid # generate secret key
# generate better filename
from base64 import urlsafe_b64decode as b64decode

from flask import (Flask, redirect, abort, 
        url_for, render_template,
        flash, request, make_response,
        jsonify, Response)
# import all methods used in the program
# need bootstrap dependences
from flask_bootstrap import Bootstrap


path = os.getcwd()
join = os.path.join
base = os.path.dirname(os.path.abspath(__file__))
tempf = os.path.join(base, 'temps')

# create app instance
app = Flask(__name__, template_folder=tempf, static_folder=path)
app.config['SECRET_KEY'] = uuid.uuid1().hex # use for session(in flash method)
# init app for bootstrap
bootstrap = Bootstrap(app)

render = render_template # generate shortcut for render

@app.route('/favicon.ico')
def icon():
    """Use for icon"""
    with open(os.path.join(base, 'favicon.ico'), 'rb') as f:
        return f.read()

@app.route('/', methods='GET POST'.split())
def index():
    "return index page use js to upload file"
    return render('index.html')

@app.route('/data', methods=['post'])
def recv():
    # get the bytes data
    file = bytes([int(i) for i in request.values.get('file').split(',')])
    name = request.values.get('name')

    print('Bytes got! Save at', name)
    
    with open(name, 'wb') as f:
        f.write(file)
    
    return jsonify({'code': 200, 'upload': True})

@app.route('/form', methods=['get','post'])
def form():
    """Use get -> post -> redirect"""
    if request.method == "POST":
        # get the file and redirect to use get method
        file = request.files.get("File")
        file.save(file.filename)
        flash("Upload success!")
        return redirect(url_for('form'))
    else:
        # return the get page source
        return render('form.html')


@app.route('/path/<path:stcp>')
def download(stcp):
    """List the files and directories under the cwd + stcp"""
    viewp = os.path.join(path, stcp)
    return check(viewp, stcp)


@app.route('/path')
def downloadm():
    """List all files and directories under the cwd"""
    return check(path, '')


def check(stcp, start):
    ("List all files and directories under the cwd\n"
        "param stcp is the full path of the request\n"
        "param start is the relative path of the request")
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
def stc(filename):
    with open(join(path, filename), 'rb') as f:
        con = f.read()
    filename = os.path.basename(filename)
    rsp = make_response(Response(con))
    rsp.headers['Content-Type'] = "application/octet-stream"
    rsp.headers['Content-Disposition'] = (b"attachment;filename=%s" % (filename.encode('utf-8'))).decode('latin-1')
    return rsp

@app.route('/nstc/<path:filename>')
def nstc(filename):
    def con():
        with open(join(path, filename), 'rb') as f:
                return  f.read()
    rsp = Response(con())
    return rsp

if __name__ == '__main__':
    def run_app(iapp, host, port):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        f = io.StringIO()
        with redirect_stderr(f), redirect_stdout(f):
            iapp.run(host, port)

    def getarg(arg):
        argv = iter(sys.argv)
        for a in argv:
            if a.startswith(arg):
                if a == arg:
                    return next(argv)
                b = a[len(a) - 1:]
                print(b)
                b = b.strip('=:')
                return b
        else:
            return None

    port = int(getarg('-p') or getarg('--port') or '5050')
    host = getarg('-b') or getarg('--bind') or '0.0.0.0'

    if '-q' in sys.argv or '--quiet' in  sys.argv:
        run_app(app, host, port)
    else:
        app.run(host, port)
