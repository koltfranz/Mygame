# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

基于马克思《资本论》的政治经济学模拟游戏，用于演示政治经济学核心概念。程序模拟从原始社会到资本主义社会的经济发展过程。

## 常用命令

```bash
# 构建项目
dotnet build Capital/Capital.csproj

# 运行程序
dotnet run --project Capital/Capital.csproj
```

## 代码架构

### 核心概念与类的对应

| 经济学概念 | 程序实现 |
|-----------|---------|
| 具体劳动（质的劳动，如狩猎、纺织） | `Labor.ConcreteLabor` |
| 抽象劳动（无差别的人类劳动） | `Labor.AbstractLabor` |
| 简单劳动（K=1，无专业技能） | `Labor.K = 1`，`LaborType.SimpleLabor` |
| 复杂劳动（K>1，需专业技能） | `Labor.K > 1`，`LaborType.ComplexLabor` |
| 使用价值（商品的有用性） | `Product.Usefulness` |
| 交换价值（商品间的交换比例） | `Commodity.Exchange()` |
| 价值（凝结的抽象劳动时间） | `Commodity.Value` = `Labor.AbstractLabor` |

### 核心类

**Product（产品）** - 只有使用价值，不用于交换
- `Name`, `Usefulness`（有用性）
- `Labor?`（可选，原始产品可能无劳动）

**Commodity（商品）** - 继承Product，既有使用价值又有交换价值
- `Value`: 凝结的抽象劳动时间
- `Labor`: 生产所需的劳动（必需）
- `Exchange()`: 计算与其他商品的交换比例

**Labor（劳动）**
- `ConcreteLabor`: 具体劳动类型名称
- `AbstractLabor`: 抽象劳动时间（LaborTime类型）
- `K`: 复杂劳动转化系数（K=1为简单劳动）

**LaborTime（劳动时间）** - 结构体
- 以小时为基准单位
- 支持隐式转换为double

**Person（人）**
- `Name`, `Age`, `Gender`
- `Labor()`: 从事劳动
- `Eat()`: 吃东西
- `Satiation`: 饱食度
- `Health`: 健康值

### 继承关系

```
Product（产品，有使用价值）
    └── Commodity（商品，有交换价值）
            └── 需要关联 Labor 对象
```

### 项目结构

```
d:\code\Mygame\
├── Capital.slnx           # 解决方案文件
├── CLAUDE.md              # 本文件
├── Capital/
│   ├── Capital.csproj     # 项目文件
│   ├── Program.cs         # 程序入口
│   ├── Labor.cs           # 劳动类（含LaborTime、LaborType）
│   ├── Product.cs         # 产品类
│   ├── Commodity.cs       # 商品类
│   ├── ValueForm.cs        # 价值形式（待实现）
│   └── Person.cs           # 人物类
```

## 设计原则

1. **产品≠商品**：原始社会产品不是商品，商品必须用于交换
2. **劳动二重性**：具体劳动创造使用价值，抽象劳动形成价值
3. **简单劳动→复杂劳动**：通过K值转化，复杂劳动是多倍简单劳动
4. **价值决定交换**：交换价值由价值量决定
