from flask import Flask, render_template, jsonify, request
from models import db, Product

app = Flask(__name__)

app.config.from_object('db_config')

db.init_app(app)

@app.route('/')  # Root path
def home():
    return 'hello world'


@app.route('/users')
def users():
    users = [
        {"name": 'Steven', "age": 25},
        {"name": 'Bob', "age": 30},
        {"name": 'Adam', "age": 27},
        {"name": 'Jane', "age": 31},
    ]
    return render_template('hello.html', users=users)


@app.route('/products/<int:id>')
def products(id):
    print({
        "method": request.method,
        "url": request.url
    })
    print('priceLow', request.args.get('priceLow'))
    print('priceHigh', request.args.get('priceHigh'))
    print('id', id ,type(id))
    # products = [
    #     {"id": 1, "name": "Laptop", "price": 100, "stock": 100},
    #     {"id": 2, "name": "Cellphpne", "price": 80, "stock": 200},
    #     {"id": 3, "name": "PS5", "price": 200, "stock": 99},
    # ]
    
    # product_res is an object not json form
    products_res = db.session.execute(db.select(Product)).scalars().all()
    print('products_res', products_res)
    
    # filtered = [x for x in products if x['id'] == id]
    products = [x.to_dict() for x in products_res]
    
    if len(products_res) == 0:
        return {"error": "Not found"}, 404

    return jsonify(products)


if __name__ == '__main__':
    app.run(debug=True)
