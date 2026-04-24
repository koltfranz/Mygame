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
    print("=" * 80)
    print("                    CapitalSimulator 资本模拟器")
    print("=" * 80)
    print(f"【初始设置】采集者: {num_foragers}, 部落成员: {num_tribe_members}, 步数: {steps}")
    print()

    # Create model
    model = CapitalModel(
        width=100,
        height=100,
        num_foragers=num_foragers,
        num_tribe_members=num_tribe_members
    )

    # Run simulation
    print("-" * 80)
    print("开始模拟...")
    print("-" * 80)

    for i in range(steps):
        old_stage = model.social_stage
        model.step()
        new_stage = model.social_stage

        # 跃迁通知
        if old_stage != new_stage:
            print(f"\n{'*' * 80}")
            print(f"  【重大事件】社会阶段跃迁: {old_stage.value} -> {new_stage.value}")
            print(f"  当前年份: {model.get_formatted_year()}")
            print(f"{'*' * 80}\n")

        # 每 20 步输出详细状态
        if (i + 1) % 20 == 0:
            _print_step_report(model, i + 1)

    print()
    print("=" * 80)
    print("模拟完成!")
    print("=" * 80)

    # 最终状态摘要
    _print_final_summary(model)

    # 绘制图表
    _plot_results(model.data_collector.get_history())

    return model


def _print_step_report(model, step: int):
    """打印每步详细报告（中文）"""
    data = model.data_collector.get_latest()

    print(f"\n{'=' * 80}")
    print(f"  【第 {step} 步】 {model.get_formatted_year()}")
    print(f"{'=' * 80}")

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
    stage_name = stage_names.get(model.social_stage.value, model.social_stage.value)
    print(f"\n【社会阶段】{stage_name} ({model.social_stage.value})")

    # 人口指标
    print(f"\n【人口指标】")
    print(f"  总人口: {data.get('total_population', 0)}")
    pop_dyn = data.get('population_dynamics', {})
    print(f"  出生率: {pop_dyn.get('birth_rate', 0):.4f}")
    print(f"  死亡率: {pop_dyn.get('death_rate', 0):.4f}")
    print(f"  增长率: {pop_dyn.get('growth_rate', 0):.4f}")
    print(f"  总和生育率: {pop_dyn.get('total_fertility_rate', 0):.2f}")

    # 生存资料
    print(f"\n【生存资料】")
    print(f"  平均生存资料满足率: {data.get('average_subsistence', 0):.2%}")

    # 经济指标
    print(f"\n【经济指标】")
    econ = data.get('economic_metrics', {})
    print(f"  剩余价值率 (s/v): {econ.get('rate_of_surplus_value', 0):.4f}")
    print(f"  资本有机构成 (c/v): {econ.get('organic_composition', 0):.4f}")
    print(f"  利润率 p': {econ.get('rate_of_profit', 0):.4f}")
    print(f"  部类偏离度: {econ.get('department_imbalance', 0):.4f}")
    print(f"  平均库存: {econ.get('avg_inventory', 0):.2f}")
    print(f"  平均劳动能力: {econ.get('avg_labor_capacity', 0):.2f}")
    print(f"  平均技能水平: {econ.get('avg_skill_level', 0):.2f}")

    # 阶级分布
    print(f"\n【阶级分布】")
    class_dist = data.get('class_distribution', {})
    class_names_cn = {
        'forager': '采集者',
        'tribe_member': '部落成员',
        'worker': '工人',
        'capitalist': '资本家',
        'slave': '奴隶',
        'slave_owner': '奴隶主',
        'serf': '农奴',
        'lord': '领主',
    }
    non_zero = {k: v for k, v in class_dist.items() if v > 0}
    if non_zero:
        for cls, count in sorted(non_zero.items(), key=lambda x: -x[1]):
            cn_name = class_names_cn.get(cls, cls)
            print(f"  {cn_name}: {count}")
    else:
        print("  无")

    # 社会关系
    print(f"\n【社会关系】")
    network = data.get('network_metrics', {})
    edge_counts = network.get('edge_counts', {})
    if edge_counts:
        edge_names_cn = {
            'kinship': '血缘关系',
            'clan': '氏族关系',
            'barter': '物物交换',
            'enslavement': '奴役关系',
            'feudal_rent': '封建地租',
            'wage_contract': '雇佣关系',
            'residence': '地缘关系',
            'tributary': '贡赋关系',
        }
        for etype, count in edge_counts.items():
            cn_name = edge_names_cn.get(etype, etype)
            print(f"  {cn_name}: {count}")
        print(f"  图密度: {network.get('graph_density', 0):.4f}")
        print(f"  地缘关系比例: {network.get('residence_ratio', 0):.4f}")
        print(f"  血缘关系比例: {network.get('kinship_ratio', 0):.4f}")
        print(f"  一般等价物集中度: {network.get('general_equivalent_concentration', 0):.4f}")
        print(f"  物象化指数: {network.get('fetishism_index', 0):.4f}")
    else:
        print("  无")

    # 跃迁指标
    print(f"\n【跃迁指标】")
    trans = data.get('transition_indicators', {})
    print(f"  剩余生产率: {trans.get('surplus_ratio', 0):.4f}")
    print(f"  社会分化度: {trans.get('stratification', 0):.4f}")
    print(f"  人口密度: {trans.get('density', 0):.4f}")

    # 政治指标
    print(f"\n【政治指标】")
    political = data.get('political_indicators', {})
    regime_type = political.get('regime_type', 'unknown')
    regime_names_cn = {
        "tribal": "部落民主制",
        "slave_monarchy": "奴隶主君主制",
        "feudal_monarchy": "封建君主制",
        "bourgeois_democracy": "资产阶级民主制",
        "workers_democracy": "无产阶级民主制",
        "unknown": "未知",
    }
    print(f"  政体类型: {regime_names_cn.get(regime_type, regime_type)}")
    print(f"  选举权水平: {political.get('suffrage_level', 0):.2%}")
    print(f"  国家镇压能力: {political.get('state_repression_capacity', 0):.2%}")
    print(f"  财政汲取能力: {political.get('fiscal_capacity', 0):.2%}")
    print(f"  法律形式平等指数: {political.get('legal_formal_equality', 0):.2%}")
    print(f"  产权保护强度: {political.get('property_rights_protection', 0):.2%}")
    print(f"  统治阶级: {political.get('ruling_class', 'none')}")

    # 文化指标
    print(f"\n【文化指标】")
    cultural = data.get('cultural_indicators', {})
    print(f"  意识形态内容: {cultural.get('ideology_content', 'unknown')}")
    print(f"  文化霸权强度: {cultural.get('hegemony_strength', 0):.2%}")
    print(f"  合法性分数: {cultural.get('legitimacy', 0):.2%}")
    print(f"  平均阶级意识: {cultural.get('avg_class_consciousness', 0):.2%}")

    # 危机指标
    print(f"\n【危机指标】")
    crisis = data.get('economic_metrics', {})
    if crisis.get('profit_rate', 0) < 0.1:
        print("  [WARNING] 利润率偏低，可能存在危机风险")
    if crisis.get('department_imbalance', 0) > 0.3:
        print("  [WARNING] 部类严重失衡，再生产出现问题")
    if cultural.get('legitimacy', 1) < 0.3:
        print("  [CRITICAL] 合法性危机！政权面临严重挑战")
    if cultural.get('legitimacy', 1) < 0.5 and cultural.get('legitimacy', 1) >= 0.3:
        print("  [CAUTION] 合法性下降，政权稳定性受到威胁")

    print()


def _print_final_summary(model: CapitalModel):
    """打印最终状态摘要（中文）"""
    print("\n" + "=" * 80)
    print("  【最终状态摘要】")
    print("=" * 80)

    history = model.data_collector.get_history()
    final_data = history[-1] if history else {}

    # 阶段信息
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
    stage_name = stage_names.get(model.social_stage.value, model.social_stage.value)
    print(f"\n【社会阶段】{stage_name} ({model.social_stage.value})")
    print(f"【当前年份】{model.get_formatted_year()}")

    # 人口
    pop = model.get_population_count()
    print(f"\n【人口】总人口: {pop}")

    if history and len(history) > 1:
        first_pop = history[0].get('total_population', pop)
        growth = (pop - first_pop) / max(first_pop, 1) * 100
        print(f"  初始人口: {first_pop}")
        print(f"  人口变化: {growth:+.2f}%")

    # 生存资料
    subs = model.get_average_subsistence()
    print(f"\n【生存资料】平均满足率: {subs:.2%}")

    # 人口动态
    pop_dyn = final_data.get('population_dynamics', {})
    print(f"  出生率: {pop_dyn.get('birth_rate', 0):.4f}")
    print(f"  死亡率: {pop_dyn.get('death_rate', 0):.4f}")
    print(f"  增长率: {pop_dyn.get('growth_rate', 0):.4f}")

    # 经济指标汇总
    print(f"\n【经济指标】")
    econ = final_data.get('economic_metrics', {})
    print(f"  剩余价值率 (s/v): {econ.get('rate_of_surplus_value', 0):.4f}")
    print(f"  资本有机构成 (c/v): {econ.get('organic_composition', 0):.4f}")
    print(f"  利润率 p': {econ.get('rate_of_profit', 0):.4f}")
    print(f"  部类偏离度: {econ.get('department_imbalance', 0):.4f}")

    # 阶级分布
    print(f"\n【阶级分布】")
    class_dist = final_data.get('class_distribution', {})
    class_names_cn = {
        'forager': '采集者',
        'tribe_member': '部落成员',
        'worker': '工人',
        'capitalist': '资本家',
        'slave': '奴隶',
        'slave_owner': '奴隶主',
        'serf': '农奴',
        'lord': '领主',
    }
    non_zero = {k: v for k, v in class_dist.items() if v > 0}
    if non_zero:
        for cls, count in sorted(non_zero.items(), key=lambda x: -x[1]):
            cn_name = class_names_cn.get(cls, cls)
            pct = count / max(pop, 1) * 100
            print(f"  {cn_name}: {count} ({pct:.1f}%)")
    else:
        print("  无阶级分化")

    # 社会关系汇总
    print(f"\n【社会关系】")
    network = final_data.get('network_metrics', {})
    edge_counts = network.get('edge_counts', {})
    edge_names_cn = {
        'kinship': '血缘关系',
        'clan': '氏族关系',
        'barter': '物物交换',
        'enslavement': '奴役关系',
        'feudal_rent': '封建地租',
        'wage_contract': '雇佣关系',
        'residence': '地缘关系',
        'tributary': '贡赋关系',
    }
    if edge_counts:
        for etype, count in edge_counts.items():
            cn_name = edge_names_cn.get(etype, etype)
            print(f"  {cn_name}: {count}")
        print(f"  图密度: {network.get('graph_density', 0):.4f}")
        print(f"  物象化指数: {network.get('fetishism_index', 0):.4f}")
    else:
        print("  无社会关系记录")

    # 政治指标汇总
    print(f"\n【政治指标】")
    political = final_data.get('political_indicators', {})
    regime_names_cn = {
        "tribal": "部落民主制",
        "slave_monarchy": "奴隶主君主制",
        "feudal_monarchy": "封建君主制",
        "bourgeois_democracy": "资产阶级民主制",
        "workers_democracy": "无产阶级民主制",
        "unknown": "未知",
    }
    print(f"  政体类型: {regime_names_cn.get(political.get('regime_type', 'unknown'), '未知')}")
    print(f"  国家镇压能力: {political.get('state_repression_capacity', 0):.2%}")
    print(f"  财政汲取能力: {political.get('fiscal_capacity', 0):.2%}")
    print(f"  法律形式平等: {political.get('legal_formal_equality', 0):.2%}")
    print(f"  产权保护: {political.get('property_rights_protection', 0):.2%}")
    print(f"  统治阶级: {political.get('ruling_class', 'none')}")

    # 文化指标汇总
    print(f"\n【文化指标】")
    cultural = final_data.get('cultural_indicators', {})
    print(f"  意识形态: {cultural.get('ideology_content', 'unknown')}")
    print(f"  文化霸权: {cultural.get('hegemony_strength', 0):.2%}")
    print(f"  合法性: {cultural.get('legitimacy', 0):.2%}")
    print(f"  阶级意识: {cultural.get('avg_class_consciousness', 0):.2%}")

    # 跃迁历史
    print(f"\n【社会演进历史】")
    stages_seen = []
    for h in history:
        stage = h.get('social_stage', 'unknown')
        if stage not in stages_seen:
            stages_seen.append(stage)
            cn_stage = stage_names.get(stage, stage)
            print(f"  Step {h.get('step', '?')}: {cn_stage}")

    print()


def _plot_results(history: list):
    """绘制结果图表（中文标签）"""
    if not history:
        return

    steps = [h['step'] for h in history]
    population = [h['total_population'] for h in history]
    subsistence = [h['average_subsistence'] for h in history]

    # 提取经济指标历史
    rates_of_profit = []
    surplus_rates = []
    for h in history:
        econ = h.get('economic_metrics', {})
        rates_of_profit.append(econ.get('rate_of_profit', 0))
        surplus_rates.append(econ.get('rate_of_surplus_value', 0))

    # 提取人口动态历史
    birth_rates = [h.get('population_dynamics', {}).get('birth_rate', 0) for h in history]
    death_rates = [h.get('population_dynamics', {}).get('death_rate', 0) for h in history]
    growth_rates = [h.get('population_dynamics', {}).get('growth_rate', 0) for h in history]

    # 提取政治文化指标历史
    legitimacy_history = [h.get('cultural_indicators', {}).get('legitimacy', 0) for h in history]
    hegemony_history = [h.get('cultural_indicators', {}).get('hegemony_strength', 0) for h in history]

    fig, axes = plt.subplots(3, 2, figsize=(16, 14))

    # 中文阶级名称映射
    class_names_cn = {
        'forager': '采集者',
        'tribe_member': '部落成员',
        'worker': '工人',
        'capitalist': '资本家',
        'slave': '奴隶',
        'slave_owner': '奴隶主',
        'serf': '农奴',
        'lord': '领主',
    }

    # 中文社会关系名称映射
    relation_names_cn = {
        'kinship': '血缘关系',
        'clan': '氏族关系',
        'barter': '物物交换',
        'enslavement': '奴役关系',
        'feudal_rent': '封建地租',
        'wage_contract': '雇佣关系',
        'residence': '地缘关系',
    }

    # 1. 人口变化
    ax1 = axes[0, 0]
    ax1.plot(steps, population, 'b-', linewidth=2)
    ax1.set_xlabel('步数 (Step)')
    ax1.set_ylabel('人口 (Population)')
    ax1.set_title('人口变化\nPopulation Over Time')
    ax1.grid(True, alpha=0.3)

    # 2. 生存资料满足率
    ax2 = axes[0, 1]
    ax2.plot(steps, subsistence, 'g-', linewidth=2)
    ax2.set_xlabel('步数 (Step)')
    ax2.set_ylabel('满足率 (Satisfaction)')
    ax2.set_title('平均生存资料满足率\nAverage Subsistence Satisfaction')
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3)

    # 3. 阶级分布变化
    ax3 = axes[1, 0]
    class_names = ['forager', 'tribe_member', 'slave', 'slave_owner', 'serf', 'lord', 'worker', 'capitalist']
    for cls in class_names:
        values = [h.get('class_distribution', {}).get(cls, 0) for h in history]
        if any(v > 0 for v in values):
            cn_name = class_names_cn.get(cls, cls)
            ax3.plot(steps, values, label=cn_name, linewidth=2)
    ax3.set_xlabel('步数 (Step)')
    ax3.set_ylabel('人数 (Count)')
    ax3.set_title('阶级分布变化\nClass Distribution Over Time')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)

    # 4. 经济指标
    ax4 = axes[1, 1]
    ax4.plot(steps, rates_of_profit, 'r-', label='利润率 p\'', linewidth=2)
    ax4.plot(steps, surplus_rates, 'm--', label='剩余价值率 s/v', linewidth=2)
    ax4.set_xlabel('步数 (Step)')
    ax4.set_ylabel('比率 (Rate)')
    ax4.set_title('经济指标\nEconomic Indicators')
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)

    # 5. 人口动态
    ax5 = axes[2, 0]
    ax5.plot(steps, birth_rates, 'g-', label='出生率', linewidth=2)
    ax5.plot(steps, death_rates, 'r--', label='死亡率', linewidth=2)
    ax5.plot(steps, growth_rates, 'b-.', label='增长率', linewidth=2)
    ax5.set_xlabel('步数 (Step)')
    ax5.set_ylabel('比率 (Rate)')
    ax5.set_title('人口动态\nPopulation Dynamics')
    ax5.legend(loc='upper right')
    ax5.grid(True, alpha=0.3)

    # 6. 政治文化指标
    ax6 = axes[2, 1]
    ax6.plot(steps, legitimacy_history, 'b-', label='合法性', linewidth=2)
    ax6.plot(steps, hegemony_history, 'r--', label='文化霸权', linewidth=2)
    ax6.set_xlabel('步数 (Step)')
    ax6.set_ylabel('强度 (Strength)')
    ax6.set_title('政治文化指标\nPolitical-Cultural Indicators')
    ax6.set_ylim(0, 1.1)
    ax6.legend(loc='upper right')
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('simulation_results.png', dpi=150)
    print(f"\n图表已保存到 simulation_results.png")


def create_demo_seed_model():
    """创建演示种子模型 - 用于演示完整社会演进

    设置较高的初始人口和合理的Agent比例，以便快速演示所有阶段。
    """
    model = CapitalModel(
        width=100,
        height=100,
        num_foragers=80,      # 较多的采集者
        num_tribe_members=120,  # 较多的部落成员（会促进向部落阶段过渡）
        num_farmers=20        # 一些农民（促进定居和农业发展）
    )
    return model


def run_interactive_demo(interval: int = 20):
    """交互式演示模式

    支持暂停/继续/快进等操作。
    按 Q 退出。
    """
    import sys
    import time
    import os

    print("=" * 80)
    print("           CapitalSimulator 交互式演示模式")
    print("=" * 80)
    print("操作说明:")
    print("  [P] - 暂停/继续")
    print("  [S] - 快进到下一阶段")
    print("  [R] - 显示详细报告")
    print("  [Q] - 退出并生成最终报告")
    print("=" * 80)

    model = create_demo_seed_model()

    # 阶段时间记录
    stage_timestamps = {}
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

    running = True
    paused = False
    old_stage = model.social_stage
    step_count = 0
    last_report_step = 0
    last_keypress_check = time.time()

    print("\n开始演示，按 P 暂停，S 快进，R 详细报告，Q 退出\n")

    while running:
        # 执行一步
        if not paused:
            old_stage = model.social_stage
            model.step()
            step_count += 1

            # 检测阶段变化
            if model.social_stage != old_stage:
                stage_timestamps[old_stage.value] = step_count
                stage_name = stage_names.get(model.social_stage.value, model.social_stage.value)
                year_str = model.get_formatted_year()
                print(f"\n{'*' * 80}")
                print(f"  【阶段跃迁】{stage_names.get(old_stage.value, old_stage.value)} -> {stage_name}")
                print(f"  到达年份: {year_str}")
                print(f"{'*' * 80}\n")

        # 显示状态栏
        current_stage_name = stage_names.get(model.social_stage.value, model.social_stage.value)
        status = "PAUSED" if paused else "RUNNING"
        year_str = model.get_formatted_year()
        print(f"\r[Step {step_count:4d}] [{status}] {year_str} | Stage: {current_stage_name} | Pop: {model.get_population_count():3d} | Subsistence: {model.get_average_subsistence():.1%}    ", end='', flush=True)

        # 每隔interval步自动显示简要报告
        if not paused and step_count - last_report_step >= interval:
            print()  # 换行
            _print_step_report(model, step_count)
            last_report_step = step_count

        # 检测键盘输入（非阻塞，兼容 Windows）
        current_time = time.time()
        if current_time - last_keypress_check > 0.1:  # 每 0.1 秒检查一次
            last_keypress_check = current_time
            key = _get_keypress_nonblocking()
            if key:
                key = key.lower()
                if key == 'q':
                    running = False
                elif key == 'p':
                    paused = not paused
                    print()  # 换行
                    print(f"[{'已暂停' if paused else '已继续'}]")
                elif key == 's':
                    print()  # 换行
                    print("[快进到下一阶段...]")
                    _force_next_stage(model)
                elif key == 'r':
                    print()  # 换行
                    _print_step_report(model, step_count)

        # 短暂休眠避免 CPU 占用 100%
        time.sleep(0.01)

    # 退出前的最终报告
    print("\n\n")
    _print_final_summary(model)
    _plot_results(model.data_collector.get_history())


def _get_keypress_nonblocking():
    """非阻塞获取键盘输入（兼容 Windows）"""
    import sys
    import time
    import os

    # Windows
    if os.name == 'nt':
        import msvcrt
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8', errors='ignore')
        return None
    # Unix/Linux/Mac
    else:
        import select
        import sys
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None


def _force_next_stage(model):
    """强制将模型推进到下一个阶段（用于演示）"""
    from src.model.social_stage import SocialStage

    current = model.social_stage

    # 强制添加相关边来触发阶段转换
    if current == SocialStage.EARLY_STATE:
        # 添加封建地租边触发封建社会
        from src.model.agents import Serf, Lord
        from src.model.relations import RelationTypes

        existing = list(model._agent_lookup.values())
        if existing:
            lord = Lord(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(lord, pos)
            lord.pos = pos
            model.social_graph.add_agent(lord.unique_id)
            model._agent_lookup[lord.unique_id] = lord

            serf = Serf(model)
            serf.lord_id = lord.unique_id
            model.space.place_agent(serf, pos)
            serf.pos = pos
            model.social_graph.add_agent(serf.unique_id)
            model._agent_lookup[serf.unique_id] = serf

            model.social_graph.add_edge(
                serf.unique_id, lord.unique_id,
                RelationTypes.FEUDAL_RENT,
                weight=1.0
            )
            print("  已添加封建地租关系，触发封建化...")

    elif current == SocialStage.FEUDAL_STATE:
        # 添加雇佣关系边触发资本主义
        from src.model.agents import Capitalist, Worker
        from src.model.relations import RelationTypes

        capitalist = Capitalist(model)
        pos = (model.random.random() * model.space.width,
               model.random.random() * model.space.height)
        model.space.place_agent(capitalist, pos)
        capitalist.pos = pos
        model.social_graph.add_agent(capitalist.unique_id)
        model._agent_lookup[capitalist.unique_id] = capitalist

        for i in range(5):
            worker = Worker(model)
            worker.employed_by = capitalist.unique_id
            model.space.place_agent(worker, pos)
            worker.pos = pos
            model.social_graph.add_agent(worker.unique_id)
            model._agent_lookup[worker.unique_id] = worker

            capitalist.workers_employed.append(worker.unique_id)

            model.social_graph.add_edge(
                worker.unique_id, capitalist.unique_id,
                RelationTypes.WAGE_CONTRACT,
                weight=1.0
            )
        print("  已添加雇佣关系，触发资本主义化...")

    elif current == SocialStage.CAPITALIST_STATE:
        # 添加计划分配边触发社会主义
        from src.model.relations import RelationTypes

        all_agents = list(model._agent_lookup.values())
        for i, agent in enumerate(all_agents[:20]):  # 限制数量
            next_agent = all_agents[(i + 1) % len(all_agents)]
            model.social_graph.add_edge(
                agent.unique_id, next_agent.unique_id,
                RelationTypes.PLANNING,
                weight=1.0
            )
        print("  已添加计划分配关系，触发社会主义化...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CapitalSimulator')
    parser.add_argument('--steps', type=int, default=200, help='模拟步数')
    parser.add_argument('--demo', action='store_true', help='交互式演示模式')
    parser.add_argument('--interval', type=int, default=20, help='演示模式输出间隔')
    args = parser.parse_args()

    if args.demo:
        run_interactive_demo(interval=args.interval)
    else:
        run_simulation(steps=args.steps)
