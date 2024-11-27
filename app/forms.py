from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField

class LoginForm(FlaskForm):
    username = StringField("username")
    email=StringField("email")
    address=StringField("address")
    postal_code=StringField("postal_code")
    city=StringField("city")
    phone_number=StringField("phone_number")
    submit=SubmitField('login')
