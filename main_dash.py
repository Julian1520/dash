import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments
import dash_table
import os
import datetime
from postgres_utils import BankingDatabase
import plotly.graph_objs as go
from dash.dependencies import Input, Output


database = BankingDatabase(database_name=os.environ.get('DATABASE_BANKING'),
                           user=os.environ.get('DATABASE_BANKING_USER'),
                           password=os.environ.get('DATABASE_BANKING_PW'),
                           host=os.environ.get('DATABASE_BANKING_HOST'),
                           port=os.environ.get('DATABASE_BANKING_PORT'))

sparkasse_balance = database.read_from_db('''
select amount from sparkasse_balance where date(date) =
                                             (select max(date(date)) from sparkasse_balance)
''')

dkb_balance = database.read_from_db('''
select amount from dkb_balance where date(date) =
                                             (select max(date(date)) from dkb_balance)
''')

cc_balance = database.read_from_db('''
select amount from credit_card_balance where date(date) =
                                             (select max(date(date)) from credit_card_balance)
''')

depot_balance = database.read_from_db('''
select sum(value) as amount from depot_data
''')

balance_all = float(sparkasse_balance.amount[0])+float(dkb_balance.amount[0])+float(cc_balance.amount[0])+float(depot_balance.amount[0])

in_out = database.read_from_db('''
select * from (
select date_trunc('month',date(date)),tag, sum(amount) as amount from sparkasse_transactions where tag != 'Internal transaction' group by 1,2
union all
select date_trunc('month',date(date)),tag, sum(amount) as amount from dkb_transactions where tag != 'Internal transaction' group by 1,2
union all
select date_trunc('month',date(value_date)),tag, sum(amount) as amount from credit_card_data where tag != 'Internal transaction' group by 1,2)a
-- where date_trunc between date('2018-07-01') AND date('{}')
''')

transactions = database.read_from_db('''
select amount, applicant_name, date(date), posting_text, purpose, bank_name,tag from dkb_transactions
union all
select amount, applicant_name, date(date), posting_text, purpose, bank_name,tag from sparkasse_transactions
union all
select amount, description as applicant_name, date(voucher_date), 'NA' as posting_text, 'NA' as purpose, 'NA' as bank_name, tag  from credit_card_data
order by date desc
''')

stocks = database.read_from_db('''
select value, name from depot_data
''')

overview = database.read_from_db('''
select 'Stocks' as "Asset", sum(value) as "Value"
from depot_data
union all
select 'Cash' as "Asset",
       ROUND((select amount from sparkasse_balance order by date(date) desc limit 1) +
             (select amount from dkb_balance order by date(date) desc limit 1) +
             (select amount from credit_card_balance order by date(date) desc limit 1)) as "Cash value"
union all
select '' as "Asset",
       ROUND((select amount from sparkasse_balance order by date(date) desc limit 1) +
             (select amount from dkb_balance order by date(date) desc limit 1) +
             (select amount from credit_card_balance order by date(date) desc limit 1))+
             (select sum(value) as "Value" from depot_data)
''')

in_out.date_trunc = in_out.date_trunc.apply(lambda x: x.date())

app = dash.Dash()
colors = {
    'background': 'rgba(0,0,0,0)',
    'text': 'rgba(1,1,1,1)',
    'in_out_color': ['rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,255,0)', 'rgb(0,255,255)',
                     'rgb(255,0,125)', 'rgb(0,255,125)', 'rgb(125,125,125)']
}
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.H1(
        children='Finance Overview',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    dash_table.DataTable(
        id='stock_table',
        columns=[{"name": i, "id": i} for i in overview.columns],
        data=overview.to_dict('rows'),
        style_table={
        'maxWidth': '500px',
        'overflowY': 'scroll',
        'border': 'thin lightgrey solid'
        },
        style_data_conditional=[{
        "if": {"row_index": 2},
        "fontWeight": "bold"
        }]
    ),

    html.Div([
        html.Div([
            dcc.Graph(
                id='Graph1',
                figure={
                    'data': [
                        {'x': ['Assets'], 'y': [sparkasse_balance.amount[0]], 'type': 'bar', 'name': 'Sparkasse'},
                        {'x': ['Assets'], 'y': [dkb_balance.amount[0]], 'type': 'bar', 'name': u'DKB'},
                        {'x': ['Assets'], 'y': [cc_balance.amount[0]], 'type': 'bar', 'name': u'CC'},
                        {'x': ['Assets'], 'y': [depot_balance.amount[0]], 'type': 'bar', 'name': u'Depot'}
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

    dcc.DatePickerRange(
        id="date-picker-in_out",
        start_date=datetime.datetime(2018, 5, 22),
        end_date=datetime.date.today(),
        min_date_allowed=datetime.datetime(2018, 5, 22),
        max_date_allowed=datetime.datetime.now(),
        end_date_placeholder_text="Select a date"
    ),

    dcc.Graph(id="in-out-graph"),

    dcc.DatePickerRange(
        id="date-picker-range",
        start_date=datetime.datetime(2018, 5, 22),
        end_date=datetime.date.today(),
        min_date_allowed=datetime.datetime(2018, 5, 22),
        max_date_allowed=datetime.datetime.now(),
        end_date_placeholder_text="Select a date"
    ),

    dash_table_experiments.DataTable(
        rows=[{}],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='table'),

])


@app.callback(
    Output("table", "rows"),
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date")]
)
def update_table(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    transactions_filtered = transactions[(transactions['date'] > start_date) & (transactions['date'] < end_date)]

    return transactions_filtered.to_dict('records')


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
    app.run_server(debug=True)
