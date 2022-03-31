from flask import Flask, render_template, request, redirect, send_file
from flask_migrate import Migrate
import base64
from pickle import dumps
from models import db, CatsModel

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/catsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'temp_img'
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/cats')
def cats():  # put application's code here
    return render_template('cats.html')

@app.route('/add', methods=['POST', 'GET'])
def add_cat():
    if request.method == 'POST':
        breed = request.form['breed']
        img = request.files['img']
        name = request.form['name']
        description = request.form['description']
        age = request.form['age']
        params = {
            'breed': breed,
            'img': base64.b64encode(img.read()),
            'name': name,
            'description': description,
            'age': age
        }
        image = base64.b64encode(img.read())
        cats = CatsModel(**params)

        try:
            db.session.add(cats)
            db.session.commit()
            return render_template('add.html', file=image.decode('utf-8'))
        except Exception as _ex:
            print(_ex)
            return 'При добавлении котика возникла ошибка'
    else:
        return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)
