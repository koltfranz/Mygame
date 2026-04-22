"""
Snapshot - 快照生成与图结构序列化

用于保存和恢复模拟状态，生成诊断报告。
"""

import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class Snapshot:
    """
    快照类 - 保存模拟状态的完整快照

    包含：
    - 模型状态（时间、阶段、人口）
    - Agent 数据
    - 社会关系图结构
    - 经济指标
    - 政治文化状态
    """

    def __init__(self, model, step: int):
        self.timestamp = datetime.now()
        self.step = step
        self.model_state: Dict[str, Any] = {}
        self.agents_data: list = []
        self.graph_data: Dict[str, Any] = {}
        self.economic_metrics: Dict[str, float] = {}
        self.political_metrics: Dict[str, Any] = {}
        self.cultural_metrics: Dict[str, Any] = {}

    def capture(self, model) -> 'Snapshot':
        """捕获当前模型状态"""
        self.step = int(model.time)
        self.model_state = {
            'social_stage': model.social_stage.value,
            'total_population': model.get_population_count(),
            'average_subsistence': model.get_average_subsistence(),
        }

        # 捕获 Agent 数据
        self.agents_data = []
        for agent in model._agent_lookup.values():
            agent_data = {
                'unique_id': agent.unique_id,
                'class_position': model.social_graph.infer_class_position(agent.unique_id),
                'subsistence_satisfaction': getattr(agent, 'subsistence_satisfaction', 0),
                'labor_power_capacity': getattr(agent, 'labor_power_capacity', 0),
                'skill_level': getattr(agent, 'skill_level', 0),
                'commodity_inventory_size': len(getattr(agent, 'commodity_inventory', [])),
            }

            # 特定类型的数据
            if hasattr(agent, 'capital_stock'):
                agent_data['capital_stock'] = agent.capital_stock
            if hasattr(agent, 'workers_employed'):
                agent_data['workers_employed'] = len(agent.workers_employed)
            if hasattr(agent, 'serfs_controlled'):
                agent_data['serfs_controlled'] = len(agent.serfs_controlled)
            if hasattr(agent, 'slaves_owned'):
                agent_data['slaves_owned'] = len(agent.slaves_owned)

            self.agents_data.append(agent_data)

        # 捕获图结构
        self.graph_data = {
            'num_nodes': model.social_graph.graph.number_of_nodes(),
            'num_edges': model.social_graph.graph.number_of_edges(),
            'edge_counts': model.social_graph.get_edge_count_by_type(),
        }

        # 捕获经济指标
        latest_data = model.data_collector.get_latest()
        self.economic_metrics = latest_data.get('economic_metrics', {})

        # 捕获政治指标
        self.political_metrics = latest_data.get('political_indicators', {})

        # 捕获文化指标
        self.cultural_metrics = latest_data.get('cultural_indicators', {})

        return self

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于 JSON 序列化）"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'step': self.step,
            'model_state': self.model_state,
            'num_agents': len(self.agents_data),
            'graph_data': self.graph_data,
            'economic_metrics': self.economic_metrics,
            'political_metrics': self.political_metrics,
            'cultural_metrics': self.cultural_metrics,
        }

    def to_json(self, filepath: Optional[str] = None) -> str:
        """导出为 JSON 格式"""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if filepath:
            Path(filepath).write_text(json_str, encoding='utf-8')

        return json_str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Snapshot':
        """从字典加载"""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.timestamp = datetime.fromisoformat(data['timestamp'])
        snapshot.step = data['step']
        snapshot.model_state = data['model_state']
        snapshot.agents_data = []
        snapshot.graph_data = data['graph_data']
        snapshot.economic_metrics = data['economic_metrics']
        snapshot.political_metrics = data['political_metrics']
        snapshot.cultural_metrics = data['cultural_metrics']
        return snapshot


class SnapshotManager:
    """
    快照管理器 - 管理多个快照，用于生成诊断报告
    """

    def __init__(self, max_snapshots: int = 100):
        self.snapshots: list = []
        self.max_snapshots = max_snapshots
        self.snapshot_interval = 50  # 每50步自动保存一次

    def add_snapshot(self, snapshot: Snapshot):
        """添加快照"""
        self.snapshots.append(snapshot)

        # 保持最大数量限制
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)

    def get_latest(self) -> Optional[Snapshot]:
        """获取最新快照"""
        return self.snapshots[-1] if self.snapshots else None

    def get_by_step(self, step: int) -> Optional[Snapshot]:
        """根据步数获取快照"""
        for snap in reversed(self.snapshots):
            if snap.step == step:
                return snap
        return None

    def generate_diagnostic_report(self, model) -> str:
        """生成诊断报告"""
        latest = self.get_latest()
        if not latest:
            return "没有可用的快照数据"

        latest.capture(model)

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("                    诊断报告")
        report_lines.append("=" * 80)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"当前步数: {latest.step}")

        # 社会阶段
        stage_names = {
            "primitive_horde": "原始群",
            "band": "游群",
            "tribe": "部落",
            "tribal_confederacy": "部落联盟",
            "chiefdom": "酋邦",
            "early_state": "早期国家",
            "slavery_state": "奴隶社会",
            "feudal_state": "封建社会",
            "capitalist_state": "资本主义",
            "socialist_state": "社会主义",
        }
        stage_name = stage_names.get(latest.model_state['social_stage'], latest.model_state['social_stage'])
        report_lines.append(f"\n【社会阶段】{stage_name}")

        # 人口
        report_lines.append(f"\n【人口指标】")
        report_lines.append(f"  总人口: {latest.model_state['total_population']}")
        report_lines.append(f"  平均生存资料满足率: {latest.model_state['average_subsistence']:.2%}")

        # 经济指标
        report_lines.append(f"\n【经济指标】")
        econ = latest.economic_metrics
        report_lines.append(f"  利润率: {econ.get('profit_rate', 0):.4f}")
        report_lines.append(f"  剩余价值率: {econ.get('rate_of_surplus_value', 0):.4f}")
        report_lines.append(f"  资本有机构成: {econ.get('organic_composition', 0):.4f}")
        report_lines.append(f"  部类偏离度: {econ.get('department_imbalance', 0):.4f}")

        # 政治指标
        report_lines.append(f"\n【政治指标】")
        pol = latest.political_metrics
        report_lines.append(f"  政体类型: {pol.get('regime_type', 'unknown')}")
        report_lines.append(f"  国家镇压能力: {pol.get('state_repression_capacity', 0):.2%}")
        report_lines.append(f"  财政汲取能力: {pol.get('fiscal_capacity', 0):.2%}")

        # 文化指标
        report_lines.append(f"\n【文化指标】")
        cul = latest.cultural_metrics
        report_lines.append(f"  合法性: {cul.get('legitimacy', 0):.2%}")
        report_lines.append(f"  文化霸权: {cul.get('hegemony_strength', 0):.2%}")
        report_lines.append(f"  阶级意识: {cul.get('avg_class_consciousness', 0):.2%}")

        # 危机预警
        report_lines.append(f"\n【危机预警】")
        if econ.get('profit_rate', 0) < 0.05:
            report_lines.append("  [CRITICAL] 利润率极低，资本主义危机迫在眉睫")
        elif econ.get('profit_rate', 0) < 0.1:
            report_lines.append("  [WARNING] 利润率偏低")

        if cul.get('legitimacy', 1) < 0.3:
            report_lines.append("  [CRITICAL] 合法性危机！")
        elif cul.get('legitimacy', 1) < 0.5:
            report_lines.append("  [CAUTION] 合法性下降")

        # 阶段演进历史
        if len(self.snapshots) > 1:
            report_lines.append(f"\n【阶段演进历史】")
            stages_seen = []
            for snap in self.snapshots:
                stage = snap.model_state['social_stage']
                if stage not in stages_seen:
                    stages_seen.append(stage)
                    cn_stage = stage_names.get(stage, stage)
                    report_lines.append(f"  Step {snap.step}: {cn_stage}")

        report_lines.append("\n" + "=" * 80)

        return "\n".join(report_lines)

    def save_report(self, model, filepath: str = "diagnostic_report.txt"):
        """保存诊断报告到文件"""
        report = self.generate_diagnostic_report(model)
        Path(filepath).write_text(report, encoding='utf-8')
        return filepath

    def export_all_snapshots(self, directory: str = "snapshots"):
        """导出所有快照到指定目录"""
        import os
        os.makedirs(directory, exist_ok=True)

        for i, snap in enumerate(self.snapshots):
            filepath = os.path.join(directory, f"snapshot_{i:04d}_step_{snap.step}.json")
            snap.to_json(filepath)

        return directory
