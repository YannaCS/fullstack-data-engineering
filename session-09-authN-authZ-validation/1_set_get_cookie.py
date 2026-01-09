from create_app import create_app
from flask import make_response, request

app = create_app()

@app.route('/set-cookie')
def set_cookie():
    response = make_response('Cookie set')
    response.set_cookie('user_id', '123', max_age=3600)
    return response

@app.route('/get-cookie')
def get_cookie():
    cookie_value = request.cookies.get('user_id')
    return f"cookie value: {cookie_value}"



if __name__ == '__main__':
    app.run(debug=True)