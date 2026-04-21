# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本代码库中工作时提供指导。

## 项目概述

**CapitalSimulator** 是一个基于 Mesa 和 NetworkX 的马克思主义经济模拟器（Agent-Based Model, ABM）。实现历史唯物主义政治经济学——模拟阶级关系、价值形式、货币、危机以及生产方式转变（原始共产 → 奴隶 → 封建 → 资本 → 社会主义）的涌现。

**理论依据**: 马克思《资本论》全三卷、阿尔都塞结构因果性、广松涉物象化论。

## 命令

```bash
# 运行模拟
python src/run.py

# 运行测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_marxist_laws.py -v

# 运行 Jupyter notebooks
jupyter notebook notebooks/01_primitive_early.ipynb
```

## 架构

### 核心原则：禁止"人性"行为假设
Agent 行为由 `SocialRelationGraph` 边**结构性地决定**——而非贪婪、效用最大化。图的边类型（Kinship, Clan, Barter, Tributary, MilitaryService, Residence, Enslavement, FeudalRent, WageContract, Training, ColonialExtraction, Planning）定义生产关系和阶级位置。

### 社会阶段框架 (塞维斯-弗里德框架)
`src/model/social_stage.py` 定义 10 阶段演进:
| 阶段 | 核心关系边 |
|------|-----------|
| PRIMITIVE_HORDE | 无 |
| BAND | KinshipEdge |
| TRIBE | ClanEdge |
| TRIBAL_CONFEDERACY | MilitaryAllianceEdge |
| CHIEFDOM | TributaryEdge |
| EARLY_STATE | ResidenceEdge |
| SLAVERY_STATE | EnslavementEdge |
| FEUDAL_STATE | FeudalRentEdge |
| CAPITALIST_STATE | WageContractEdge |
| SOCIALIST_STATE | PlanningEdge |

### 物品四态机 (`src/model/ontology.py`)
| 状态 | 描述 |
|------|------|
| `STATE_USELESS` | 无法满足任何人类需求 |
| `STATE_PURE_USE_VALUE` | 无劳动介入的自然物 |
| `STATE_PRODUCT` | 凝结了个别劳动的有用物 |
| `STATE_COMMODITY` | 用于交换的产品 (exchange_status="Pending") |

**关键**: 价值和使用价值**绝不是静态属性**。使用价值是动态匹配事件，价值是事后 SNLT 幽灵比例。

### 社会关系图 (`src/model/relations.py`)
- 基于 NetworkX `MultiDiGraph`
- 阶级位置由边类型推断，而非 Agent 类型声明
- 边类型: KINSHIP, BARTER, ENSLAVEMENT, FEUDAL_RENT, WAGE_CONTRACT, PLANNING

### 主模型 (`src/model/model.py`)
- `CapitalModel` 协调所有子系统
- 步进顺序: 生产方式转变评估 → Agent 行动 → 地景再生 → 危机检测 → 数据收集

### 关键模块
| 模块 | 用途 |
|------|------|
| `src/model/` | 核心: 本体、Agent、社会关系、地景、生产方式 |
| `src/engine/` | 经济引擎: SNLT计算、生产、磨损、再生产、阶级斗争 |
| `src/superstructure/` | 国家机器、法律体系、意识形态、政治体制 |
| `src/international/` | 外国市场、殖民地、贸易路由 |
| `src/military/` | 军队、国防工业、战争事件 |
| `src/population/` | 人口统计、迁移 |
| `src/analysis/` | 数据收集、指标、价值形式分析 |
| `src/visualization/` | Plotly 图表、Dash 应用 |

## 马克思主义红线（绝对禁止）

1. **本体论红线**: 禁止将 `value` 或 `use_value` 存储为静态属性
2. **行为学红线**: 禁止在 Agent.step() 中写入基于"贪婪/效用最大化"的 if-else 逻辑
3. **术语红线**: 使用严格马克思主义术语——见 `开发大纲.md` 附录 A/B
4. **机制红线**: 机器只能转移价值(c)，不能创造新价值；工资是劳动力价格，不是劳动报酬
5. **测试红线**: 任何 PR 必须包含 `tests/test_marxist_laws.py` 中的测试
6. **先验性红线**: 禁止预设复杂劳动倍加系数或固定技能要求表

## 开发里程碑

当前状态: **M1-M5 完成** (v0.6)
- M1: 环境搭建 + 原始社会
- M2: 农业定居 + 生产系统
- M3: 价值形式 + 危机检测 + 上层建筑 + 国际 + 军事 + 人口
- M4: 奴隶社会模块
- M5: 封建社会模块

计划中: M6-M7 (资本主义), M8-M9 (社会主义)

## 数据收集

`DataCollector` 追踪: 总人口、边类型计数、平均生存资料满足率、再生产指标、危机指标。通过 `model.data_collector.get_history()` 访问。

## 文件命名约定

- Agent: `src/model/agents.py`
- SNLT 引擎: `src/engine/labor_value.py`
- 危机检测: `src/engine/reproduction.py`
- 社会阶段转变: `src/model/social_stage.py`
- 旧版生产方式 (已废弃): `src/model/mode_of_production.py`
