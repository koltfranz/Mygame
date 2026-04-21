"""
CapitalSimulator - A Marxist Economic Simulation

Run with: python src/run.py
"""

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.model.model import CapitalModel
import matplotlib.pyplot as plt


def run_simulation(steps: int = 100,
                   num_foragers: int = 50,
                   num_tribe_members: int = 50):
    """
    运行模拟 - Run the simulation.

    Args:
        steps: Number of simulation steps
        num_foragers: Initial number of forager agents
        num_tribe_members: Initial number of tribe member agents
    """
    print("=" * 60)
    print("         CapitalSimulator 资本模拟器")
    print("=" * 60)
    print(f"初始设置: {num_foragers} 采集者, {num_tribe_members} 部落成员")
    print(f"模拟步数: {steps}")
    print()

    # Create model
    model = CapitalModel(
        width=100,
        height=100,
        num_foragers=num_foragers,
        num_tribe_members=num_tribe_members
    )

    # Run simulation
    print("-" * 60)
    print("开始模拟...")
    print("-" * 60)

    for i in range(steps):
        old_stage = model.social_stage
        model.step()
        new_stage = model.social_stage

        # 跃迁通知
        if old_stage != new_stage:
            print(f"\n*** 【重大事件】社会阶段跃迁 ***")
            print(f"    {old_stage.value} -> {new_stage.value}")
            print("-" * 60)

        # 每 20 步输出详细状态
        if (i + 1) % 20 == 0:
            data = model.data_collector.get_latest()
            stage = model.social_stage.value

            print(f"\n【Step {i+1}】")
            print(f"  社会阶段: {stage}")
            print(f"  总人口: {data['total_population']}")
            print(f"  平均生存资料满足率: {data['average_subsistence']:.2f}")

            # 阶级分布
            if 'class_distribution' in data:
                classes = data['class_distribution']
                non_zero = {k: v for k, v in classes.items() if v > 0}
                if non_zero:
                    print(f"  阶级分布: {non_zero}")

            # 社会关系
            edge_counts = model.social_graph.get_edge_count_by_type()
            if edge_counts:
                print(f"  社会关系: {edge_counts}")

    print()
    print("=" * 60)
    print("模拟完成!")
    print("=" * 60)

    # 最终状态摘要
    _print_final_summary(model)

    # 绘制图表
    _plot_results(model.data_collector.get_history())

    return model


def _print_final_summary(model: CapitalModel):
    """打印最终状态摘要"""
    print("\n【最终状态摘要】")

    # 阶段信息
    print(f"  社会阶段: {model.social_stage.value}")

    # 人口
    pop = model.get_population_count()
    print(f"  总人口: {pop}")

    # 生存资料
    subs = model.get_average_subsistence()
    print(f"  平均生存资料满足率: {subs:.2f}")

    # 跃迁历史
    history = model.data_collector.get_history()
    transitions = []
    for i in range(1, len(history)):
        # 检测模式变化（通过阶级分布变化推断）
        pass  # 简化处理

    # 阶级分布
    final_data = model.data_collector.get_latest()
    if 'class_distribution' in final_data:
        classes = final_data['class_distribution']
        non_zero = {k: v for k, v in classes.items() if v > 0}
        if non_zero:
            print(f"  阶级分布:")
            for cls, count in sorted(non_zero.items(), key=lambda x: -x[1]):
                print(f"    {cls}: {count}")

    # 社会关系统计
    edge_counts = model.social_graph.get_edge_count_by_type()
    if edge_counts:
        print(f"  社会关系统计:")
        for edge_type, count in edge_counts.items():
            print(f"    {edge_type}: {count}")

    # 跃迁条件
    te = model.transition_engine
    surplus = te._calculate_surplus_ratio(model)
    strat = te._calculate_stratification(model)
    density = te._calculate_density(model)
    print(f"  跃迁指标:")
    print(f"    剩余生产率: {surplus:.2f}")
    print(f"    社会分化度: {strat:.2f}")
    print(f"    人口密度: {density:.2f}")


def _plot_results(history: list):
    """绘制结果图表"""
    if not history:
        return

    steps = [h['step'] for h in history]
    population = [h['total_population'] for h in history]
    subsistence = [h['average_subsistence'] for h in history]

    # 提取阶级分布
    class_keys = set()
    for h in history:
        if 'class_distribution' in h:
            class_keys.update(h['class_distribution'].keys())

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 人口变化
    ax1 = axes[0, 0]
    ax1.plot(steps, population, 'b-', linewidth=2)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Population')
    ax1.set_title('Population Over Time')
    ax1.grid(True, alpha=0.3)

    # 生存资料满足率
    ax2 = axes[0, 1]
    ax2.plot(steps, subsistence, 'g-', linewidth=2)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Subsistence Satisfaction')
    ax2.set_title('Average Subsistence Satisfaction')
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3)

    # 阶级分布变化
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

    # 社会关系变化
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
    print(f"\n图表已保存到 simulation_results.png")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CapitalSimulator')
    parser.add_argument('--steps', type=int, default=200, help='模拟步数')
    args = parser.parse_args()
    run_simulation(steps=args.steps)
