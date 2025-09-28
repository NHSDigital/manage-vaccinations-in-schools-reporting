from flask_wtf import FlaskForm
from wtforms import RadioField, SelectMultipleField
from wtforms.validators import InputRequired, Optional


class DownloadForm(FlaskForm):
    """Form for selecting the programme and variables to download data for"""

    programme = RadioField(
        id="programme",
        label="Which programme do you want to download data for?",
        name="programme",
        validators=[InputRequired(message="Please select a programme")],
    )

    variables = SelectMultipleField(
        name="variables",
        id="variables",
        label="How would you like to break down the data?",
        validators=[Optional()],
    )

    def __init__(self, programmes, variables, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.programmes = programmes
        self.programme.choices = [
            (programme["value"], programme["text"]) for programme in self.programmes
        ]
        self.variables.choices = [
            (variable["value"], variable["text"]) for variable in variables
        ]
