import dash_core_components as dcc
import datetime


def return_datepicker(id, df_date_column):
    return dcc.DatePickerRange(
        id=id,
        start_date=df_date_column.min(),
        end_date=datetime.date.today(),
        min_date_allowed=df_date_column.min(),
        max_date_allowed=datetime.datetime.now(),
        end_date_placeholder_text="Select a date"
    )


def return_dropdown(id, list_picker_options):
    return dcc.Dropdown(
        id=id,
        options=[{"label": i, "value": i} for i in
                 list_picker_options],
        value=[i for i in list_picker_options],
        multi=True,
    )
