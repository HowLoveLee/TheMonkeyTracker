import threading

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table, Input, Output

app = dash.Dash(__name__)


def viewStats(self):
    data = self.getCommittedExpenseData()
    launch_view(data, self.getDetailedExpensesForType)
    self.dash_thread = threading.Thread(target=app.run_server, kwargs={'debug': True, 'use_reloader': False})
    self.dash_thread.start()

    def run_dash():
        app.run_server(debug=True, use_reloader=False)  # Ensure use_reloader is set to False

    # Run the Dash app in a separate thread
    threading.Thread(target=run_dash).start()


def closeEvent(self, event):
    # Terminate the Dash thread when the PyQt app is closed
    if hasattr(self, 'dash_thread'):
        self.dash_thread.join(timeout=1)  # You can adjust the timeout as needed
    event.accept()


def launch_view(data_dict, detailed_expense_fetcher):
    # Convert the data dictionary to a Pandas DataFrame
    df = pd.DataFrame(list(data_dict.items()), columns=['Type', 'Amount'])

    # Create the pie chart
    fig = px.pie(data_frame=df, names='Type', values='Amount')

    app.layout = html.Div([
        dcc.Graph(id='pie-chart', figure=fig),
        dash_table.DataTable(id='table')
    ])

    @app.callback(
        Output('table', 'data'),
        Output('table', 'columns'),
        [Input('pie-chart', 'clickData')]
    )
    def update_table(clickData):
        if clickData:
            # Get the name of the type that was clicked on
            selected_type = clickData['points'][0]['label']

            # Fetch expenses for the selected type
            expenses = get_expenses_for_type(selected_type)

            return expenses, [{"name": i, "id": i} for i in expenses[0].keys()]
        return [], []

    # Placeholder function
    def get_expenses_for_type(expense_type):
        return detailed_expense_fetcher(expense_type)
