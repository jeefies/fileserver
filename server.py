import os

from flask import Flask, redirect, abort, url_for, render_template, flash
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
base = os.path.dirname(os.path.abspath(__file__))
tempf = os.path.join(base, 'temps')

app = Flask(__name__, template_folder=tempf, static_folder=path)
app.config['SECRET_KEY'] = 'hard to get a kkey'
bootstrap = Bootstrap(app)

_j = os.path.join
p = _j(base, 'static')
_app = Flask(__name__, static_folder=p)
static = 'http://0.0.0.0:5001/static'
stcs = [os.path.join(static, n) for n in ['jquery.js',
                                          'bootstrap.js', 'bootstrap.css', 'favicon.ico']]
del _j, p


def render(file, **kwargs):
    kwargs['_sts'] = stcs
    return render_template(file, **kwargs)


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
            af((i, url_for('static', filename=p)))
        else:
            ad((i, url_for('download', stcp=p)))
    return render('files.html', dirs=d, files=f)


if __name__ == '__main__':
    def run_app():
        import io
        from contextlib import redirect_stdout, redirect_stderr
        f = io.StringIO()
        with redirect_stderr(f), redirect_stdout(f):
            _app.run('0.0.0.0', 5001)
    Process(target=run_app).start()
    Process(target=app.run, args=('0.0.0.0', 5000)).start()
