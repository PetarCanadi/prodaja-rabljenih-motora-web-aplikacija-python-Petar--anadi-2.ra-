#potrebno instalirati visual studio code
# potrebno instalirati python 3.1.2
#potrebno instalirati flask za mogucnost izrade web aplikacije
#potrebno instalirati waitress( za development local server)
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user
from waitress import serve
import json
import os

# LoginManager
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Putanja do datoteke za korisnike
USERS_FILE = 'users.json'

# Putanja do datoteke za ponudu motora za kupnju
MOTORS_FILE = 'motors.json'

# Provjeri postoji li datoteka s korisnicima, ako ne postoji, stvori je
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as file:
        json.dump([], file)

# Provjeri postoji li datoteka s ponudom motora za kupnju, ako ne postoji, stvori je
if not os.path.exists(MOTORS_FILE):
    with open(MOTORS_FILE, 'w') as file:
        json.dump([], file)

# Konfiguracija Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            return User()

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

def load_users():
    with open(USERS_FILE, 'r') as file:
        return json.load(file)

def save_motors(motors):
    with open(MOTORS_FILE, 'w') as file:
        json.dump(motors, file)

def load_motors():
    with open(MOTORS_FILE, 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Ovdje možete dodati dodatne informacije koje želite prikupiti prilikom registracije

        # Provjera je li korisnik već registriran
        users = load_users()
        for user in users:
            if user['username'] == username:
                flash('Korisničko ime već postoji. Molimo odaberite drugo korisničko ime.', 'error')
                return redirect(url_for('register'))

        # Stvaranje novog korisnika
        new_user = {'id': len(users) + 1, 'username': username, 'password': password}
        users.append(new_user)
        save_users(users)
        flash('Uspješno ste se registrirali. Molimo prijavite se.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Provjera valjanosti korisničkog imena i lozinke
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                # Prijavite korisnika i preusmjeravanje  na nadzornu ploču (dashboard)
                user_obj = User()
                user_obj.id = user['id']
                login_user(user_obj)
                return redirect(url_for('dashboard'))
        flash('Pogrešno korisničko ime ili lozinka!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/prodaja', methods=['GET', 'POST'])
def prodaja():
    if request.method == 'POST':
        marka = request.form['marka']
        model = request.form['model']
        godiste = request.form['godiste']
        kilometri = request.form['kilometri']
        snaga = request.form['snaga']
        obujam = request.form['obujam']
        prodavac = request.form['prodavac']
        telefon = request.form['telefon']
        cijena = request.form['cijena']  # Dodano dohvaćanje cijene

        slika = request.files['slika']  # Dodano dohvaćanje datoteke
        if slika:
            slika_filename = slika.filename
            slika_path = os.path.join('static', slika_filename)
            slika.save(slika_path)

        # Stvaranje novog motora
        novi_motor = {
            'marka': marka,
            'model': model,
            'godiste': godiste,
            'kilometri': kilometri,
            'snaga': snaga,
            'obujam': obujam,
            'prodavac': prodavac,
            'telefon': telefon,
            'slika': slika_filename,  # Ime datoteke
            'cijena': cijena
        }

        # Dodavanje novog motora u listu motora za kupnju
        motors = load_motors()
        motors.append(novi_motor)
        save_motors(motors)

        flash('Novi motor je uspješno dodan u ponudu za kupnju.', 'success')
        return redirect(url_for('kupnja'))

    return render_template('prodaja.html')

@app.route('/kupnja')
def kupnja():
    # Dohvaćanje liste motora za kupnju
    primjeri_motora_za_kupnju = load_motors()
    return render_template('kupnja.html', primjeri_motora=primjeri_motora_za_kupnju)

if __name__ == "__main__":
    app.debug = True  # Omogući debug mod
    serve(app, host='127.0.0.1', port=5000)
