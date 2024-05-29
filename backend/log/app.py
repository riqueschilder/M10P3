from flask import Flask, jsonify, request
import psycopg2
import logging
from psycopg2 import pool

app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'db',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

# Configuração de pool de conexões
conn_pool = pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para obter conexão do pool
def get_db_connection():
    return conn_pool.getconn()

# Função para liberar conexão ao pool
def release_db_connection(conn):
    conn_pool.putconn(conn)

# Função para registrar logs no banco de dados
def log_to_db(level, message, logger_name):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('INSERT INTO logs (level, message, logger_name) VALUES (%s, %s, %s)', (level, message, logger_name))
        conn.commit()
    except Exception as e:
        logger.error(f'Error logging to database: {str(e)}')
    finally:
        if conn:
            release_db_connection(conn)

# Rota para registrar logs
@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    if not data or 'level' not in data or 'message' not in data or 'logger_name' not in data:
        return jsonify({'message': 'Invalid data'}), 400
    
    level = data['level']
    message = data['message']
    logger_name = data['logger_name']

    log_to_db(level, message, logger_name)
    
    return jsonify({'message': 'Log registered successfully'})

# Rota para requisitar logs
@app.route('/logs', methods=['GET'])
def get_logs():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT id, timestamp, level, message, logger_name FROM logs')
            logs = cur.fetchall()
        
        logs_list = [{
            'id': log[0],
            'timestamp': log[1],
            'level': log[2],
            'message': log[3],
            'logger_name': log[4]
        } for log in logs]

        return jsonify(logs_list)
    except Exception as e:
        logger.error(f'Error retrieving logs from database: {str(e)}')
        return jsonify({'message': str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
