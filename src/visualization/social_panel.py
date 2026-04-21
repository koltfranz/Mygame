"""
SocialPanel - 政治文化状态面板

Displays political and cultural state indicators for the simulation.
Shows legitimacy warnings when < 0.3 (30%).
"""

from typing import Dict, List


class SocialPanel:
    """
    政治文化状态面板 - Displays political and cultural state.

    Integrates with:
    - PoliticalRegime (政治体制)
    - IdeologyManager (意识形态管理器)
    - SocialStage (社会阶段)

    Generates natural language descriptions of the current state.
    """

    def __init__(self, model=None):
        self.model = model
        self._political_regime = None
        self._ideology_manager = None

    def set_components(self, political_regime, ideology_manager):
        """设置政治和意识形态组件"""
        self._political_regime = political_regime
        self._ideology_manager = ideology_manager

    def get_political_state(self) -> Dict:
        """
        获取政治状态 - Get political state indicators.

        Returns dict with:
        - regime_type: 政体类型
        - suffrage_level: 参政水平
        - tax_rate: 税率
        - repression_level: 镇压水平
        - property_rights: 财产权保护
        """
        if not self._political_regime:
            return self._default_political_state()

        effects = self._political_regime.apply_regime_effects(self.model)

        return {
            'regime_type': self._political_regime.regime_type,
            'suffrage_level': self._political_regime.suffrage_level,
            'tax_rate': effects.get('tax_rate', 0.0),
            'repression_level': effects.get('repression_level', 0.0),
            'property_rights': effects.get('property_rights', 0.5),
        }

    def get_cultural_state(self) -> Dict:
        """
        获取文化状态 - Get cultural state indicators.

        Returns dict with:
        - hegemony_strength: 霸权强度
        - legitimacy: 合法性
        - avg_class_consciousness: 平均阶级意识
        - ideology_content: 意识形态内容
        """
        if not self._ideology_manager:
            return self._default_cultural_state()

        metrics = self._ideology_manager.get_hegemony_metrics()
        return {
            'hegemony_strength': metrics.get('hegemony_strength', 0.5),
            'legitimacy': metrics.get('legitimacy', 0.7),
            'avg_class_consciousness': metrics.get('avg_class_consciousness', 0.2),
            'ideology_content': metrics.get('ideology_content', 'unknown'),
        }

    def get_legitimacy_warning(self) -> bool:
        """检查是否需要合法性警告"""
        cultural_state = self.get_cultural_state()
        return cultural_state.get('legitimacy', 1.0) < 0.3

    def generate_state_description(self) -> str:
        """
        生成状态自然语言描述 - Generate natural language description.

        Returns a string describing the current political-cultural state.
        """
        political = self.get_political_state()
        cultural = self.get_cultural_state()

        stage_name = self._get_stage_name()

        # 政体描述
        regime_desc = self._describe_regime(political['regime_type'])

        # 参政水平描述
        suffrage_desc = self._describe_suffrage(political['suffrage_level'])

        # 意识形态描述
        ideology_desc = self._describe_ideology(cultural['ideology_content'])

        # 霸权描述
        hegemony_desc = self._describe_hegemony(cultural['hegemony_strength'])

        # 合法性警告
        warning = ""
        if cultural['legitimacy'] < 0.3:
            warning = "【危机警告】合法性低于30%，统治正当性严重不足！"

        description = (
            f"当前社会: {stage_name}\n"
            f"政体类型: {regime_desc}\n"
            f"参政水平: {suffrage_desc}\n"
            f"意识形态: {ideology_desc}\n"
            f"文化霸权: {hegemony_desc}\n"
            f"合法性: {cultural['legitimacy']*100:.0f}%\n"
        )

        if warning:
            description += f"\n{warning}"

        return description

    def _get_stage_name(self) -> str:
        """获取社会阶段中文名"""
        if not self.model:
            return "未知"

        stage = self.model.social_stage
        stage_names = {
            'primitive_horde': '原始群',
            'band': '游群',
            'tribe': '部落',
            'tribal_confederacy': '部落联盟',
            'chiefdom': '酋邦',
            'early_state': '早期国家',
            'slavery_state': '奴隶社会',
            'feudal_state': '封建社会',
            'capitalist_state': '资本主义',
            'socialist_state': '社会主义',
        }
        return stage_names.get(stage.value, stage.value)

    def _describe_regime(self, regime_type: str) -> str:
        """描述政体类型"""
        descriptions = {
            'tribal': '部落民主制',
            'slave_monarchy': '奴隶主君主制',
            'slave_aristocracy': '奴隶主贵族制',
            'feudal_monarchy': '封建君主制',
            'bourgeois_democracy': '资产阶级民主制',
            'workers_democracy': '工人民主制',
        }
        return descriptions.get(regime_type, regime_type)

    def _describe_suffrage(self, suffrage_level: float) -> str:
        """描述参政水平"""
        if suffrage_level >= 1.0:
            return "普遍选举权"
        elif suffrage_level >= 0.5:
            return "有限选举权"
        elif suffrage_level >= 0.2:
            return "高度限制的选举权"
        else:
            return "极少数人参政"

    def _describe_ideology(self, ideology_content: str) -> str:
        """描述意识形态内容"""
        descriptions = {
            'primitive_communal': '原始共产主义意识形态',
            'slave_society': '奴隶制意识形态',
            'feudalism': '封建主义意识形态',
            'capitalism': '资产阶级意识形态',
            'socialism': '社会主义意识形态',
            'communal': '部落共有制意识形态',
        }
        return descriptions.get(ideology_content, f'{ideology_content}意识形态')

    def _describe_hegemony(self, hegemony_strength: float) -> str:
        """描述霸权强度"""
        if hegemony_strength >= 0.7:
            return "强势文化霸权，统治阶级意识形态占主导地位"
        elif hegemony_strength >= 0.5:
            return "中等霸权，统治思想具有较强影响力"
        elif hegemony_strength >= 0.3:
            return "弱霸权，阶级意识开始觉醒"
        else:
            return "霸权危机，意识形态控制力严重不足"

    def _default_political_state(self) -> Dict:
        """默认政治状态"""
        return {
            'regime_type': 'tribal',
            'suffrage_level': 1.0,
            'tax_rate': 0.05,
            'repression_level': 0.2,
            'property_rights': 0.5,
        }

    def _default_cultural_state(self) -> Dict:
        """默认文化状态"""
        return {
            'hegemony_strength': 0.5,
            'legitimacy': 0.7,
            'avg_class_consciousness': 0.2,
            'ideology_content': 'communal',
        }

    def get_crisis_warnings(self) -> List[str]:
        """
        获取危机警告列表 - Get list of crisis warnings.

        Returns list of warning strings for various crisis conditions.
        """
        warnings = []

        political = self.get_political_state()
        cultural = self.get_cultural_state()

        # 合法性危机
        if cultural['legitimacy'] < 0.3:
            warnings.append(f"【合法性危机】合法性仅剩 {cultural['legitimacy']*100:.0f}%")

        # 镇压过度
        if political['repression_level'] > 0.7:
            warnings.append(f"【镇压警告】镇压水平过高 ({political['repression_level']*100:.0f}%)")

        # 阶级意识觉醒
        if cultural['avg_class_consciousness'] > 0.4:
            warnings.append(f"【阶级觉醒】被统治阶级意识正在觉醒 ({cultural['avg_class_consciousness']*100:.0f}%)")

        # 霸权虚弱
        if cultural['hegemony_strength'] < 0.3:
            warnings.append(f"【霸权危机】文化霸权控制力严重不足")

        return warnings

    def render_panel(self) -> Dict:
        """
        渲染面板 - Render the complete social panel.

        Returns dict with all panel data ready for display.
        """
        return {
            'political_state': self.get_political_state(),
            'cultural_state': self.get_cultural_state(),
            'legitimacy_warning': self.get_legitimacy_warning(),
            'description': self.generate_state_description(),
            'crisis_warnings': self.get_crisis_warnings(),
        }