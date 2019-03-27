import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_table_experiments
import dash_table
import os
import random
import dash_auth
import argparse
import pandas as pd
from postgres_utils import BankingDatabase
from dash.dependencies import Input, Output
from user_credentials import VALID_USERNAME_PASSWORD_PAIRS
from faker import Faker
from sql_queries import *
from dash_utils_classes import MultiLineChart, SimpleDataTable, SmartDataTable, MultipleStackedBarChart, BarChart, \
    PieChart

multi_line_chart = MultiLineChart('my-graph')
simple_data_table = SimpleDataTable('stock_table')
smart_data_table = SmartDataTable('table')
multiple_stacked_bar_chart = MultipleStackedBarChart("in-out-graph")
bar_chart = BarChart('Graph1')
pie_chart = PieChart('stock_overview')

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str, help='yes to run on demo mode')
parsed_args = parser.parse_args()

fake = Faker()

if parsed_args.test == 'yes':
    obscure_int = random.uniform(3, 9)
    obscure_text = 'dummy'
else:
    obscure_int = 1

database = BankingDatabase(database_name=os.environ.get('DATABASE_BANKING'),
                           user=os.environ.get('DATABASE_BANKING_USER'),
                           password=os.environ.get('DATABASE_BANKING_PW'),
                           host=os.environ.get('DATABASE_BANKING_HOST'),
                           port=os.environ.get('DATABASE_BANKING_PORT'))

sparkasse_balance = database.read_from_db(sparkasse_balance_query.format(obscure_int))
dkb_balance = database.read_from_db(dkb_balance_query.format(obscure_int))
cc_balance = database.read_from_db(cc_balance_query.format(obscure_int))
depot_balance = database.read_from_db(depot_balance_query.format(obscure_int))
in_out = database.read_from_db(in_out_query.format(obscure_int, obscure_int, obscure_int))
transactions = database.read_from_db(transactions_query)
stocks = database.read_from_db(stocks_query.format(obscure_int))
overview = database.read_from_db(overview_query.format(obscure_int=obscure_int))
balance_chart = database.read_from_db(balance_chart_query)
balance_over_all = database.read_from_db(balance_over_all_query.format(obscure_int=obscure_int))

balance_all = float(sparkasse_balance.amount[0]) + float(dkb_balance.amount[0]) + float(cc_balance.amount[0]) + float(
    depot_balance.amount[0])

if parsed_args.test == 'yes':
    transactions['amount'] = [fake.random_number(3) for i in range(transactions.amount.size)]
    transactions['applicant_name'] = [fake.first_name() for i in range(transactions.applicant_name.size)]
    transactions['purpose'] = [fake.catch_phrase() for i in range(transactions.purpose.size)]

in_out.date_trunc = in_out.date_trunc.apply(lambda x: x.date())

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.FLATLY])

server = app.server

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

colors = {
    'background': 'rgba(0,0,0,0)',
    'text': 'rgba(1,1,1,1)',
    'in_out_color': ['rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,255,0)', 'rgb(0,255,255)',
                     'rgb(255,0,125)', 'rgb(0,255,125)', 'rgb(125,125,125)']
}

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    html.Header('Financial Overview',
                style={'display': 'inline',
                       'font-size': '2.65em',
                       'margin-left': '90px',
                       'margin-top': '30px',
                       'font-weight': 'bolder',
                       'font-family': 'Sans-Serif',
                       'color': "rgba(117, 117, 117, 0.95)"
                       }),

    dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
        dcc.Tab(label='Overview', value='tab-1-example'),
        dcc.Tab(label='In/Out', value='tab-2-example'),
        dcc.Tab(label='Test', value='tab-3-example'),
    ]),
    dbc.Row(html.H1('')),
    html.Div(id='tabs-content-example')
])


@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1-example':

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H1('Overall balance'),
                    simple_data_table.visual_simple_data_table(overview),
                ]),

                dbc.Col([
                    html.H1('Balance over time'),
                    dbc.Row(multi_line_chart.visual_dropdown('my-dropdown', balance_chart['Cash location'].unique())),
                    dbc.Row(multi_line_chart.visual_graph())
                ]),
            ]),

            dbc.Row([
                dbc.Col([
                    html.H1('Asset allocation'),
                    bar_chart.visual_bar_chart(balance_over_all, 'allocation', 'amount')
                ]),

                dbc.Col([
                    html.H1('Stock overview'),
                    pie_chart.visual_pie_chart(stocks, 'name', 'value')
                ]),
            ]),

        ]),

    elif tab == 'tab-2-example':
        return dbc.Container([
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Filters"),
                                  dbc.CardBody([
                                      html.H1('Transactions'),
                                      smart_data_table.visual_datepicker('date-picker-range',
                                                                         transactions.date),
                                      html.H1(''),
                                      html.H1('In/Out'),
                                      multiple_stacked_bar_chart.visual_datepicker('date-picker-in_out',
                                                                                   in_out.date_trunc),
                                  ])
                                  ],
                                 outline=True), width='auto'),

                dbc.Col([
                    dbc.Row(html.H1('In-Out bar chart')),
                    dbc.Row(multiple_stacked_bar_chart.visual_graph()),
                    dbc.Row(html.H1('Transactions')),
                    dbc.Row(smart_data_table.visual_smart_data_table())
                ]),
                dbc.Col(html.H1(''), width='auto')
            ]),
            dbc.Row(html.H1(''))
        ], fluid=True)


call_back_temp1 = multi_line_chart.call_back_dropdown_multiline_graph(balance_chart, 'Cash location', 'date', 'amount')
call_back_temp1 = app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])(call_back_temp1)

call_back_temp2 = smart_data_table.call_back_datepicker_smart_data_table(transactions, 'date')
call_back_temp2 = app.callback(Output("table", "rows"),
                               [Input("date-picker-range", "start_date"),
                                Input("date-picker-range", "end_date")])(call_back_temp2)

call_back_temp3 = multiple_stacked_bar_chart.call_back_datepicker_multiple_stacked_bar_chart(in_out, 'date_trunc',
                                                                                             'amount', 'tag',
                                                                                             colors['in_out_color'])
call_back_temp3 = app.callback(Output("in-out-graph", "figure"),
                               [Input("date-picker-in_out", "start_date"),
                                Input("date-picker-in_out", "end_date")])(call_back_temp3)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
