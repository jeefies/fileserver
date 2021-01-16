import os
import sys
import uuid
from functools import lru_cache

from flask import Flask, redirect, abort, url_for, render_template, flash
from flask import make_response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import DataRequired
from multiprocessing import Process


class FileForm(FlaskForm):
    file = FileField('Please choose the file you\'d like to upload',
                     validators=[DataRequired(message='Your must give in a file')])
    submit = SubmitField('Submit')


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
    form = FileForm()
    if form.validate_on_submit():
        data = form.file.data
        name = data.filename
        p = os.path.join(path, name)
        flash('Upload success!')
        data.save(p)
        form.file = FileField('Please choose the file you\'d like to upload',
                              validators=[DataRequired(message='Your must give in a file')])
    return render('index.html', form=form)


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
    return render('files.html', dirs=d, files=f)

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
        Process(target=run_app, args = (app,)).start()
    else:
        Process(target=app.run, args=('0.0.0.0', 5050)).start()
