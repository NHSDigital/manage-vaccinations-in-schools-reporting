from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import InputRequired


class DataTypeForm(FlaskForm):
    """Form for selecting the type of data to download"""

    CHILD_RECORDS = "child-records"
    AGGREGATE_DATA = "aggregate-data"

    data_type = RadioField(
        id="data_type",
        label="What data do you want to download?",
        name="data_type",
        validators=[InputRequired(message="Select which data you want to download")],
        choices=[
            (CHILD_RECORDS, "Child-level vaccination data"),
            (AGGREGATE_DATA, "Aggregate vaccination and consent data"),
        ],
    )

    hints = {
        CHILD_RECORDS: "Full vaccination details for individual children. Only \
            includes vaccinations given by your team.",
        AGGREGATE_DATA: "Total figures for all children in your cohort. Includes \
            vaccinations given by any provider.",
    }
