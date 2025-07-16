from flask import Flask, jsonify, request, send_from_directory, render_template, make_response
from flask_cors import CORS
from translatelatex import translate
import logging
from time import time
from os import path, makedirs
import signal

app = Flask(__name__)
CORS(app)

# Ensure the logs directory exists
if not path.exists('logs'):
    makedirs('logs')

# Configure logging for general logs
log_handler = logging.FileHandler('logs/app.log')  # Save logs in the logs folder
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
log_handler.setFormatter(formatter)

# Configure logging for error logs
error_log_handler = logging.FileHandler('logs/error.log')  # Separate file for error logs
error_log_handler.setLevel(logging.ERROR)
error_log_handler.setFormatter(formatter)

# Set up logger
app_logger = logging.getLogger('app_logger')
app_logger.addHandler(log_handler)  # Add general log handler
app_logger.addHandler(error_log_handler)  # Add error log handler
app_logger.setLevel(logging.INFO)  # Log at INFO level and above

abbreviations = {
'TI_on': 'TI',
'SC_on': 'SC',
'constants_on': 'CO',
'coulomb_on': 'CL',
'e_on': 'E',
'i_on': 'I',
'g_on': 'G'
}

# Simple timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(_signum, _frame):  # Underscore prefix indicates intentionally unused parameters
    raise TimeoutError("Translation timeout")

# Serve all files in the 'templates' directory
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/<path:filename>')
def serve_file(filename):
    # Serve files from the 'templates' directory
    return send_from_directory(path.join('src', 'templates', 'reference', 'modules', 'ROOT'), filename)

@app.route('/translate', methods=['POST', 'GET', 'OPTIONS'])
def translate_expression():
    if request.method == 'POST':
        # Handle POST requests (e.g., translating an expression)
        start_time = time()
        try:
            real_ip = request.headers.get('X-Real-IP')
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                real_ip = forwarded_for.split(',')[0]

            data = request.json
            if data is None:
                return jsonify({'error': 'Invalid JSON data.'}), 400
                
            expression = data.get('expression', '')
            
            # Block overly long requests
            if len(expression) > 10000000000:
                return jsonify({'error': 'Expression too long. Please use shorter expressions.'}), 400
            
            settings = {
                'TI_on': data.get('TI_on', True),
                'SC_on': data.get('SC_on', False),
                'constants_on': data.get('constants_on', False),
                'coulomb_on': data.get('coulomb_on', False),
                'e_on': data.get('e_on', False),
                'i_on': data.get('i_on', False),
                'g_on': data.get('g_on', False)
            }

            # Create a string of active settings using the first letter of each setting name
            active_settings = " ".join([abbr for setting, abbr in abbreviations.items() if settings.get(setting, False)])

            # Set timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout
            
            try:
                result = translate(expression, **settings)
            finally:
                signal.alarm(0)  # Cancel timeout
            
            time_taken = (time() - start_time) * 1000

            # Log the successful translation along with the active settings
            app_logger.info(f"{real_ip} | {expression} | {result} | {time_taken:.2f} ms | Active Settings: {active_settings}")
            return jsonify({'result': result})

        except TimeoutError:
            time_taken = (time() - start_time) * 1000
            app_logger.error(f"{real_ip} | {expression} | TIMEOUT | {time_taken:.2f} ms")
            return jsonify({'error': 'Translation timeout. Please try a simpler expression.'}), 408
        except Exception as e:
            time_taken = (time() - start_time) * 1000
            # Log the error in both app.log and error.log
            app_logger.error(f"{real_ip} | {expression} | Error: {str(e)} | {time_taken:.2f} ms")
            return jsonify({'error': 'An error occurred during translation.'}), 500

    elif request.method == 'GET':
        # Serve an HTML page
        return render_template('translate.html')  # Make sure you have this template

    elif request.method == 'OPTIONS':
        # Handle CORS preflight requests
        response = make_response('', 204)  # No content for OPTIONS requests
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    return jsonify({"error": "Method not allowed."}), 405  # For unsupported methods

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
