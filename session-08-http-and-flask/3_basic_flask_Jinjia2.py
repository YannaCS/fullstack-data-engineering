from flask import Flask, render_template

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

if __name__ == '__main__':
    app.run(debug=True)
