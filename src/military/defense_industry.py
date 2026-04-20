"""
Defense Industry - 国防工业

Part of Department I (生产资料部类).
Produces means of destruction (not means of production).
"""

from typing import Dict


class DefenseIndustry:
    """
    国防工业 - Defense industry model.

    Defense industry is part of Department I (means of production)
    but produces for destruction rather than production.
    """

    def __init__(self):
        self.output_capacity = 100.0  # Max output per period
        self.current_output = 0.0
        self.capital_stock = 50.0
        self.organic_composition = 4.0  # c/v - higher than civilian industry

        # Inputs from Department I
        self.inputs_required = {
            'steel': 10.0,
            'chemicals': 5.0,
        }

    def produce(self, input_resources: Dict[str, float] = None) -> float:
        """
        生产军事物资 - Produce military output.

        Returns value of military output produced.
        """
        if input_resources:
            # Check if we have enough inputs
            for resource, amount in self.inputs_required.items():
                if input_resources.get(resource, 0.0) < amount:
                    # Limited production
                    self.current_output = self.output_capacity * 0.5
        else:
            self.current_output = self.output_capacity * 0.8

        # Consume constant capital
        constant_capital_consumed = self.capital_stock * 0.1
        self.capital_stock -= constant_capital_consumed

        return self.current_output

    def calculate_value_added(self) -> Dict[str, float]:
        """计算增加值"""
        return {
            'constant_capital': self.capital_stock * 0.1,
            'variable_capital': self.output_capacity * 0.2,
            'surplus_value': self.output_capacity * 0.3,
            'total_value': self.output_capacity * 0.6,
        }