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
    print("=== CapitalSimulator: 原始社会早期 ===")
    print(f"Initial setup: {num_foragers} foragers, {num_tribe_members} tribe members")
    print()

    # Create model
    model = CapitalModel(
        width=100,
        height=100,
        num_foragers=num_foragers,
        num_tribe_members=num_tribe_members
    )

    # Run simulation
    print("Running simulation...")
    for i in range(steps):
        model.step()
        if (i + 1) % 20 == 0:
            data = model.data_collector.get_latest()
            print(f"Step {i+1}: Population={data['total_population']}, "
                  f"Subsistence={data['average_subsistence']:.2f}")

    print()
    print("Simulation complete!")

    # Display results
    _plot_results(model.data_collector.get_history())

    return model


def _plot_results(history: list):
    """绘制结果图表"""
    if not history:
        return

    steps = [h['step'] for h in history]
    population = [h['total_population'] for h in history]
    subsistence = [h['average_subsistence'] for h in history]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.plot(steps, population, 'b-', linewidth=2)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Population')
    ax1.set_title('Population Over Time')
    ax1.grid(True)

    ax2.plot(steps, subsistence, 'g-', linewidth=2)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Subsistence Satisfaction')
    ax2.set_title('Average Subsistence Satisfaction')
    ax2.set_ylim(0, 1.1)
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig('simulation_results.png')
    print("Results saved to simulation_results.png")


if __name__ == "__main__":
    run_simulation(steps=100)
