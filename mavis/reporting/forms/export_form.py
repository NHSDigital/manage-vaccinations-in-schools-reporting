from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, RadioField, SelectField
from wtforms.validators import InputRequired, Optional


class ExportForm(FlaskForm):
    """Form for requesting an async vaccination export"""

    programme_type = RadioField(
        id="programme_type",
        label="Which programme do you want data for?",
        name="programme_type",
        validators=[InputRequired(message="Select a programme")],
    )

    file_format = RadioField(
        id="file_format",
        label="Which file format do you want?",
        name="file_format",
        validators=[InputRequired(message="Select a file format")],
        choices=[
            ("mavis", "MAVIS"),
            ("systm_one", "SystmOne"),
            ("careplus", "Careplus"),
        ],
    )

    academic_year = SelectField(
        id="academic_year",
        label="Which academic year?",
        name="academic_year",
        coerce=int,
        validators=[InputRequired(message="Select an academic year")],
    )

    date_from = DateField(
        id="date_from",
        label="From date (optional)",
        name="date_from",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    date_to = DateField(
        id="date_to",
        label="To date (optional)",
        name="date_to",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    def __init__(self, programmes=None, file_formats=None, academic_years=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if programmes:
            self.programme_type.choices = [
                (p["value"], p["text"]) for p in programmes
            ]
        if file_formats:
            self.file_format.choices = [(f, f.replace("_", " ").title()) for f in file_formats]
        if academic_years:
            self.academic_year.choices = [(y, f"{y}/{str(y + 1)[2:]}") for y in academic_years]
