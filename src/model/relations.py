"""
SocialRelationGraph - 社会关系图构建器

Uses NetworkX to construct social relation graphs where:
- Nodes are Human agents
- Edges are relation types (Kinship, Barter, Enslavement, FeudalRent, WageContract, Planning)
- Class position is dynamically inferred from edge types
"""

import networkx as nx
from enum import Enum
from typing import Dict, Set, Optional


class RelationTypes(Enum):
    """关系边类型 - Types of social relation edges"""
    KINSHIP = "kinship"
    BARTER = "barter"
    ENSLAVEMENT = "enslavement"
    FEUDAL_RENT = "feudal_rent"
    WAGE_CONTRACT = "wage_contract"
    PLANNING = "planning"


class SocialRelationGraph:
    """
    社会关系图 - Graph of social relations.

    The graph structure DETERMINES agent behavior.
    No "greed" or "utility maximization" - only structural relations.
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._edge_types_count: Dict[str, int] = {}

    def add_agent(self, agent_id: int):
        """添加Agent到图中"""
        self.graph.add_node(agent_id)

    def add_edge(self, source_id: int, target_id: int,
                 relation_type: RelationTypes,
                 weight: float = 1.0,
                 metadata: Dict = None):
        """
        添加关系边 - Add a social relation edge.

        The TYPE of edge determines the production relation:
        - KINSHIP: Primitive communal society
        - BARTER: Early exchange before money
        - ENSLAVEMENT: Slave society (output extracted)
        - FEUDAL_RENT: Feudal society (rent extracted)
        - WAGE_CONTRACT: Capitalist society (surplus-value extracted)
        - PLANNING: Socialist society (planned allocation)
        """
        edge_data = {
            'relation_type': relation_type.value,
            'weight': weight,
            **(metadata or {})
        }
        self.graph.add_edge(source_id, target_id, **edge_data)
        self._update_edge_count(relation_type.value)

    def _update_edge_count(self, relation_type: str):
        """更新边类型计数"""
        self._edge_types_count[relation_type] = \
            self._edge_types_count.get(relation_type, 0) + 1

    def get_relations(self, agent_id: int) -> Set[str]:
        """
        获取某Agent的所有关系类型 - Get all relation types for an agent.
        Class position is inferred from the TYPES of edges connected to this agent.
        """
        if agent_id not in self.graph:
            return set()

        relations = set()
        # In-edges (relations WHERE this agent is the target)
        for u, k, data in self.graph.in_edges(agent_id, data=True):
            relations.add(data.get('relation_type', 'unknown'))
        # Out-edges (relations WHERE this agent is the source)
        for u, k, data in self.graph.out_edges(agent_id, data=True):
            relations.add(data.get('relation_type', 'unknown'))
        return relations

    def infer_class_position(self, agent_id: int) -> str:
        """
        从关系边推断阶级位置 - Infer class position from edge types.

        This is a STRUCTURAL determination, not a behavioral one.
        """
        relations = self.get_relations(agent_id)

        if RelationTypes.WAGE_CONTRACT.value in relations:
            # Has wage contract edge - Capitalist (extracts surplus-value)
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.WAGE_CONTRACT.value):
                return "capitalist"
            # Has wage contract edge - Worker (has labor-power to sell)
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.WAGE_CONTRACT.value):
                return "worker"
        if RelationTypes.ENSLAVEMENT.value in relations:
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.ENSLAVEMENT.value):
                return "slave_owner"
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.ENSLAVEMENT.value):
                return "slave"
        if RelationTypes.FEUDAL_RENT.value in relations:
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.FEUDAL_RENT.value):
                return "lord"
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.FEUDAL_RENT.value):
                return "serf"
        if RelationTypes.KINSHIP.value in relations:
            return "tribe_member"
        return "forager"

    def _has_outgoing_edge_of_type(self, agent_id: int, edge_type: str) -> bool:
        """检查是否有指定类型的出边"""
        for _, _, data in self.graph.out_edges(agent_id, data=True):
            if data.get('relation_type') == edge_type:
                return True
        return False

    def _has_incoming_edge_of_type(self, agent_id: int, edge_type: str) -> bool:
        """检查是否有指定类型的入边"""
        for _, _, data in self.graph.in_edges(agent_id, data=True):
            if data.get('relation_type') == edge_type:
                return True
        return False

    def get_edge_count_by_type(self) -> Dict[str, int]:
        """获取各类型边的数量"""
        return self._edge_types_count.copy()

    def calculate_graph_metrics(self) -> Dict:
        """计算图论指标 - For data collection"""
        if len(self.graph.nodes) == 0:
            return {}

        metrics = {
            'total_agents': self.graph.number_of_nodes(),
            'total_relations': self.graph.number_of_edges(),
            'graph_density': nx.density(self.graph),
        }

        # Add edge type counts
        metrics.update(self._edge_types_count)

        return metrics

    def remove_agent(self, agent_id: int):
        """移除Agent及其所有边"""
        self.graph.remove_node(agent_id)
