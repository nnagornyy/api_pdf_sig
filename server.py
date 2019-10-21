import os, datetime
from flask import Flask, render_template, request, jsonify, send_file, json
from acrobat import Acrobat

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return render_template('form.html')


@app.route('/sign', methods=['POST'])
def sig():
    clear_upload_dir();
    pdf = request.files['pdf']
    pfx = request.files['pfx']
    pwd = request.form.get('pwd')

    pdf_server_path = os.path.abspath(os.path.join('upload', pdf.filename))
    pfx_server_path = os.path.abspath(os.path.join('upload', pfx.filename))

    pdf.save(pdf_server_path)
    pfx.save(pfx_server_path)

    acrobat = Acrobat(pdf_server_path)
    res = acrobat.sing_document(pfx_server_path, pwd)
    if not res == True:
        return jsonify(res), 500
    else:
        acrobat.finish()
        return send_file(pdf_server_path, as_attachment=True)


@app.route('/generate', methods=['POST', 'GET'])
def generate_cer():
    response = {}

    name = request.args.get('name')
    email = request.args.get('email')
    org = request.args.get('org')
    pwd = request.args.get('pwd')

    acrobat = Acrobat()
    res = acrobat.create_new_sert(name, email, org, pwd, app.root_path)
    response = jsonify({'status': 'success', 'result': res})
    return response


@app.route('/file/<path:path_to_file>')
def download_file(path_to_file):
    real_path = os.path.abspath(os.path.join('upload', path_to_file))
    if os.path.exists(real_path):
        return send_file(real_path, as_attachment=True)
    else:
        return "Файл не найден " + real_path, 404

def clear_upload_dir():
    print('очищаем папку от старых файлов')
    path = os.path.abspath(os.path.join('upload'))
    now = datetime.datetime.now()
    for r, d, f in os.walk(path):
        for file in f:
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join('upload', file)))
            delta = now - file_date
            if (delta.seconds / 60 > 2):
                os.remove(os.path.join(path, file))

if __name__ == '__main__':
    app.run(host='0.0.0.0')