"""
Dash App - Dash 应用

Web-based interactive visualization and control panel.
"""

from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from typing import List, Dict


class DashApp:
    """
    Dash 应用 - Interactive web visualization.

    Provides:
    - Real-time simulation visualization
    - Parameter controls
    - Historical data exploration
    """

    def __init__(self, model=None):
        self.app = Dash(__name__)
        self.model = model
        self.data_collector = None

        self._setup_layout()

    def _setup_layout(self):
        """设置布局"""
        self.app.layout = html.Div([
            html.H1("CapitalSimulator - 历史唯物主义经济模拟"),

            html.Div([
                html.H2("控制面板"),
                html.Label("模拟步数:"),
                dcc.Input(id='steps-input', type='number', value=100),
                html.Button('运行模拟', id='run-button', n_clicks=0),
                html.Button('重置', id='reset-button', n_clicks=0),
            ], style={'padding': '20px', 'border': '1px solid #ccc'}),

            html.Div([
                html.H2("人口动态"),
                dcc.Graph(id='population-chart'),
            ], style={'padding': '20px'}),

            html.Div([
                html.H2("阶级分布"),
                dcc.Graph(id='class-chart'),
            ], style={'padding': '20px'}),

            html.Div([
                html.H2("危机指标"),
                dcc.Graph(id='crisis-chart'),
            ], style={'padding': '20px'}),

            html.Div(id='metrics-display'),

            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # Update every second
                n_intervals=0
            )
        ])

        self._setup_callbacks()

    def _setup_callbacks(self):
        """设置回调"""
        @self.app.callback(
            Output('population-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_population_chart(n):
            if self.model and hasattr(self.model, 'data_collector'):
                history = self.model.data_collector.get_history()
                if history:
                    steps = [h['step'] for h in history]
                    pop = [h['total_population'] for h in history]
                    return {'data': [{'x': steps, 'y': pop, 'type': 'scatter', 'mode': 'lines'}],
                            'layout': {'title': '人口'}}
            return {'data': [], 'layout': {'title': '人口'}}

        @self.app.callback(
            Output('class-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_class_chart(n):
            if self.model and hasattr(self.model, 'data_collector'):
                history = self.model.data_collector.get_history()
                if history:
                    latest = history[-1]
                    class_dist = latest.get('class_distribution', {})
                    non_zero = {k: v for k, v in class_dist.items() if v > 0}
                    if non_zero:
                        return {'data': [{'x': list(non_zero.keys()), 'y': list(non_zero.values()), 'type': 'bar'}],
                                'layout': {'title': '阶级分布'}}
            return {'data': [], 'layout': {'title': '阶级分布'}}

    def run(self, debug: bool = False, port: int = 8050):
        """运行应用"""
        self.app.run(debug=debug, port=port)