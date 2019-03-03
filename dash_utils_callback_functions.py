import plotly.graph_objs as go
import datetime


def call_back_dropdown_multiline_graph(df, name_col_distinguish, name_col_x, name_col_y):
    def plot_time_series(dropdown_value):
        data = []
        for x in dropdown_value:
            trace = go.Scatter(
                x=df[df[name_col_distinguish] == x][name_col_x],
                y=df[df[name_col_distinguish] == x][name_col_y],
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


def call_back_datepicker_tablbe(df, name_col_date):
    def update_table(start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        transactions_filtered = df[(df[name_col_date] > start_date) & (df[name_col_date] < end_date)]

        return transactions_filtered.to_dict('records')

    return update_table
