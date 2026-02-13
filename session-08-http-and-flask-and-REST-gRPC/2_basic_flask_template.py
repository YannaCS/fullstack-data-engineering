from flask import Flask, render_template

app = Flask(__name__)

# route 1: home page
@app.route('/')  # Root path
def home():
    return 'hello world'

# rounte 2: users page with html template
@app.route('/users')
def users():
    return render_template('hello.html')

if __name__ == '__main__':
    app.run(debug=True)
