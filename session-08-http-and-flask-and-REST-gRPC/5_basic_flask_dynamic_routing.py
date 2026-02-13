from flask import Flask, render_template, jsonify

app = Flask(__name__)

# route 1: home page
@app.route('/')  # Root path
def home():
    return 'hello world'

# rounte 2: users page with html template
@app.route('/users')
def users():
    users = [
        {'name': 'Steven', 'age': 25},
        {'name': 'Bob', 'age': 30},
        {'name': 'Adam', 'age': 27}
    ]
    return render_template('hello_Jinjia2.html', users=users)

# dynamic routes
@app.route('/products/<int:id>') # no space after the colon!
def products(id):
    print('id: ', id, 'type of id:', type(id))
    products = [
        {'id': 1, 'name': 'Laptop', 'price': 25, 'stock': 100},
        {'id': 2, 'name': 'Cellphone', 'price': 80, 'stock': 200},
        {'id': 3, 'name': 'PS5', 'price': 200, 'stock': 99}
    ]
    filtered = [x for x in products if x['id'] == id]
    if len(filtered) == 0:
        return {'error': 'not found'}, 404

    return jsonify(filtered)

if __name__ == '__main__':
    app.run(debug=True)

