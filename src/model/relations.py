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
    """关系边类型 - Types of social relation edges

    Based on Service-Fried anthropological framework (塞维斯-弗里德框架).
    """
    # 原始社会关系
    KINSHIP = "kinship"                      # 血缘关系 - 游群起
    CLAN = "clan"                           # 氏族关系 - 部落起
    BARTER = "barter"                       # 物物交换 - 部落起

    # 过渡阶段关系
    TRIBUTARY = "tributary"                 # 贡赋关系 - 酋邦起
    MILITARY_SERVICE = "military_service"   # 兵役 - 早期国家起
    RESIDENCE = "residence"                 # 地缘关系 - 早期国家起

    # 阶级社会关系
    ENSLAVEMENT = "enslavement"              # 奴役关系 - 部落联盟晚期起
    FEUDAL_RENT = "feudal_rent"            # 封建地租 - 封建社会
    WAGE_CONTRACT = "wage_contract"         # 雇佣关系 - 资本主义

    # 教育与发展
    TRAINING = "training"                   # 培训关系 - 封建社会起

    # 殖民与帝国主义
    COLONIAL_EXTRACTION = "colonial_extraction"  # 殖民榨取 - 资本主义

    # 社会主义
    PLANNING = "planning"                  # 计划分配 - 社会主义


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
        - KINSHIP: 血缘关系 (游群起)
        - CLAN: 氏族关系 (部落起)
        - BARTER: 物物交换 (部落起)
        - TRIBUTARY: 贡赋关系 (酋邦起)
        - MILITARY_SERVICE: 兵役 (早期国家起)
        - RESIDENCE: 地缘关系 (早期国家起)
        - ENSLAVEMENT: 奴役关系 (部落联盟晚期起)
        - FEUDAL_RENT: 封建地租 (封建社会)
        - WAGE_CONTRACT: 雇佣关系 (资本主义)
        - TRAINING: 培训关系 (封建社会起)
        - COLONIAL_EXTRACTION: 殖民榨取 (资本主义)
        - PLANNING: 计划分配 (社会主义)
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
        Class position is determined by the dominant relation edge type.

        Edge type priority: WAGE_CONTRACT > FEUDAL_RENT > ENSLAVEMENT >
                            COLONIAL_EXTRACTION > TRIBUTARY > RESIDENCE >
                            MILITARY_SERVICE > CLAN > KINSHIP
        """
        relations = self.get_relations(agent_id)

        # 资本主义社会关系 (最高优先级)
        if RelationTypes.WAGE_CONTRACT.value in relations:
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.WAGE_CONTRACT.value):
                return "worker"
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.WAGE_CONTRACT.value):
                return "capitalist"

        # 封建社会关系
        if RelationTypes.FEUDAL_RENT.value in relations:
            # serf -> lord (serf pays rent to lord)
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.FEUDAL_RENT.value):
                return "serf"
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.FEUDAL_RENT.value):
                return "lord"

        # 奴隶社会关系
        if RelationTypes.ENSLAVEMENT.value in relations:
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.ENSLAVEMENT.value):
                return "slave_owner"
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.ENSLAVEMENT.value):
                return "slave"

        # 殖民榨取关系
        if RelationTypes.COLONIAL_EXTRACTION.value in relations:
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.COLONIAL_EXTRACTION.value):
                return "colonized"
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.COLONIAL_EXTRACTION.value):
                return "colonizer"

        # 酋邦/早期国家关系
        if RelationTypes.TRIBUTARY.value in relations:
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.TRIBUTARY.value):
                return "chief"
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.TRIBUTARY.value):
                return "commoner"

        if RelationTypes.RESIDENCE.value in relations:
            return "citizen"

        if RelationTypes.MILITARY_SERVICE.value in relations:
            return "warrior"

        # 培训关系
        if RelationTypes.TRAINING.value in relations:
            if self._has_incoming_edge_of_type(agent_id, RelationTypes.TRAINING.value):
                return "apprentice"
            if self._has_outgoing_edge_of_type(agent_id, RelationTypes.TRAINING.value):
                return "trainer"

        # 社会主义计划关系
        if RelationTypes.PLANNING.value in relations:
            return "comrade"

        # 部落社会关系
        if RelationTypes.CLAN.value in relations:
            return "tribesman"

        if RelationTypes.KINSHIP.value in relations:
            return "band_member"

        # 无关系
        return "primitive_forager"

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
