"""
Terminology Linter - 术语扫描工具

Scans code for banned terminology (Red Line 3 enforcement).
Uses config/terminology_blacklist.yaml for the blacklist patterns.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict


class TerminologyLinter:
    """
    术语扫描器 - Scans Python files for banned terminology.

    RED LINE 3: Variables, comments, and logs must use Marxist terminology.
    """

    def __init__(self, config_path: str = None):
        self.banned_patterns: Dict[str, str] = {}
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """从 YAML 加载禁语配置"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.banned_patterns = data.get('banned_terms', {})
        except Exception:
            # Fallback: hardcoded patterns
            self.banned_patterns = {
                r'\butility\b': 'use_value',
                r'\bprofit\b': 'surplus_value',
                r'\bmoney\b': 'value_equivalent',
                r'\bprice\b': 'exchange_ratio',
                r'\bcost\b': 'c_consumed',
                r'\bhuman.capital\b': 'labor_power_quality',
            }

    def scan_file(self, filepath: str) -> List[Tuple[int, str, str]]:
        """
        扫描文件 - Scan a file for banned terminology.

        Returns list of (line_number, banned_term, suggested_replacement)
        """
        violations = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    for pattern, replacement in self.banned_patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append((i, pattern, replacement))
        except Exception:
            pass
        return violations

    def scan_directory(self, directory: str, pattern: str = "**/*.py") -> Dict[str, List]:
        """
        扫描目录 - Scan a directory for banned terminology.
        """
        results = {}
        for filepath in Path(directory).glob(pattern):
            violations = self.scan_file(str(filepath))
            if violations:
                results[str(filepath)] = violations
        return results
