from flask import Flask, render_template, redirect, url_for, flash
from forms import ContactForm
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moje_tajne_heslo_123'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')#DAtábaze SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optimalizace vykonu

db = SQLAlchemy(app)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Automaticke ID
    name = db.Column(db.String(100), nullable=False) # Jméno Uživatele
    email = db.Column(db.String(100), nullable=False) # Email uživatele
    message = db.Column(db.Text, nullable=False) # Zpráva uživatele

    def __repr__(self):
        return f"Message(¨{self.name}¨, '{self.email}')"
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
        print("✅ Formulář prošel validací")
        new_message = Message(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(new_message)
        db.session.commit()
        print("📦 Uloženo do databáze")
        flash(f'Děkujeme {form.name.data}, tvoje zpráva byla uložena!', 'success')
        return redirect(url_for('kontakt'))
    else:
        print("❌ Formulář NEprošel validací")
        print(form.errors)

# načteme zprávy z databáze
    messages = Message.query.order_by(Message.id.desc()).all()
    return render_template('contact.html', form=form, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
