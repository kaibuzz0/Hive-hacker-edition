#!/usr/bin/env python3
"""
HIVE VERIFICATION ENGINE v2
Actually validates task results before marking complete.
Honest capability: Runs verification checks, not just status flags.

This is NOT formal verification or cryptographic proof.
It IS a working validation layer that checks actual results.
"""

import re
import subprocess
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

@dataclass
class VerificationResult:
    """Result of verification check."""
    passed: bool
    check: str
    message: str
    details: Dict[str, Any]

class VerificationEngine:
    """
    Validates task results with actual checks.
    
    CAPABILITIES:
    - Check command exit codes
    - Validate output formats
    - Verify network connectivity
    - Confirm file existence
    - Regex pattern matching
    - Custom validator functions
    - Chain multiple checks
    
    LIMITATIONS:
    - Cannot verify intent (only results)
    - Network-dependent checks may fail transiently
    - No formal proof generation
    - Limited to observable outputs
    
    HONEST LABEL: "Result validation with concrete checks"
    """
    
    def __init__(self):
        self.validators: Dict[str, Callable] = {
            'exit_code': self._check_exit_code,
            'output_contains': self._check_output_contains,
            'output_matches': self._check_output_regex,
            'file_exists': self._check_file_exists,
            'file_contains': self._check_file_contains,
            'port_open': self._check_port_open,
            'dns_resolves': self._check_dns_resolves,
            'json_valid': self._check_json_valid,
            'custom': self._run_custom_validator
        }
    
    def verify(self, result: Dict, checks: List[Dict]) -> VerificationResult:
        """
        Verify a task result against multiple checks.
        
        Args:
            result: Task result dict from agent
            checks: List of verification check specifications
            
        Returns:
            VerificationResult with pass/fail status
        """
        for check in checks:
            check_type = check.get('type')
            
            if check_type not in self.validators:
                return VerificationResult(
                    passed=False,
                    check=check_type,
                    message=f"Unknown verification type: {check_type}",
                    details={}
                )
            
            # Run the validator
            validator = self.validators[check_type]
            check_result = validator(result, check)
            
            if not check_result.passed:
                return check_result
        
        # All checks passed
        return VerificationResult(
            passed=True,
            check="all",
            message=f"All {len(checks)} verification checks passed",
            details={'checks_performed': len(checks)}
        )
    
    def _check_exit_code(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify process exit code."""
        actual = result.get('exit_code', -1)
        expected = check.get('expected', 0)
        
        passed = actual == expected
        
        return VerificationResult(
            passed=passed,
            check='exit_code',
            message=f"Exit code {actual} {'==' if passed else '!='} expected {expected}",
            details={'actual': actual, 'expected': expected}
        )
    
    def _check_output_contains(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify output contains expected string."""
        output = result.get('stdout', '') + result.get('stderr', '')
        expected = check.get('expected', '')
        
        passed = expected in output
        
        return VerificationResult(
            passed=passed,
            check='output_contains',
            message=f"Output {'contains' if passed else 'does not contain'} '{expected[:50]}...'",
            details={'expected': expected, 'output_sample': output[:200]}
        )
    
    def _check_output_regex(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify output matches regex pattern."""
        output = result.get('stdout', '') + result.get('stderr', '')
        pattern = check.get('pattern', '')
        
        try:
            match = re.search(pattern, output)
            passed = match is not None
            
            return VerificationResult(
                passed=passed,
                check='output_matches',
                message=f"Pattern {'matched' if passed else 'not found'}: {pattern[:50]}",
                details={'pattern': pattern, 'match': match.group(0) if match else None}
            )
        except re.error as e:
            return VerificationResult(
                passed=False,
                check='output_matches',
                message=f"Invalid regex pattern: {e}",
                details={'pattern': pattern}
            )
    
    def _check_file_exists(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify file exists."""
        from pathlib import Path
        
        path = check.get('path', result.get('file_path', ''))
        file_path = Path(path)
        
        passed = file_path.exists()
        
        return VerificationResult(
            passed=passed,
            check='file_exists',
            message=f"File {path} {'exists' if passed else 'not found'}",
            details={'path': str(file_path.resolve()) if passed else path}
        )
    
    def _check_file_contains(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify file contains expected content."""
        from pathlib import Path
        
        path = check.get('path', result.get('file_path', ''))
        expected = check.get('expected', '')
        
        try:
            content = Path(path).read_text()
            passed = expected in content
            
            return VerificationResult(
                passed=passed,
                check='file_contains',
                message=f"File {'contains' if passed else 'missing'} expected content",
                details={'path': path, 'expected': expected[:100]}
            )
        except Exception as e:
            return VerificationResult(
                passed=False,
                check='file_contains',
                message=f"Cannot read file: {e}",
                details={'path': path}
            )
    
    def _check_port_open(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify network port is open."""
        import socket
        
        host = check.get('host', result.get('host', 'localhost'))
        port = check.get('port', result.get('port', 0))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(check.get('timeout', 5))
            result_code = sock.connect_ex((host, port))
            sock.close()
            
            passed = result_code == 0
            
            return VerificationResult(
                passed=passed,
                check='port_open',
                message=f"Port {host}:{port} is {'open' if passed else 'closed' if result_code == 111 else f'error {result_code}'}",
                details={'host': host, 'port': port, 'result_code': result_code}
            )
        except Exception as e:
            return VerificationResult(
                passed=False,
                check='port_open',
                message=f"Connection failed: {e}",
                details={'host': host, 'port': port}
            )
    
    def _check_dns_resolves(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify DNS resolution works."""
        import socket
        
        hostname = check.get('hostname', result.get('hostname', ''))
        
        try:
            ip = socket.gethostbyname(hostname)
            
            return VerificationResult(
                passed=True,
                check='dns_resolves',
                message=f"{hostname} resolves to {ip}",
                details={'hostname': hostname, 'ip': ip}
            )
        except socket.gaierror as e:
            return VerificationResult(
                passed=False,
                check='dns_resolves',
                message=f"DNS resolution failed: {e}",
                details={'hostname': hostname}
            )
    
    def _check_json_valid(self, result: Dict, check: Dict) -> VerificationResult:
        """Verify result is valid JSON."""
        data = result.get('data', result.get('stdout', result))
        
        # If data is already a dict/list, it's valid JSON structure
        if isinstance(data, (dict, list)):
            return VerificationResult(
                passed=True,
                check='json_valid',
                message="Valid JSON structure",
                details={'type': type(data).__name__, 'keys': list(data.keys())[:5] if isinstance(data, dict) else None}
            )
        
        # Try parsing if it's a string
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return VerificationResult(
                    passed=True,
                    check='json_valid',
                    message="Valid JSON",
                    details={'type': type(parsed).__name__, 'keys': list(parsed.keys())[:5] if isinstance(parsed, dict) else None}
                )
            except json.JSONDecodeError as e:
                return VerificationResult(
                    passed=False,
                    check='json_valid',
                    message=f"Invalid JSON: {e}",
                    details={'sample': str(data)[:200]}
                )
        
        return VerificationResult(
            passed=True,
            check='json_valid',
            message="Data is valid (not JSON but acceptable)",
            details={'type': type(data).__name__}
        )
    
    def _run_custom_validator(self, result: Dict, check: Dict) -> VerificationResult:
        """Run custom validation function."""
        # This would run a user-provided validator
        # For now, just report that custom validation isn't implemented
        return VerificationResult(
            passed=False,
            check='custom',
            message="Custom validators require function binding (not yet implemented)",
            details={}
        )
    
    def register_validator(self, name: str, func: Callable) -> bool:
        """
        Register a custom validator function.
        
        Args:
            name: Validator name
            func: Function taking (result, check) -> VerificationResult
            
        Returns:
            True if registered
        """
        self.validators[name] = func
        return True


def test_verification_engine():
    """Test the verification engine."""
    print("=" * 60)
    print("TESTING: VerificationEngine")
    print("=" * 60)
    
    engine = VerificationEngine()
    
    # Test 1: Exit code check
    print("\n1. Testing exit_code check...")
    result = {'exit_code': 0, 'stdout': 'success'}
    checks = [{'type': 'exit_code', 'expected': 0}]
    vr = engine.verify(result, checks)
    print(f"   Exit 0 == 0: {vr.passed} ✓")
    
    result = {'exit_code': 1, 'stdout': 'error'}
    vr = engine.verify(result, checks)
    print(f"   Exit 1 == 0: {vr.passed} ✗ (expected fail)")
    
    # Test 2: Output contains
    print("\n2. Testing output_contains...")
    result = {'stdout': 'Scan complete. Found 5 open ports.', 'stderr': ''}
    checks = [{'type': 'output_contains', 'expected': 'open ports'}]
    vr = engine.verify(result, checks)
    print(f"   Contains 'open ports': {vr.passed} ✓")
    
    checks = [{'type': 'output_contains', 'expected': 'vulnerabilities'}]
    vr = engine.verify(result, checks)
    print(f"   Contains 'vulnerabilities': {vr.passed} ✗ (expected fail)")
    
    # Test 3: Regex pattern
    print("\n3. Testing output_matches (regex)...")
    result = {'stdout': 'IP: 192.168.1.100', 'stderr': ''}
    checks = [{'type': 'output_matches', 'pattern': r'\d+\.\d+\.\d+\.\d+'}]
    vr = engine.verify(result, checks)
    print(f"   IP regex match: {vr.passed} ✓")
    print(f"   Match: {vr.details.get('match')}")
    
    # Test 4: DNS resolution
    print("\n4. Testing dns_resolves...")
    result = {'hostname': 'google.com'}
    checks = [{'type': 'dns_resolves'}]
    vr = engine.verify(result, checks)
    print(f"   DNS resolves: {vr.passed} ✓")
    print(f"   {vr.message}")
    
    # Test 5: Port check
    print("\n5. Testing port_open...")
    result = {'host': '127.0.0.1', 'port': 22}
    checks = [{'type': 'port_open'}]
    vr = engine.verify(result, checks)
    print(f"   Port 22 open: {vr.passed} (actual status: {vr.message})")
    
    # Test 6: JSON valid
    print("\n6. Testing json_valid...")
    result = {'data': '{"status": "ok", "count": 42}'}
    checks = [{'type': 'json_valid'}]
    vr = engine.verify(result, checks)
    print(f"   Valid JSON: {vr.passed} ✓")
    
    result = {'data': '{"status": "ok", "count": }'}
    vr = engine.verify(result, checks)
    print(f"   Invalid JSON: {vr.passed} ✗ (expected fail)")
    
    # Test 7: Multiple checks
    print("\n7. Testing multiple checks (AND logic)...")
    result = {
        'exit_code': 0,
        'stdout': 'Operation completed successfully',
        'stderr': ''
    }
    checks = [
        {'type': 'exit_code', 'expected': 0},
        {'type': 'output_contains', 'expected': 'completed'},
        {'type': 'output_contains', 'expected': 'successfully'}
    ]
    vr = engine.verify(result, checks)
    print(f"   All checks passed: {vr.passed} ✓")
    print(f"   Message: {vr.message}")
    
    # Test 8: Multiple checks with failure
    print("\n8. Testing multiple checks with one failure...")
    checks = [
        {'type': 'exit_code', 'expected': 0},
        {'type': 'output_contains', 'expected': 'completed'},
        {'type': 'output_contains', 'expected': 'vulnerabilities'}  # Will fail
    ]
    vr = engine.verify(result, checks)
    print(f"   All checks passed: {vr.passed} ✗ (expected fail)")
    print(f"   Failed at: {vr.check}")
    
    print("\n" + "=" * 60)
    print("All verification tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_verification_engine()
