"""
Plotly Charts - Plotly 图表

Provides interactive visualizations for:
- Population dynamics
- Class distribution
- Value form topology
- Crisis indicators
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List


class PlotlyCharts:
    """
    Plotly 图表 - Interactive chart generation.
    """

    @staticmethod
    def plot_population_dynamics(history: List[Dict]) -> go.Figure:
        """绘制人口动态"""
        steps = [h['step'] for h in history]
        population = [h['total_population'] for h in history]
        subsistence = [h['average_subsistence'] for h in history]

        fig = make_subplots(rows=2, cols=1, subplot_titles=('人口', '生活资料满足率'))

        fig.add_trace(
            go.Scatter(x=steps, y=population, mode='lines', name='人口'),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=steps, y=subsistence, mode='lines', name='满足率'),
            row=2, col=1
        )

        fig.update_layout(title='人口动态变化', height=600)
        return fig

    @staticmethod
    def plot_class_distribution(history: List[Dict]) -> go.Figure:
        """绘制阶级分布"""
        if not history:
            return go.Figure()

        latest = history[-1]
        class_dist = latest.get('class_distribution', {})

        if not class_dist:
            return go.Figure()

        # Filter non-zero classes
        non_zero = {k: v for k, v in class_dist.items() if v > 0}

        fig = go.Figure(data=[
            go.Bar(x=list(non_zero.keys()), y=list(non_zero.values()))
        ])

        fig.update_layout(title='当前阶级分布')
        return fig

    @staticmethod
    def plot_crisis_indicators(crisis_data: Dict) -> go.Figure:
        """绘制危机指标"""
        indicators = ['rate_of_surplus_value', 'organic_composition', 'profit_rate', 'department_imbalance']
        values = [crisis_data.get(ind, 0.0) for ind in indicators]

        fig = go.Figure(data=[
            go.Bar(x=indicators, y=values)
        ])

        fig.update_layout(title='危机指标')
        return fig

    @staticmethod
    def plot_value_form_evolution(snlt_history: Dict[str, List[float]]) -> go.Figure:
        """绘制价值形式演变"""
        fig = go.Figure()

        for commodity, snlt_values in snlt_history.items():
            fig.add_trace(
                go.Scatter(y=snlt_values, mode='lines', name=commodity)
            )

        fig.update_layout(title='SNLT 演变 (价值形式)', height=400)
        return fig

    @staticmethod
    def plot_reproduction_schema(schema_data: Dict) -> go.Figure:
        """绘制再生产图式"""
        departments = ['Department I\n(c)', 'Department I\n(v)', 'Department I\n(s)',
                       'Department II\n(c)', 'Department II\n(v)', 'Department II\n(s)']
        values = [
            schema_data.get('i_c', 0),
            schema_data.get('i_v', 0),
            schema_data.get('i_s', 0),
            schema_data.get('ii_c', 0),
            schema_data.get('ii_v', 0),
            schema_data.get('ii_s', 0),
        ]

        fig = go.Figure(data=[
            go.Bar(x=departments, y=values, marker_color=['red']*3 + ['blue']*3)
        ])

        fig.update_layout(title='再生产图式')
        return fig

    @staticmethod
    def create_dashboard(history: List[Dict], crisis_data: Dict = None) -> go.Figure:
        """创建综合仪表板"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('人口变化', '阶级分布', '生活资料满足率', '社会关系', '危机指标', 'SNLT演变'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )

        # Population
        steps = [h['step'] for h in history]
        pop = [h['total_population'] for h in history]
        fig.add_trace(go.Scatter(x=steps, y=pop, mode='lines', name='人口'), row=1, col=1)

        # Class distribution
        if history:
            latest = history[-1]
            class_dist = latest.get('class_distribution', {})
            non_zero = {k: v for k, v in class_dist.items() if v > 0}
            if non_zero:
                fig.add_trace(go.Bar(x=list(non_zero.keys()), y=list(non_zero.values()), name='阶级'), row=1, col=2)

        # Subsistence
        subs = [h['average_subsistence'] for h in history]
        fig.add_trace(go.Scatter(x=steps, y=subs, mode='lines', name='满足率'), row=2, col=1)

        # Social relations
        if history:
            relations = history[-1].get('total_relations', 0)
            fig.add_trace(go.Bar(x=['关系数'], y=[relations], name='社会关系'), row=2, col=2)

        # Crisis indicators
        if crisis_data:
            indicators = list(crisis_data.keys())
            values = list(crisis_data.values())
            fig.add_trace(go.Bar(x=indicators, y=values, name='危机'), row=3, col=1)

        fig.update_layout(height=900, showlegend=False, title_text='CapitalSimulator 仪表板')
        return fig