from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import pool
import logging
import requests
import bcrypt

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Initialize Flask app
app = Flask(__name__)

# Configure database connection pool
db_pool = pool.SimpleConnectionPool(1, 10,
                                    host='db',
                                    database='postgres',
                                    user='postgres',
                                    password='postgres')

def get_db_connection():
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting DB connection: {str(e)}")
        raise

def return_db_connection(conn):
    try:
        db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error returning DB connection: {str(e)}")

def log_to_api(level, message, logger_name):
    try:
        data = {
            'level': level,
            'message': message,
            'logger_name': logger_name
        }
        requests.post('http://172.17.0.1:8000/log', json=data)
    except Exception as e:
        logger.error(f'Failed to send log to API: {str(e)}')

@app.route('/login', methods=['POST'])
def login():
    log_to_api('INFO', 'Login request received', 'loginHandler')
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT senha FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        return_db_connection(conn)

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
            log_to_api('INFO', f'Login successful for user: {email}', 'loginHandler')
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        log_to_api('ERROR', f'Error during login: {str(e)}', 'loginHandler')
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/register', methods=['POST'])
def register():
    log_to_api('INFO', 'Register request received', 'registerHandler')
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (email, senha) VALUES (%s, %s)', (email, hashed_password.decode('utf-8')))
        conn.commit()
        cur.close()
        return_db_connection(conn)

        log_to_api('INFO', f'User {email} created successfully', 'registerHandler')
        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        log_to_api('ERROR', f'Error creating user: {str(e)}', 'registerHandler')
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/users', methods=['GET'])
def users():
    try:
        log_to_api('INFO', 'Users request received', 'usersHandler')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT email FROM users')
        users = cur.fetchall()
        cur.close()
        return_db_connection(conn)

        return jsonify(users)
    except Exception as e:
        log_to_api('ERROR', f'Error getting users: {str(e)}', 'usersHandler')
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
