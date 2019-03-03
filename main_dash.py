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
from dash_utils_visuals import *
from dash_utils_callback_functions import *

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

balance_all = float(sparkasse_balance.amount[0]) + float(dkb_balance.amount[0]) + float(cc_balance.amount[0]) + float(
    depot_balance.amount[0])

if parsed_args.test == 'yes':
    transactions['amount'] = [fake.random_number(3) for i in range(transactions.amount.size)]
    transactions['applicant_name'] = [fake.first_name() for i in range(transactions.applicant_name.size)]
    transactions['purpose'] = [fake.catch_phrase() for i in range(transactions.purpose.size)]

in_out.date_trunc = in_out.date_trunc.apply(lambda x: x.date())

app = dash.Dash(__name__)

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
app.layout = html.Div(className="app-header",
                      style={'backgroundColor': colors['background']},
                      children=[

                          html.Div([
                              html.Header('Financial Overview',
                                          style={'display': 'inline',
                                                 # 'float': 'left',
                                                 'font-size': '2.65em',
                                                 'margin-left': '90px',
                                                 'margin-top': '30px',
                                                 'font-weight': 'bolder',
                                                 'font-family': 'Sans-Serif',
                                                 'color': "rgba(117, 117, 117, 0.95)"
                                                 }),
                              html.Img(
                                  src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                                  style={
                                      'height': '53px',
                                      'float': 'right'
                                  },
                              ),
                          ]),

                          html.Div([
                              html.Div([
                                  dash_table.DataTable(
                                      id='stock_table',
                                      columns=[{"name": i, "id": i} for i in overview.columns],
                                      data=overview.to_dict('rows'),
                                      style_table={
                                          'maxWidth': '500px',
                                          'overflowY': 'scroll',
                                          'margin-top': '20px'
                                      },
                                      style_data_conditional=[{
                                          "if": {"row_index": 2},
                                          "fontWeight": "bold"
                                      }]
                                  ),
                              ], style={'width': '42%', 'display': 'inline-block'}),

                              html.Div([
                                  html.H1('Balance over time'),
                                  return_dropdown('my-dropdown', balance_chart['Cash location'].unique()),
                                  dcc.Graph(id='my-graph')
                              ], style={'width': '49%', 'display': 'inline-block'}),
                          ]),

                          html.Div([
                              html.Div([
                                  dcc.Graph(
                                      id='Graph1',
                                      figure={
                                          'data': [
                                              {'x': ['Assets'], 'y': [sparkasse_balance.amount[0]], 'type': 'bar',
                                               'name': 'Sparkasse'},
                                              {'x': ['Assets'], 'y': [dkb_balance.amount[0]], 'type': 'bar',
                                               'name': u'DKB'},
                                              {'x': ['Assets'], 'y': [cc_balance.amount[0]], 'type': 'bar',
                                               'name': u'CC'},
                                              {'x': ['Assets'], 'y': [depot_balance.amount[0]], 'type': 'bar',
                                               'name': u'Depot'}
                                          ],
                                          'layout': {
                                              'title': 'Asset allocation',
                                              'plot_bgcolor': colors['background'],
                                              'paper_bgcolor': colors['background'],
                                              'font': {
                                                  'color': colors['text']
                                              }
                                          }
                                      }
                                  )
                              ], style={'width': '49%', 'display': 'inline-block'}),

                              html.Div([
                                  dcc.Graph(id='stock_overview',
                                            figure=go.Figure(
                                                data=[go.Pie(labels=list(stocks.name),
                                                             values=list(stocks.value))],
                                                layout=go.Layout(
                                                    title='Stock overview')
                                            ))
                              ], style={'width': '49%', 'display': 'inline-block'}),
                          ]),

                          return_datepicker('date-picker-in_out', in_out.date_trunc),

                          dcc.Graph(id="in-out-graph"),

                          return_datepicker('date-picker-range', transactions.date),

                          html.H1('Transactions'),
                          dash_table_experiments.DataTable(
                              rows=[{}],
                              row_selectable=True,
                              filterable=True,
                              sortable=True,
                              selected_row_indices=[],
                              id='table'),

                      ])

call_back_temp1 = call_back_dropdown_multiline_graph(balance_chart, 'Cash location', 'date', 'amount')
call_back_temp1 = app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])(call_back_temp1)

call_back_temp2 = call_back_datepicker_tablbe(transactions, 'date')
call_back_temp2 = app.callback(Output("table", "rows"),
                            [Input("date-picker-range", "start_date"),
                             Input("date-picker-range", "end_date")])(call_back_temp2)


@app.callback(
    Output("in-out-graph", "figure"),
    [Input("date-picker-in_out", "start_date"),
     Input("date-picker-in_out", "end_date")]
)
def update_graph(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    filtered_df = in_out[(in_out['date_trunc'] > start_date) & (in_out['date_trunc'] < end_date)]

    data = list()
    count = 0
    in_out_dict = (filtered_df.groupby('tag').apply(lambda x: (list(x['amount']), list(x['date_trunc']))).to_dict())

    for key, value in in_out_dict.items():
        data.append(go.Bar(
            x=value[1],
            y=value[0],
            name=key,
            marker=go.bar.Marker(
                color=colors['in_out_color'][count]
            )
        ))
        count = count + 1

    return {
        "data": data,
        "layout": go.Layout(
            autosize=True,
            title='Net-in-out',
            showlegend=True,
            barmode='relative',
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
