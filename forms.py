from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    name = StringField('Jméno', validators=[
        DataRequired(message="Prosím, vyplňte své jméno."),
        Length(min=2, message="Jméno musí mít alespoň 2 znaky.")
    ])
    email = StringField('E-mail', validators=[
        DataRequired(message="Prosím, zadejte e-mail."),
        Email(message="Zadejte platnou e-mailovou adresu.")
    ])
    message = TextAreaField('Zpráva', validators=[
        DataRequired(message="Napište zprávu, prosím."),
        Length(min=10, message="Zpráva musí mít alespoň 10 znaků.")
    ])
    submit = SubmitField('Odeslat zprávu')
