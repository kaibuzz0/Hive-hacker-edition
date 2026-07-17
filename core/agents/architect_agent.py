#!/usr/bin/env python3
"""
HIVE SWARM - Architect Agent
Code Review & Design Approval
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class CodeReview:
    file_path: str
    issues: List[Dict]
    score: float
    approved: bool
    security_concerns: List[str]
    performance_notes: List[str]
    recommendations: List[str]

class ArchitectAgent:
    """
    Code quality and security reviewer.
    
    Responsibilities:
    - Structural integrity
    - Security vulnerabilities
    - Performance patterns
    - Maintainability
    """
    
    SECURITY_PATTERNS = {
        'eval_usage': r'\beval\s*\(',
        'exec_usage': r'\bexec\s*\(',
        'shell_injection': r'os\.system|subprocess\.call.*shell\s*=\s*True',
        'pickle_usage': r'pickle\.(load|loads)',
        'yaml_load': r'yaml\.load\s*\(',
    }
    
    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)
        
    def review_code(self, file_path: str, code: str) -> CodeReview:
        """Perform code review."""
        print(f"\n[ARCHITECT] Reviewing {file_path}...")
        
        issues = []
        score = 1.0
        security = []
        performance = []
        
        # Security checks
        for pattern_name, pattern in self.SECURITY_PATTERNS.items():
            if re.search(pattern, code):
                issues.append({
                    'type': 'security',
                    'severity': 'high',
                    'message': f"Potential security issue: {pattern_name}"
                })
                security.append(pattern_name)
                score -= 0.2
        
        # Basic structure check
        if 'def ' not in code and 'class ' not in code:
            issues.append({
                'type': 'structure',
                'severity': 'medium',
                'message': 'No functions or classes found'
            })
            score -= 0.1
        
        score = max(0.0, min(1.0, score))
        approved = score >= 0.7
        
        # Display results
        print(f"\n[CODE REVIEW] {file_path}")
        print("-" * 50)
        print(f"  Score: {score:.0%}")
        print(f"  Issues: {len(issues)}")
        if security:
            print(f"  Security: {', '.join(security)}")
        print(f"  Status: {'APPROVED' if approved else 'NEEDS_WORK'}")
        print("-" * 50)
        
        return CodeReview(
            file_path=file_path,
            issues=issues,
            score=score,
            approved=approved,
            security_concerns=security,
            performance_notes=performance,
            recommendations=["Add docstrings", "Add error handling"]
        )
    
    def suggest_refactoring(self, code: str) -> List[str]:
        """Suggest refactoring improvements."""
        suggestions = []
        
        if len(code.split('\n')) > 100:
            suggestions.append("Consider splitting into smaller functions")
        
        if code.count('try:') == 0:
            suggestions.append("Add error handling with try/except")
        
        return suggestions

def main():
    agent = ArchitectAgent()
    print("""
╔══════════════════════════════════════════╗
║  🏗️ HIVE Architect Agent                 ║
║  Code Review & Design Approval            ║
╚══════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
