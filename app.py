from flask import Flask, render_template, request, redirect
from flask_migrate import Migrate
import base64
from io import BytesIO
from PIL import Image
from models import db, CatsModel
from werkzeug.urls import url_encode
from sqlalchemy.sql.expression import func
from re import sub

#host.docker.internal
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@host.docker.internal/catsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'temp_img'
db.init_app(app)
migrate = Migrate(app, db)

PAGINATION = 5

with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg']


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))


@app.route('/')
def main():
    cat = db.session.query(CatsModel).order_by(func.random()).first()
    return render_template('index.html', cat=cat, img=cat.img.decode('utf-8'))


@app.route('/cats/page_<int:page>', methods=['POST', 'GET'])
def cats(page=1):
    if request.method == "POST":
        return redirect(f'/search/page_1?query={request.form["query"]}')
    sort, how = request.args.get('sort'), request.args.get('how')
    all_cats = CatsModel.query
    all_cats = sort_cats(sort, how, all_cats).paginate(page, PAGINATION, False)
    return render_template('cats.html', cats=all_cats)


@app.route('/search/page_<int:page>', methods=['POST', 'GET'])
def search(page=1):
    if request.method == "POST":
        return redirect(f'/search/page_1?sort=relevance&query={request.form["query"]}')
    query = request.args.get('query')
    if ' ' in query:
        query = sub(' +', ' ', query)
        query = query.rstrip().replace(' ', '|')
    sort, how = request.args.get('sort'), request.args.get('how')
    filtered_cats = CatsModel.query.filter(CatsModel.__ts_vector__.match(query, postgresql_regconfig='russian'))
    filtered_cats = sort_cats(sort, how, filtered_cats).paginate(page, PAGINATION, False)
    return render_template('cats.html', cats=filtered_cats if filtered_cats.total != 0 else None)


def sort_cats(sort_type, how, cats_to_sort):
    if sort_type == 'breed':
        return cats_to_sort.order_by(CatsModel.breed if how is None or how == 'asc' else CatsModel.breed.desc())
    elif sort_type == 'age':
        return cats_to_sort.order_by(CatsModel.age if how is None or how == 'asc' else CatsModel.age.desc())
    else:
        return cats_to_sort.order_by(CatsModel.__ts_vector__)


@app.route('/cats/cat_<int:id>')
def get_cat(id):
    print(CatsModel.query.filter_by())
    cat = CatsModel.query.get(id)
    return render_template('cat_description.html', cat=cat, img=cat.img.decode('utf-8')) # resize_image(cat.img, (350, 280)))


@app.route('/add', methods=['POST', 'GET'])
def add_cat():
    if request.method == 'POST':
        try:
            db.session.add(CatsModel(**get_params(request)))
            db.session.commit()
            return render_template('add.html', flag=None)
        except Exception as _ex:
            print(_ex)
            return render_template('add.html', flag='error')
    else:
        return render_template('add.html')


@app.route('/update/cat_<int:id>', methods=['POST', 'GET'])
def update_cat(id):
    cat = CatsModel.query.get(id)
    img = cat.img.decode('utf-8')
    if request.method == "POST":
        try:
            db.session.query(CatsModel).filter(CatsModel.id == id).update(get_params(request))
            db.session.commit()
            return redirect(f'/cats/cat_{id}')
        except Exception as _ex:
            print(_ex)
            return render_template('update.html', cat=cat, img=img, flag='error')
    else:
        return render_template('update.html', cat=cat, img=img)


def get_params(req):
    breed = req.form['breed']
    img = req.files['img']
    name = req.form['name']
    description = req.form['description']
    age = req.form['age']
    if not allowed_file(img.filename):
        return render_template('add.html', flag='bad_image')
    return {
            'breed': breed,
            'img': base64.b64encode(img.read()),
            'name': name,
            'description': description,
            'age': age
        }

@app.route('/delete/cat_<int:id>', methods=['POST', 'GET'])
def delete_cat(id):
    if request.method == "POST":
        CatsModel.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect('/cats')
    else:
        return render_template('delete.html')


def resize_image(img: bytes, size: tuple) -> str:
    buffer = BytesIO(base64.b64decode(img))
    image = Image.open(buffer).resize(size, Image.ANTIALIAS)
    buffer = BytesIO()
    image.save(buffer, 'png')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
