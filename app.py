from flask import Flask, redirect, url_for, render_template, request, flash, jsonify  
from models import create_subscription, get_subscriptions, update_subscription, delete_subscription  
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  
from werkzeug.security import generate_password_hash, check_password_hash  
from database import get_db_connection  
import secrets

app = Flask(__name__)  
app.secret_key = secrets.token_hex(16)

login_manager = LoginManager()  
login_manager.init_app(app)  
login_manager.login_view = 'login'  

class User(UserMixin):  
    def __init__(self, id):  
        self.id = id  

def log_audit_action(action, user_id=None, subscription_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    

    cur.execute(
        "INSERT INTO audit (action, user_id, subscription_id) VALUES (%s, %s, %s);",
        (action, user_id, subscription_id)
    )
    
    conn.commit()
    cur.close()
    conn.close()

@app.route('/dashboard')  
@login_required  
def dashboard():  
    return render_template('dashboard.html')  

@login_manager.user_loader  
def load_user(user_id):  
    conn = get_db_connection()  
    cur = conn.cursor()  
    cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))  
    user = cur.fetchone()  
    cur.close()  
    conn.close()  
    return User(user[0]) if user else None  

@app.route('/login', methods=['GET', 'POST'])  
def login():  
    if request.method == 'POST':  
        username = request.form['username']  
        password = request.form['password']  

        conn = get_db_connection()  
        cur = conn.cursor()  
        cur.execute("SELECT * FROM users WHERE username = %s;", (username,))  
        user = cur.fetchone()
        cur.close()  
        conn.close()  

        if user and check_password_hash(user[2], password):    
            user_obj = User(user[0])  
            login_user(user_obj)  
            return redirect(url_for('dashboard'))  
        else:  
            flash('Неверное имя пользователя или пароль')  

    return render_template('login.html')  

@app.route('/logout')  
@login_required  
def logout():  
    logout_user()  
    return redirect(url_for('login'))  

@app.route('/register', methods=['GET', 'POST']) 
def register(): 
    if request.method == 'POST': 
        username = request.form['username'] 
        password = request.form['password'] 
        
        # Проверка на существование пользователя 
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute("SELECT * FROM users WHERE username = %s;", (username,)) 
        existing_user = cur.fetchone() 

        if existing_user: 
            flash('Пользователь с таким именем уже существует.') 
            cur.close() 
            conn.close() 
            return redirect(url_for('register')) 
        # Проверка на пустые поля
        if not username or not password:
            flash('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('register'))

        # Хеширование пароля 
        hashed_password = generate_password_hash(password) 

        # Добавление нового пользователя в базу данных 
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, hashed_password)) 
        conn.commit() 
        cur.close() 
        conn.close() 

        flash('Вы успешно зарегистрировались! Теперь вы можете войти в систему.') 
        return redirect(url_for('login')) 

    return render_template('register.html') 

@app.route('/subscriptions', methods=['POST'])
def create_new_subscription():
    data = request.json
    subscription_id = create_subscription(
        name=data['name'],
        amount=data['amount'],
        frequency=data['frequency'],
        start_date=data['start_date'],
        user_id=data['user_id']
    )
    log_audit_action('Создана подписка', data['user_id'], subscription_id)
    return jsonify({'message': 'Subscription created'}), 201

@app.route('/subscriptions', methods=['GET'])
def list_subscriptions():
    user_id = request.args.get('user_id')
    subscriptions = get_subscriptions(user_id)
    return jsonify([{
        'id': sub[0],
        'name': sub[1],
        'amount': sub[2],
        'frequency': sub[3],
        'start_date': sub[4]
    } for sub in subscriptions])

@app.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
def update_subscription_route(subscription_id):
    data = request.get_json()
    update_subscription(subscription_id, data['amount'], data['frequency'], data['start_date'])
    log_audit_action('Обновлена подписка', current_user.id, subscription_id)
    return jsonify({"message": "Подписка обновлена!"}), 200

@app.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
def delete_subscription_route(subscription_id):
    delete_subscription(subscription_id)
    log_audit_action('Удалена подписка', current_user.id, subscription_id)
    return jsonify({"message": "Подписка удалена!"}), 200

