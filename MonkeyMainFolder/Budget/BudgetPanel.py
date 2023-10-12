from random import random

import matplotlib
from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6 import QtWidgets
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates

matplotlib.use('QtAgg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class BudgetPanel(QtWidgets.QWidget):
    def __init__(self):
        def ordinal(n):
            if 10 <= n % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
            return f"{n}{suffix}"

        super().__init__()

        # Placeholder widget for the Net Worth chart
        netWorthChart = QtWidgets.QWidget()
        netWorthChart.setStyleSheet("background-color: red;")  # Temp color to visualize space

        # Expense data
        data = {
            'Date': [
                "8/1/2023", "8/2/2023", "8/3/2023", "8/4/2023", "8/5/2023",
                "8/6/2023", "8/7/2023", "8/8/2023", "8/9/2023", "8/10/2023",
                "8/11/2023", "8/12/2023", "8/13/2023", "8/14/2023", "8/15/2023",
                "8/16/2023", "8/17/2023", "8/18/2023", "8/19/2023", "8/20/2023",
                "8/21/2023", "8/22/2023", "8/23/2023", "8/24/2023", "8/25/2023",
                "8/26/2023", "8/27/2023", "8/28/2023", "8/29/2023", "8/30/2023",
                "8/31/2023", "9/1/2023", "9/2/2023", "9/3/2023", "9/4/2023",
                "9/5/2023", "9/6/2023", "9/7/2023", "9/8/2023", "9/9/2023",
                "9/10/2023", "9/11/2023", "9/12/2023", "9/13/2023", "9/14/2023",
                "9/15/2023", "9/16/2023", "9/17/2023", "9/18/2023", "9/19/2023",
            ],
            'Amount': [
                3.14, 5.32, 10.12, 20.73, 41.85,
                81.21, 150.56, 250.91, 400.27, 600.68,
                800.00, 600.68, 400.27, 250.91, 150.56,
                81.21, 41.85, 20.73, 10.12, 5.32,
                3.14, 5.32, 10.12, 20.73, 41.85,
                81.21, 150.56, 250.91, 400.27, 600.68,
                800.00, 600.68, 400.27, 250.91, 150.56,
                81.21, 41.85, 20.73, 10.12, 5.32,
                81.21, 41.85, 20.73, 10.12, 5.32,
                81.21, 41.85, 20.73, 10.12, 5.32

            ]
        }

        # Randomly shuffle the 'Amount' values between the defined range
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date')

        # Seaborn plot
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sns.lineplot(data=df, x="Date", y="Amount", ax=sc.axes, marker="o")

        def customDateFormat(x, _=None):
            date = mdates.num2date(x).date()
            return date.strftime(f'{ordinal(date.day)} %b')

        sc.axes.xaxis.set_major_formatter(customDateFormat)
        sc.figure.autofmt_xdate()

        # Navigation toolbar
        toolbar = NavigationToolbar(sc, self)

        # Organize chart layouts with equal stretch factors
        chartLayout = QtWidgets.QHBoxLayout()
        chartLayout.addWidget(sc, 1)  # 50% width
        chartLayout.addWidget(sc, 1)  # 50% width

        # Ensure charts and buttons each take up half the height of the panel
        chartLayout.setContentsMargins(0, 0, 0, 0)
        chartLayout.setSpacing(0)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(chartLayout)

        # Layout for the buttons with size policy adjustments
        buttonLayout = QtWidgets.QHBoxLayout()

        conditionalStatementsBtn = QPushButton("Conditional Statements")
        conditionalStatementsBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        budgetingGoalsBtn = QPushButton("Budgeting Goals")
        budgetingGoalsBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        debtManagementBtn = QPushButton("Debt Management")
        debtManagementBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        buttonLayout.addWidget(conditionalStatementsBtn)
        buttonLayout.addWidget(budgetingGoalsBtn)
        buttonLayout.addWidget(debtManagementBtn)

        # mainLayout.addWidget(toolbar)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
