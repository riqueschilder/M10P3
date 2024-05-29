from flask import Flask, jsonify, request
import psycopg2
import logging
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

app = Flask(__name__)

conn = psycopg2.connect(
    host='db',
    database='postgres',
    user='postgres',
    password='postgres'
)

def log_to_api(level, message, logger_name):
    try:
        data = {
            'level': level,
            'message': message,
            'logger_name': logger_name
        }
        requests.post('http://10.150.8.26:8000/log', json=data)
    except Exception as e:
        print(f'Failed to send log to API: {str(e)}')

@app.route('/login', methods=['POST'])
def login():
    log_to_api('INFO', 'Login request received', 'loginHandler')
    data = request.get_json()
    email = data['email']
    password = data['password']

    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s AND senha = %s', (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            log_to_api('INFO', f'Login successful for user: {email}', 'loginHandler')
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'message': 'Invalid credentials'})
    except Exception as e:
        log_to_api('ERROR', f'Error during login: {str(e)}', 'loginHandler')
        return jsonify({'message': str(e)})

@app.route('/register', methods=['POST'])
def register():
    log_to_api('INFO', 'Register request received', 'registerHandler')
    data = request.get_json()
    email = data['email']
    password = data['password']

    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (email, senha) VALUES (%s, %s)', (email, password))
        conn.commit()
        cur.close()
        log_to_api('INFO', f'User {email} created successfully', 'registerHandler')
        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        log_to_api('ERROR', f'Error creating user: {str(e)}', 'registerHandler')
        return jsonify({'message': str(e)})


@app.route('/users', methods=['GET'])
def users():
    try:
        log_to_api('INFO', 'Users request received', 'usersHandler')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        cur.close()

        return jsonify(users)
    except Exception as e:
        log_to_api('ERROR', f'Error getting users: {str(e)}', 'usersHandler')
        return jsonify({'message': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)