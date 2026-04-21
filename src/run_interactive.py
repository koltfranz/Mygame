"""
CapitalSimulator - Interactive Mode

Run with: python src/run_interactive.py

Features:
- Step-by-step execution with detailed output
- Pause/continue option after each step
- See class distribution and social relations in real-time
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.model.model import CapitalModel
import matplotlib.pyplot as plt


def run_interactive(steps: int = 100,
                   num_foragers: int = 50,
                   num_tribe_members: int = 50,
                   auto_mode: bool = False):
    """
    交互式运行模拟 - Interactive simulation.

    Args:
        steps: Number of simulation steps
        num_foragers: Initial number of forager agents
        num_tribe_members: Initial number of tribe member agents
        auto_mode: If True, run without pausing (press Ctrl+C to stop)
    """
    print("=" * 70)
    print("         CapitalSimulator 资本模拟器 - 交互模式")
    print("=" * 70)
    print(f"初始设置: {num_foragers} 采集者, {num_tribe_members} 部落成员")
    print(f"模拟步数: {steps}")
    print(f"自动模式: {'是' if auto_mode else '否'}")
    print()
    print("控制说明:")
    print("  [Enter] - 执行下一步")
    print("  'a' + [Enter] - 切换自动模式 (自动执行所有步)")
    print("  'q' + [Enter] - 退出模拟")
    print("  's' + [Enter] - 跳过查看直接运行到最后")
    print("  'p' + [Enter] - 查看当前状态详情")
    print("=" * 70)

    if not auto_mode:
        input("按 Enter 开始...")

    # Create model
    model = CapitalModel(
        width=100,
        height=100,
        num_foragers=num_foragers,
        num_tribe_members=num_tribe_members
    )

    # Run simulation
    running = True
    step_count = 0

    while running and step_count < steps:
        step_count += 1
        old_stage = model.social_stage
        model.step()
        new_stage = model.social_stage

        # 清屏效果 - 打印当前步信息
        print("\n" + "=" * 70)
        print(f"  Step {step_count}/{steps}")
        print("=" * 70)

        # 跃迁通知
        if old_stage != new_stage:
            print(f"\n*** 【重大事件】社会阶段跃迁 ***")
            print(f"    {old_stage.value} -> {new_stage.value}")
            print("-" * 70)

        # 核心指标
        data = model.data_collector.get_latest()
        stage = model.social_stage.value
        pop = data['total_population']
        subs = data['average_subsistence']

        print(f"\n【{stage}】")
        print(f"  人口: {pop}")
        print(f"  生存资料满足率: {subs:.2f}")

        # 阶级分布
        if 'class_distribution' in data:
            classes = data['class_distribution']
            non_zero = {k: v for k, v in classes.items() if v > 0}
            if non_zero:
                print(f"\n  阶级分布:")
                for cls, count in sorted(non_zero.items(), key=lambda x: -x[1]):
                    bar = "█" * count
                    print(f"    {cls:12}: {count:3} {bar}")

        # 社会关系
        edge_counts = model.social_graph.get_edge_count_by_type()
        if edge_counts:
            print(f"\n  社会关系:")
            for edge_type, count in edge_counts.items():
                bar = "#" * min(count, 20)
                print(f"    {edge_type:12}: {count:3} {bar}")

        # 跃迁指标
        te = model.transition_engine
        surplus = te._calculate_surplus_ratio(model)
        strat = te._calculate_stratification(model)
        density = te._calculate_density(model)
        print(f"\n  跃迁指标:")
        print(f"    剩余生产率: {surplus:8.2f} (需>0.2)")
        print(f"    社会分化度: {strat:8.2f} (需>0.5)")
        print(f"    人口密度:   {density:8.2f} (需>0.3)")

        if not auto_mode:
            print("\n" + "-" * 70)
            print("控制: [Enter]=下一步, 'a'=自动模式, 'q'=退出, 's'=跳过, 'p'=详情")
            choice = input("> ").strip().lower()

            if choice == 'q':
                print("退出模拟...")
                running = False
            elif choice == 'a':
                auto_mode = True
                print("切换到自动模式，按 Ctrl+C 停止...")
            elif choice == 's':
                print("跳转到最后...")
                # 运行剩余步
                prev_stage = model.social_stage
                for i in range(step_count, steps):
                    model.step()
                    if model.social_stage != prev_stage:
                        print(f"\n*** 跃迁: {prev_stage.value} -> {model.social_stage.value} ***")
                        prev_stage = model.social_stage
                step_count = steps
            elif choice == 'p':
                _print_detailed_status(model)

    # 结束
    print("\n" + "=" * 70)
    print("模拟完成!")
    print("=" * 70)
    _print_final_summary(model)

    # 绘图
    history = model.data_collector.get_history()
    if history:
        _plot_results(history)
        print(f"\n图表已保存到 simulation_results.png")

    return model


def _print_detailed_status(model: CapitalModel):
    """打印详细状态"""
    print("\n" + "=" * 70)
    print("           详细状态")
    print("=" * 70)

    # 所有 agent 列表
    print(f"\n【Agent 列表】(共 {len(model._agent_lookup)} 个)")
    print("-" * 70)

    for agent in list(model.agents)[:20]:  # 只显示前20个
        class_pos = model.social_graph.infer_class_position(agent.unique_id)
        inventory = len(agent.commodity_inventory)
        subs = agent.subsistence_satisfaction
        labor = agent.labor_power_capacity

        print(f"  {type(agent).__name__:12} id={agent.unique_id:3} | "
              f"阶级:{class_pos:12} | "
              f"库存:{inventory:2} | "
              f"生存:{subs:.2f} | "
              f"劳动:{labor:.2f}")

    if len(model._agent_lookup) > 20:
        print(f"  ... 还有 {len(model._agent_lookup) - 20} 个 agent")

    # 商品库存详情
    print(f"\n【商品库存】")
    all_items = []
    for agent in model._agent_lookup.values():
        for item in agent.commodity_inventory:
            name = item.physical_props.get('name', 'unknown')
            state = item.state.value
            labor = item.individual_labor_embodied
            all_items.append((name, state, labor))

    item_counts = {}
    for name, state, labor in all_items:
        key = f"{name}({state})"
        if key not in item_counts:
            item_counts[key] = {'count': 0, 'labor': 0}
        item_counts[key]['count'] += 1
        item_counts[key]['labor'] += labor

    for item, info in sorted(item_counts.items(), key=lambda x: -x[1]['count'])[:10]:
        print(f"  {item:20}: {info['count']:3} 个, 总劳动凝结: {info['labor']:.1f}")

    print("-" * 70)
    input("按 Enter 继续...")


def _print_final_summary(model: CapitalModel):
    """打印最终状态摘要"""
    print("\n【最终状态摘要】")

    print(f"  社会阶段: {model.social_stage.value}")

    pop = model.get_population_count()
    print(f"  总人口: {pop}")

    subs = model.get_average_subsistence()
    print(f"  平均生存资料满足率: {subs:.2f}")

    final_data = model.data_collector.get_latest()
    if 'class_distribution' in final_data:
        classes = final_data['class_distribution']
        non_zero = {k: v for k, v in classes.items() if v > 0}
        if non_zero:
            print(f"\n  阶级分布:")
            for cls, count in sorted(non_zero.items(), key=lambda x: -x[1]):
                print(f"    {cls}: {count}")

    edge_counts = model.social_graph.get_edge_count_by_type()
    if edge_counts:
        print(f"\n  社会关系统计:")
        for edge_type, count in edge_counts.items():
            print(f"    {edge_type}: {count}")


def _plot_results(history: list):
    """绘制结果图表"""
    if not history:
        return

    steps = [h['step'] for h in history]
    population = [h['total_population'] for h in history]
    subsistence = [h['average_subsistence'] for h in history]

    class_keys = set()
    for h in history:
        if 'class_distribution' in h:
            class_keys.update(h['class_distribution'].keys())

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax1 = axes[0, 0]
    ax1.plot(steps, population, 'b-', linewidth=2)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Population')
    ax1.set_title('Population Over Time')
    ax1.grid(True, alpha=0.3)

    ax2 = axes[0, 1]
    ax2.plot(steps, subsistence, 'g-', linewidth=2)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Subsistence Satisfaction')
    ax2.set_title('Average Subsistence Satisfaction')
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3)

    ax3 = axes[1, 0]
    class_names = ['forager', 'tribe_member', 'slave', 'slave_owner', 'serf', 'lord', 'worker', 'capitalist']
    for cls in class_names:
        values = [h.get('class_distribution', {}).get(cls, 0) for h in history]
        if any(v > 0 for v in values):
            ax3.plot(steps, values, label=cls, linewidth=2)
    ax3.set_xlabel('Step')
    ax3.set_ylabel('Count')
    ax3.set_title('Class Distribution Over Time')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)

    ax4 = axes[1, 1]
    relation_names = ['kinship', 'enslavement', 'feudal_rent', 'wage_contract']
    for rel in relation_names:
        values = [h.get(rel, 0) for h in history]
        if any(v > 0 for v in values):
            ax4.plot(steps, values, label=rel, linewidth=2)
    ax4.set_xlabel('Step')
    ax4.set_ylabel('Count')
    ax4.set_title('Social Relations Over Time')
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('simulation_results.png', dpi=150)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CapitalSimulator Interactive Mode')
    parser.add_argument('--steps', type=int, default=100, help='模拟步数')
    parser.add_argument('--foragers', type=int, default=50, help='采集者数量')
    parser.add_argument('--tribe', type=int, default=50, help='部落成员数量')
    parser.add_argument('--auto', action='store_true', help='自动模式')
    args = parser.parse_args()

    run_interactive(
        steps=args.steps,
        num_foragers=args.foragers,
        num_tribe_members=args.tribe,
        auto_mode=args.auto
    )
