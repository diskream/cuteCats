from flask import Flask, render_template, request, redirect, send_file
from flask_migrate import Migrate
import base64
from io import BytesIO, StringIO
from PIL import Image
from sqlalchemy import cast
from sqlalchemy import func
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

@app.route('/cats/page_<int:page>', methods=['POST', 'GET'])
def cats(page=1):
    if request.method == "POST":
        return redirect(f'/search?query={request.form["query"]}')
    cats = CatsModel.query.paginate(page, 5, False)
    return render_template('cats.html', cats=cats)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        return redirect(f'/search?query={request.form["query"]}')
    query = request.args.get('query').replace(' ', '|')
    # find = ((CatsModel.breed.like(query)) | (CatsModel.name.like(query)) |
    #         (CatsModel.description.like(query))| (CatsModel.age.cast(db.String).like(query)))
    filtered_cats = CatsModel.query.filter(CatsModel.__ts_vector__.match(query, postgresql_regconfig='russian')).\
        paginate(1, 5, False)
    return render_template('cats.html', cats = filtered_cats)

@app.route('/cats/cat_<int:id>')
def get_cat(id):
    print(CatsModel.query.filter_by())
    cat = CatsModel.query.get(id)
    return render_template('cat_description.html', cat=cat, img=resize_image(cat.img, (300, 250)))

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

def resize_image(img: bytes, size: tuple) -> str:
    buffer = BytesIO(base64.b64decode(img))
    image = Image.open(buffer).resize(size, Image.ANTIALIAS)
    buffer = BytesIO()
    image.save(buffer, 'png')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
