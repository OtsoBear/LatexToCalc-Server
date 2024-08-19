from os import path, makedirs
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from translatelatex import translate
import logging
from time import time

app = Flask(__name__)
CORS(app)

# Ensure the logs directory exists
if not path.exists('logs'):
    makedirs('logs')

# Configure logging
log_handler = logging.FileHandler('logs/app.log')  # Save logs in the logs folder
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
log_handler.setFormatter(formatter)

app_logger = logging.getLogger('app_logger')
app_logger.addHandler(log_handler)
app_logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_expression():
    start_time = time()

    try:
        # Get client IP address
        real_ip = request.headers.get('X-Real-IP')
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            real_ip = forwarded_for.split(',')[0]  # Use the first IP in the list

        # Extract translation data from the request
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

        # Perform translation
        result = translate(expression, **settings)
        time_taken = (time() - start_time) * 1000

        # Log the translation process
        app_logger.info(f"{real_ip} | {expression} | {result} | {time_taken:.2f} ms | None".replace("\n", " "))

        return jsonify({'result': result})

    except Exception as e:
        # Handle and log errors
        time_taken = (time() - start_time) * 1000
        app_logger.error(f"{real_ip} | {expression} | Error: {str(e)} | {time_taken:.2f} ms".replace("\n", " "))
        return jsonify({'error': 'An error occurred during translation.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
