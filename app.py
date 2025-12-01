from flask import Flask, request, jsonify
from flask_cors import CORS 
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.languages import POR
import pandas as pd
import random
import psycopg2 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURAÇÃO DO BANCO ---
DB_HOST = "localhost"
DB_NAME = "projeto_integrador_III"
DB_USER = "postgres"
DB_PASS = "123456" 

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        return None

# --- INICIALIZAÇÃO DO BANCO (CRIA AS 3 TABELAS) ---
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        
        # 1. Tabela de Usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL, 
                senha VARCHAR(255) NOT NULL
            );
        """)
        

        cur.execute("""
            CREATE TABLE IF NOT EXISTS respostas_quiz (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                q1 VARCHAR(50), q2 VARCHAR(50), q3 VARCHAR(50), q4 VARCHAR(50),
                q5 VARCHAR(50), q6 VARCHAR(50), q7 VARCHAR(50), q8 VARCHAR(50),
                q9 VARCHAR(50), q10 VARCHAR(50),
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_quiz_usuario FOREIGN KEY (email) REFERENCES usuarios(email) ON DELETE CASCADE
            );
        """)


        cur.execute("""
            CREATE TABLE IF NOT EXISTS minhas_reservas (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                nome_roteiro VARCHAR(100),
                status VARCHAR(50) DEFAULT 'Em Análise',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_reserva_usuario FOREIGN KEY (email) REFERENCES usuarios(email) ON DELETE CASCADE
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("Banco de dados inicializado com sucesso!")


try:
    df = pd.read_excel("./cs.xlsx") 
    conversa_limpa = [item for item in list(df['Perguntas e Respostas']) if isinstance(item, str)]
    bot = ChatBot('Tour4Friends Bot', tagger_language=POR)
    trainer = ListTrainer(bot)
    trainer.train(conversa_limpa)
except:
    bot = ChatBot('Tour4Friends Bot', tagger_language=POR) 

respostas_padrao = ['Não entendi...', 'Pode perguntar de novo?']



@app.route('/perguntar', methods=['POST'])
def perguntar():
    dados = request.get_json()
    pergunta = dados.get('pergunta')
    if not pergunta: return jsonify({"resposta": "Erro"})
    try:
        resposta = bot.get_response(pergunta)
        return jsonify({"resposta": str(resposta) if resposta.confidence > 0.4 else random.choice(respostas_padrao)})
    except:
        return jsonify({"resposta": "Erro interno do bot."})

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')
    
    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro no banco"}), 500
    
    cur = conn.cursor()
    cur.execute("SELECT nome, senha FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if usuario and check_password_hash(usuario[1], senha):
        return jsonify({"sucesso": True, "nome": usuario[0]})
    
    return jsonify({"sucesso": False, "mensagem": "E-mail ou senha incorretos."}), 401

# --- ROTA RESTAURADA: CADASTRO ---
@app.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({"sucesso": False, "mensagem": "Preencha todos os campos!"}), 400

    senha_hash = generate_password_hash(senha)
    conn = get_db_connection()
    if not conn: return jsonify({"sucesso": False, "mensagem": "Erro no banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha_hash))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"sucesso": True, "mensagem": "Cadastro realizado!"})
    
    except psycopg2.IntegrityError:
        return jsonify({"sucesso": False, "mensagem": "E-mail já cadastrado!"}), 400
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500

@app.route('/salvar_quiz', methods=['POST'])
def salvar_quiz():
    dados = request.get_json()
    email = dados.get('email')
    respostas = dados.get('respostas')

    if not email or not respostas:
        return jsonify({"sucesso": False, "mensagem": "Dados incompletos"}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Verifica se o usuário existe antes de salvar (Segurança da Chave Estrangeira)
        cur.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
        if not cur.fetchone():
            return jsonify({"sucesso": False, "mensagem": "Usuário não encontrado. Faça login novamente."}), 400

        cur.execute("""
            INSERT INTO respostas_quiz (email, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            email, 
            respostas.get('q1'), respostas.get('q2'), respostas.get('q3'), respostas.get('q4'), 
            respostas.get('q5'), respostas.get('q6'), respostas.get('q7'), respostas.get('q8'), 
            respostas.get('q9'), respostas.get('q10')
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"sucesso": True, "mensagem": "Respostas salvas!"})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500

@app.route('/minhas_reservas', methods=['POST'])
def minhas_reservas():
    dados = request.get_json()
    email = dados.get('email')
    if not email: return jsonify([])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM respostas_quiz WHERE email = %s ORDER BY data_envio DESC", (email,))
    rows = cur.fetchall()
    
    colnames = [desc[0] for desc in cur.description]
    lista_reservas = []
    for row in rows:
        item = dict(zip(colnames, row))
        if isinstance(item.get('data_envio'), datetime):
            item['data_envio'] = item['data_envio'].strftime("%d/%m/%Y")
        lista_reservas.append(item)

    cur.close()
    conn.close()
    return jsonify(lista_reservas)

init_db()

if __name__ == '__main__':
    app.run(port=5000, debug=True)