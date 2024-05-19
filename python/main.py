from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from translatelatex import translate
from time import time
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_expression():
    start = time()
    print("Received POST request to /translate")
    
    real_ip = request.headers.get('X-Real-IP')
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        real_ip = forwarded_for.split(',')[0]  # Get the first IP in the list

    print(f"Received POST request to /translate")
    print(f"Requester IP: {real_ip}")


    
    data = request.json
    expression = data.get('expression', '')
    settings = {
        'TI_on': data.get('TI_on', True),
        'SC_on': data.get('SC_on', False),
        'constants_on': data.get('constants_on', False),
        'coulomb_on': data.get('coulomb_on', False),
        'e_on': data.get('e_on', False),
        'i_on': data.get('i_on', False),
        'g_on': data.get('g_on', False)
    }
    print("Expression:", expression)
    result = translate(expression, **settings)
    print("Translation Result:", result)
    print(f"Time taken: {(time() - start) * 1000:.2f} milliseconds")
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
