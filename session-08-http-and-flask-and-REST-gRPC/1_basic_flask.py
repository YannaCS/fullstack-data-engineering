from flask import Flask

app = Flask(__name__)

@app.route('/')  # Root path
def home():
    return 'hello world'

if __name__ == '__main__':
    app.run(debug=True)
