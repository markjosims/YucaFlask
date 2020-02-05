from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import Entry


class EntryForm(FlaskForm):
    headword = StringField( 'Form', validators=[DataRequired()] )
    pos = StringField( 'Grammatical Category', validators=[DataRequired()] )
    gloss = StringField( 'Gloss', validators=[DataRequired()] )
    submit = SubmitField('Create')