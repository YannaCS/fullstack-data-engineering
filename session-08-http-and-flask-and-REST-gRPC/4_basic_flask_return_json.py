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

@app.route('/products')
def products():
    products = [
        {'name': 'Laptop', 'price': 25, 'stock': 100},
        {'name': 'Cellphone', 'price': 80, 'stock': 200},
        {'name': 'PS5', 'price': 200, 'stock': 99}
    ]

    # return products # flask will return data into json format automatically
    # usually will use jsonify
    # for this example, there is no difference
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
