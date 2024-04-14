from dash import Dash, html, dash_table
import pandas as pd

df = pd.read_csv('aqi_data.csv')

app = Dash(__name__)

app.layout = html.Div([
    html.Div(children='uh'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=1000)
])

if __name__ == '__main__':
    app.run(debug=True)