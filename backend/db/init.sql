CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(50) NOT NULL
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10),
    message TEXT,
    logger_name VARCHAR(255)
);

INSERT INTO users (email, senha) VALUES ('123@123.com', '123');