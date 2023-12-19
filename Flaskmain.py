from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def handle_request():
    data = request.get_data()
    headers = dict(request.headers)
    method = request.method
    args = dict(request.args)
    form_data = dict(request.form)

    result = {
        'form_data': form_data,
    }

    with open('D://MyProjects/xakaton/req.txt', 'w') as f:
        f.write(str(result))
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
