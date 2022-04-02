from flask import Flask, render_template, request, redirect
from flask_migrate import Migrate
import base64
from io import BytesIO
from PIL import Image
from models import db, CatsModel
from werkzeug.urls import url_encode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/catsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'temp_img'
db.init_app(app)
migrate = Migrate(app, db)

PAGINATION = 5

with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png']


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/cats/page_<int:page>', methods=['POST', 'GET'])
def cats(page=1):
    if request.method == "POST":
        return redirect(f'/search/page_1?query={request.form["query"]}')
    sort = request.args.get('sort')
    all_cats = CatsModel.query
    all_cats = sort_cats(sort, all_cats).paginate(page, PAGINATION, False)
    return render_template('cats.html', cats=all_cats)


@app.route('/search/page_<int:page>', methods=['POST', 'GET'])
def search(page=1):
    if request.method == "POST":
        return redirect(f'/search/page_1?sort=relevance&query={request.form["query"]}')
    query = request.args.get('query').replace(' ', '|')
    sort = request.args.get('sort')
    filtered_cats = CatsModel.query.filter(CatsModel.__ts_vector__.match(query, postgresql_regconfig='russian'))
    print(CatsModel.query.filter(CatsModel.__ts_vector__.match(query, postgresql_regconfig='russian')))
    filtered_cats = sort_cats(sort, filtered_cats).paginate(page, PAGINATION, False)
    return render_template('cats.html', cats=filtered_cats if filtered_cats.total != 0 else None)


def sort_cats(sort_type, cats_to_sort):
    if sort_type == 'breed':
        return cats_to_sort.order_by(CatsModel.breed)
    elif sort_type == 'age':
        return cats_to_sort.order_by(CatsModel.age)
    else:
        return cats_to_sort


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
        if not allowed_file(img.filename):
            return render_template('add.html', flag='bad_image')
        params = {
            'breed': breed,
            'img': base64.b64encode(img.read()),
            'name': name,
            'description': description,
            'age': age
        }
        cats = CatsModel(**params)
        try:
            db.session.add(cats)
            db.session.commit()
            return render_template('add.html', flag=None)
        except Exception as _ex:
            print(_ex)
            return render_template('add.html', flag='error')
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
