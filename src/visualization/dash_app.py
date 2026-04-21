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
    - Political/cultural state panel
    """

    def __init__(self, model=None):
        self.app = Dash(__name__)
        self.model = model
        self.data_collector = None
        self.social_panel = None

        self._setup_layout()

    def set_model(self, model):
        """设置模型"""
        self.model = model
        if model and hasattr(model, 'data_collector'):
            self.data_collector = model.data_collector

    def set_social_panel(self, social_panel):
        """设置社会面板组件"""
        self.social_panel = social_panel

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

            dcc.Tabs(id='tabs', value='population_tab', children=[
                dcc.Tab(label='人口动态', value='population_tab', children=[
                    dcc.Graph(id='population-chart'),
                ]),
                dcc.Tab(label='阶级分布', value='class_tab', children=[
                    dcc.Graph(id='class-chart'),
                ]),
                dcc.Tab(label='社会关系', value='relation_tab', children=[
                    dcc.Graph(id='relation-chart'),
                ]),
                dcc.Tab(label='政治文化', value='political_tab', children=[
                    html.Div(id='political-cultural-panel', style={'padding': '20px'}),
                ]),
            ]),

            html.Div(id='metrics-display'),

            dcc.Interval(
                id='interval-component',
                interval=1*1000,
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

        @self.app.callback(
            Output('relation-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_relation_chart(n):
            if self.model and hasattr(self.model, 'data_collector'):
                history = self.model.data_collector.get_history()
                if history:
                    latest = history[-1]
                    edge_counts = {k: v for k, v in latest.items()
                                   if k not in ['step', 'total_population', 'average_subsistence',
                                                'class_distribution', 'social_stage',
                                                'transition_indicators', 'economic_metrics',
                                                'total_agents', 'total_relations', 'graph_density']
                                   and isinstance(v, (int, float)) and v > 0}
                    if edge_counts:
                        return {'data': [{'x': list(edge_counts.keys()), 'y': list(edge_counts.values()), 'type': 'bar'}],
                                'layout': {'title': '社会关系分布'}}
            return {'data': [], 'layout': {'title': '社会关系分布'}}

        @self.app.callback(
            Output('political-cultural-panel', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_political_panel(n):
            if self.social_panel:
                panel_data = self.social_panel.render_panel()
                political = panel_data['political_state']
                cultural = panel_data['cultural_state']
                warnings = panel_data['crisis_warnings']

                # 警告样式
                warning_style = {'color': 'red', 'fontWeight': 'bold', 'padding': '10px',
                                 'backgroundColor': '#ffeeee', 'border': '1px solid red'}
                normal_style = {'padding': '10px'}

                children = [
                    html.H3("政治状态"),
                    html.P(f"政体类型: {political['regime_type']}"),
                    html.P(f"参政水平: {political['suffrage_level']*100:.0f}%"),
                    html.P(f"税率: {political['tax_rate']*100:.0f}%"),
                    html.P(f"镇压水平: {political['repression_level']*100:.0f}%"),
                    html.P(f"财产权保护: {political['property_rights']*100:.0f}%"),

                    html.H3("文化状态"),
                    html.P(f"霸权强度: {cultural['hegemony_strength']*100:.0f}%"),
                    html.P(f"合法性: {cultural['legitimacy']*100:.0f}%"),
                    html.P(f"平均阶级意识: {cultural['avg_class_consciousness']*100:.0f}%"),
                    html.P(f"意识形态: {cultural['ideology_content']}"),
                ]

                # 添加警告
                if warnings:
                    children.append(html.H4("危机警告", style={'color': 'red'}))
                    for warning in warnings:
                        children.append(html.P(warning, style={'color': 'red'}))

                # 合法性警告（红色预警）
                if cultural['legitimacy'] < 0.3:
                    children.insert(0, html.Div(
                        "【红色预警】合法性低于30%，统治正当性严重不足！",
                        style={'color': 'white', 'backgroundColor': 'red', 'padding': '15px',
                               'fontWeight': 'bold', 'textAlign': 'center'}
                    ))

                return children

            return html.P("社会面板未初始化")

    def run(self, debug: bool = False, port: int = 8050):
        """运行应用"""
        self.app.run(debug=debug, port=port)