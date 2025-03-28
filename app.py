from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask_mail import Mail, Message
from forms import ContactForm
from werkzeug.security import check_password_hash, generate_password_hash
import os

# Inicializuj SQLAlchemy bez app
db = SQLAlchemy()

# Vytvoř Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'moje_tajne_heslo_123'

# Oprava DATABASE_URL
raw_uri = os.environ.get('DATABASE_URL')
if raw_uri and raw_uri.startswith("postgres://"):
    raw_uri = raw_uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = raw_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Nastavení Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# Připoj app k SQLAlchemy
db.init_app(app)

# Připoj Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Model zprávy
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Uživatelský model
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Uživatelé (zatím napevno)
users = {
    "admin": generate_password_hash("tajneheslo")
}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ROUTES

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dovednosti')
def dovednosti():
    return render_template('skills.html')

@app.route('/projekty')
def projekty():
    return render_template('projects.html')

@app.route('/kontakt', methods=['GET', 'POST'])
def kontakt():
    form = ContactForm()
    if form.validate_on_submit():
        new_message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(new_message)
        db.session.commit()
        posli_email(form.name.data, form.email.data, form.message.data)
        flash(f'Děkujeme {form.name.data}, tvoje zpráva byla odeslána!', 'success')
        return redirect(url_for('kontakt'))

    return render_template('contact.html', form=form)

@app.route('/tajny-pristup', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_hash = users.get(username)

        if user_hash and check_password_hash(user_hash, password):
            login_user(User(username))
            flash('Přihlášení proběhlo úěspěšně!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Nesprávné přihlašovací údaje', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Byl jste odhlášen.', 'info')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    messages = ContactMessage.query.order_by(ContactMessage.id.desc()).all()
    return render_template('admin.html', messages=messages)

# Odeslání emailu po odeslání zprávy z formuláře
def posli_email(jmeno, email, zprava):
    try:
        msg = Message("Nová zpráva z portfolia", recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"Jméno: {jmeno}\nE-mail: {email}\nZpráva:\n{zprava}"
        msg.reply_to = email
        mail.send(msg)
    except Exception as e:
        print("Chyba při odesílání e-mailu:", e)

if __name__ == '__main__':
    app.run(debug=True)

