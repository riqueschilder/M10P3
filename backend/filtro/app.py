from flask import Flask, request, send_file, jsonify
from PIL import Image
import psycopg2
import io
import logging
import requests

def configure_logging():
    """Configure the logging settings."""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = configure_logging()

app = Flask(__name__)

def connect_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host='db',
            database='postgres',
            user='postgres',
            password='postgres'
        )
        return conn
    except Exception as e:
        logger.error(f'Failed to connect to the database: {str(e)}')
        return None

conn = connect_db()

def log_to_api(level, message, logger_name):
    """Send log messages to an external logging API."""
    try:
        data = {
            'level': level,
            'message': message,
            'logger_name': logger_name
        }
        requests.post('http://172.17.0.1:8000/log', json=data)
    except Exception as e:
        logger.error(f'Failed to send log to API: {str(e)}')

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Handle image upload, convert to black and white, and return the processed image.
    """
    log_to_api('INFO', 'Upload request received', 'uploadHandler')
    if 'image' not in request.files:
        logger.warning('No image part in the request')
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']

    if file.filename == '':
        logger.warning('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file:
        logger.info('Image received: %s', file.filename)
        try:
            image = Image.open(file)
            # Convert the image to black and white
            bw_image = image.convert("L")

            img_io = io.BytesIO()
            bw_image.save(img_io, 'JPEG')
            img_io.seek(0)

            log_to_api('INFO', 'Image processed successfully', 'uploadHandler')

            return send_file(img_io, mimetype='image/jpeg')
        except Exception as e:
            logger.error('Failed to process image: %s', str(e))
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

    logger.error('File not processed')
    return jsonify({'error': 'File not processed'}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        if conn:
            conn.close()
            logger.info('Database connection closed')
