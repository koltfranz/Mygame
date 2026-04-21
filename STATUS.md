# CapitalSimulator 项目状态

**最后更新**: 2026-04-21
**版本**: v0.6 (基于开发大纲 v10.2)

## 框架升级 (v10.2)

### 社会阶段框架 (塞维斯-弗里德框架)
- [x] SocialStage 枚举 (10个阶段)
- [x] TransitionEngine 转型引擎
- [x] 关系边类型扩展 (12种)

### 社会阶段枚举
| 阶段 | 人口规模 | 核心关系边 |
|------|----------|-----------|
| PRIMITIVE_HORDE | 10-30 | 无 |
| BAND | 20-50 | KinshipEdge |
| TRIBE | 100-500 | ClanEdge |
| TRIBAL_CONFEDERACY | 500-2000 | MilitaryAllianceEdge |
| CHIEFDOM | 2000-10000 | TributaryEdge |
| EARLY_STATE | 10000+ | ResidenceEdge |
| SLAVERY_STATE | 可变 | EnslavementEdge |
| FEUDAL_STATE | 可变 | FeudalRentEdge |
| CAPITALIST_STATE | 可变 | WageContractEdge |
| SOCIALIST_STATE | 可变 | PlanningEdge |

### 关系边类型 (12种)
Kinship, Clan, Barter, Tributary, MilitaryService, Residence, Enslavement, FeudalRent, WageContract, Training, ColonialExtraction, Planning

## 已完成里程碑

### M1: 环境搭建 + 原始社会早期 ✓
- [x] Mesa 框架集成
- [x] 物品四态机 (State_Useless/Pure_Use_Value/Product/Commodity)
- [x] 社会关系图 (NetworkX)
- [x] Forager/TribeMember Agent
- [x] Landscape 地块系统
- [x] 数据收集器

### M2: 农业定居 + 生产函数 ✓
- [x] ProductionSystem 生产系统
- [x] 技能要求动态计算
- [x] SNLTCalculator 劳动价值计算
- [x] DepreciationEngine 生产资料磨损
- [x] Farmer Agent
- [x] SocialStage 状态机

### M3: 价值形式与危机 ✓
- [x] ValueFormRouter 价值形式路由
- [x] ValueFormAnalyzer 价值形式分析
- [x] ReproductionEngine 再生产引擎
- [x] CrisisDetection 危机检测
- [x] 上层建筑模块 (State, Legal, Ideology, Political)
- [x] 国际模块 (ForeignMarket, Colony, TradeRouter)
- [x] 军事模块 (Army, DefenseIndustry, WarEvent)
- [x] 人口模块 (Demography, Migration)
- [x] 可视化 (Plotly, Dash)

### M4: 奴隶社会模块 ✓
- [x] Slave/SlaveOwner Agent 完善
- [x] EnslavementEdge 边类型
- [x] 奴隶劳动产出剥夺机制
- [x] 抵抗机制 (resistance_level)
- [x] 系统性提取逻辑
- [x] M4 测试用例 (12 tests)

### M5: 封建社会模块 ✓
- [x] Serf/Lord Agent 完善
- [x] FeudalRentEdge 边类型
- [x] 地租支付机制
- [x] 领主清理死亡农奴
- [x] M5 测试用例 (12 tests)

## 项目结构

```
src/
├── model/          # 核心模型
│   ├── ontology.py        # 物品四态机
│   ├── relations.py      # 社会关系图
│   ├── agents.py          # Agent类型
│   ├── model.py          # Mesa模型
│   ├── resources.py      # 资源系统
│   ├── mode_of_production.py  # 生产方式
│   └── agent_initializers.py  # Agent工厂
├── engine/         # 经济引擎
│   ├── labor_value.py     # SNLT计算
│   ├── production.py      # 生产函数
│   ├── depreciation.py    # 磨损转移
│   ├── reproduction.py    # 再生产
│   ├── value_form_router.py  # 价值形式
│   └── class_struggle.py  # 阶级斗争
├── superstructure/  # 上层建筑
│   ├── state_apparatus.py
│   ├── legal_system.py
│   ├── ideology_manager.py
│   └── political_regime.py
├── international/   # 国际经济
│   ├── foreign_market.py
│   ├── colony.py
│   └── trade_router.py
├── military/        # 军事
│   ├── army.py
│   ├── defense_industry.py
│   └── war_event.py
├── population/      # 人口
│   ├── demography.py
│   └── migration.py
├── analysis/        # 分析
│   ├── data_collector.py
│   ├── metrics.py
│   └── value_form.py
└── visualization/   # 可视化
    ├── plotly_charts.py
    └── dash_app.py
```

## 待完成里程碑

### M6-M7: 资本主义模块 (规划中)
- Worker/Capitalist Agent
- WageContractRelation边类型
- 剩余价值计算
- 利润率平均化
- 生产价格

### M8-M9: 社会主义与发布 (规划中)
- PlanningEdge
- 计划配置
- 可视化完善
- 文档

## 测试状态

```
tests/
├── test_ontology.py        ✓ 物品状态机测试 (11/11 通过)
├── test_marxist_laws.py    ✓ 马克思主义红线测试 (6/6 通过)
├── test_slave_society.py   ✓ 奴隶社会模块测试 (12/12 通过)
└── test_feudal_society.py  ✓ 封建社会模块测试 (12/12 通过)
```

## 运行命令

```bash
# 运行模拟
python src/run.py

# 运行测试
pytest tests/ -v

# 运行Notebook
jupyter notebook notebooks/01_primitive_early.ipynb
```

## 马克思主义红线验证

✓ **本体论红线**: 价值不是静态属性，通过SNLT事后计算
✓ **行为学红线**: Agent行为由社会关系图决定，不是"人性"
✓ **机制红线**: 机器只能转移价值(wear transfer)，不能创造价值
✓ **剥削率红线**: 工资是劳动力价格，不是劳动报酬
✓ **危机红线**: 危机来自利润率下降，不是需求不足
