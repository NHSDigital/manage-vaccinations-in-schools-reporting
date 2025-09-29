from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import InputRequired


class DataTypeForm(FlaskForm):
    """Form for selecting the type of data to download"""

    CHILD_RECORDS = "child-records"
    AGGREGATE_DATA = "aggregate-data"

    data_type = RadioField(
        id="data_type",
        label="What kind of data do you want to download?",
        name="data_type",
        validators=[InputRequired(message="Select a kind of data to download")],
        choices=[
            (CHILD_RECORDS, "Child-level vaccination record data"),
            (AGGREGATE_DATA, "Aggregate vaccination and consent data"),
        ],
    )
