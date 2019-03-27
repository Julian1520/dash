import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments
import dash_table
import os
import random
import datetime
import plotly.graph_objs as go
import dash_auth
import argparse
import pandas as pd
from postgres_utils import BankingDatabase
from dash.dependencies import Input, Output
from user_credentials import VALID_USERNAME_PASSWORD_PAIRS
from faker import Faker
from sql_queries import *


# from dash_utils_visuals import *
# from dash_utils_callback_functions import *

class SmartDataTable(object):

    def __init__(self, object_id):
        self.id = object_id

    def visual_smart_data_table(self):
        return dash_table_experiments.DataTable(
            rows=[{}],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id=self.id)

    @staticmethod
    def visual_datepicker(id_datepicker, df_date_column):
        return dcc.DatePickerRange(
            id=id_datepicker,
            start_date=df_date_column.min(),
            end_date=datetime.date.today(),
            min_date_allowed=df_date_column.min(),
            max_date_allowed=datetime.datetime.now(),
            end_date_placeholder_text="Select a date"
        )

    @staticmethod
    def call_back_datepicker_smart_data_table(df, df_date_column_name):
        def update_table(start_date, end_date):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

            transactions_filtered = df[(df[df_date_column_name] > start_date) & (df[df_date_column_name] < end_date)]

            return transactions_filtered.to_dict('records')

        return update_table


class SimpleDataTable(object):

    def __init__(self, object_id):
        self.id = object_id

    def visual_simple_data_table(self, df):
        return dash_table.DataTable(
            id=self.id,
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('rows'),
            style_data_conditional=[{
                "if": {"row_index": 2},
                "fontWeight": "bold"
            }]
        )


class MultiLineChart(object):

    def __init__(self, object_id):
        self.id = object_id

    def visual_graph(self):
        return dcc.Graph(id=self.id)

    @staticmethod
    def visual_dropdown(id_dropdown, list_picker_options):
        return dcc.Dropdown(
            id=id_dropdown,
            options=[{"label": i, "value": i} for i in
                     list_picker_options],
            value=[i for i in list_picker_options],
            multi=True,
        )

    @staticmethod
    def call_back_dropdown_multiline_graph(df, df_distinguish_column_name, df_x_column_name, df_y_column_name):
        def plot_time_series(dropdown_value):
            data = []
            for x in dropdown_value:
                trace = go.Scatter(
                    x=df[df[df_distinguish_column_name] == x][df_x_column_name],
                    y=df[df[df_distinguish_column_name] == x][df_y_column_name],
                    mode='lines',
                    name=x
                )
                data.append(trace)
            return {
                "data": data,
                "layout": go.Layout(
                    autosize=True,
                    showlegend=True,
                )
            }

        return plot_time_series


class MultipleStackedBarChart(object):

    def __init__(self, object_id):
        self.id = object_id

    def visual_graph(self):
        return dcc.Graph(id=self.id)

    @staticmethod
    def visual_datepicker(id_datepicker, df_date_column):
        return dcc.DatePickerRange(
            id=id_datepicker,
            start_date=df_date_column.min(),
            end_date=datetime.date.today(),
            min_date_allowed=df_date_column.min(),
            max_date_allowed=datetime.datetime.now(),
            end_date_placeholder_text="Select a date"
        )

    @staticmethod
    def call_back_datepicker_multiple_stacked_bar_chart(df, df_date_column_name, df_y_column_name,
                                                        df_stacking_values_column_name, color_list):
        def update_graph(start_date, end_date):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

            filtered_df = df[(df[df_date_column_name] > start_date) & (
                    df[df_date_column_name] < end_date)]

            data = list()
            count = 0
            in_out_dict = (
                filtered_df.groupby(df_stacking_values_column_name).apply(
                    lambda x: (list(x[df_y_column_name]), list(x[df_date_column_name]))).to_dict())

            for key, value in in_out_dict.items():
                data.append(go.Bar(
                    x=value[1],
                    y=value[0],
                    name=key,
                    marker=go.bar.Marker(
                        color=color_list[count]
                    )
                ))
                count = count + 1

            return {
                "data": data,
                "layout": go.Layout(
                    autosize=True,
                    showlegend=True,
                    barmode='relative',
                )
            }

        return update_graph


class BarChart(object):
    def __init__(self, object_id):
        self.id = object_id

    def visual_bar_chart(self, df, df_identifier_column_name, df_value_column_name):
        temp_list = []
        for x in range(0, len(df)):
            temp_list.append({'x': ['Assets'], 'y': [df.iloc[x][df_value_column_name]], 'type': 'bar',
                              'name': df.iloc[x][df_identifier_column_name]})
        return dcc.Graph(
            id=self.id,
            figure={
                'data': temp_list,

            }
        )


class PieChart(object):
    def __init__(self, object_id):
        self.id = object_id

    def visual_pie_chart(self, df, df_identifier_column_name, df_value_column_name):
        return dcc.Graph(id=self.id,
                         figure=go.Figure(
                             data=[go.Pie(labels=list(df[df_identifier_column_name]),
                                          values=list(df[df_value_column_name]))],
                         ))
