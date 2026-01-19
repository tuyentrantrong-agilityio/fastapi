#!/usr/bin/env python3
"""Unit tests for all hello programs in chapter_1"""

import unittest

import subprocess
import sys
import os


def run_program(filename, args=None):
    """Helper function to run a program and return result"""
    cmd = [sys.executable, filename]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, capture_output=True, text=True)


# ============================================================================
# hello01_print.py tests
# ============================================================================


def test_hello01_exists():
    """hello01_print.py file exists"""
    assert os.path.isfile("hello01_print.py")


def test_hello01_runs():
    """hello01_print.py runs without errors"""
    result = run_program("hello01_print.py")
    assert result.returncode == 0


def test_hello01_output():
    """hello01_print.py prints Hello World"""
    result = run_program("hello01_print.py")
    assert "Hello World" in result.stdout


# ============================================================================
# hello02_print.py tests
# ============================================================================


def test_hello02_exists():
    """hello02_print.py file exists"""
    assert os.path.isfile("hello02_print.py")


def test_hello02_runs():
    """hello02_print.py runs without errors"""
    result = run_program("hello02_print.py")
    assert result.returncode == 0


def test_hello02_output():
    """hello02_print.py prints Hello World"""
    result = run_program("hello02_print.py")
    assert "Hello World" in result.stdout


# ============================================================================
# hello03_shebang.py tests
# ============================================================================


def test_hello03_exists():
    """hello03_shebang.py file exists"""
    assert os.path.isfile("hello03_shebang.py")


def test_hello03_runs():
    """hello03_shebang.py runs without errors"""
    result = run_program("hello03_shebang.py")
    assert result.returncode == 0


def test_hello03_output():
    """hello03_shebang.py prints Hello World"""
    result = run_program("hello03_shebang.py")
    assert "Hello World" in result.stdout


# ============================================================================
# hello04_agr.py tests (positional argument)
# ============================================================================


def test_hello04_exists():
    """hello04_agr.py file exists"""
    assert os.path.isfile("hello04_agr.py")


def test_hello04_runs():
    """hello04_agr.py runs with positional name argument"""
    result = run_program("hello04_agr.py", ["Alice"])
    assert result.returncode == 0


def test_hello04_output():
    """hello04_agr.py prints greeting with name"""
    result = run_program("hello04_agr.py", ["Bob"])
    assert "Hello, Bob" in result.stdout


# ============================================================================
# hello05_argparse_option.py tests (optional argument)
# ============================================================================


def test_hello05_exists():
    """hello05_argparse_option.py file exists"""
    assert os.path.isfile("hello05_argparse_option.py")


def test_hello05_runs():
    """hello05_argparse_option.py runs without errors"""
    result = run_program("hello05_argparse_option.py")
    assert result.returncode == 0


def test_hello05_default_output():
    """hello05_argparse_option.py prints default greeting"""
    result = run_program("hello05_argparse_option.py")
    assert "Hello, World" in result.stdout


def test_hello05_custom_name_long_flag():
    """hello05_argparse_option.py accepts --name argument"""
    result = run_program("hello05_argparse_option.py", ["--name", "Charlie"])
    assert "Hello, Charlie" in result.stdout


def test_hello05_custom_name_short_flag():
    """hello05_argparse_option.py accepts -n argument"""
    result = run_program("hello05_argparse_option.py", ["-n", "David"])
    assert "Hello, David" in result.stdout


# ============================================================================
# hello06_main_function.py tests
# ============================================================================


def test_hello06_exists():
    """helllo06_main_function.py file exists"""
    assert os.path.isfile("helllo06_main_function.py")


def test_hello06_runs():
    """helllo06_main_function.py runs without errors"""
    result = run_program("helllo06_main_function.py")
    assert result.returncode == 0


def test_hello06_output():
    """helllo06_main_function.py prints Hello World"""
    result = run_program("helllo06_main_function.py")
    assert "Hello World" in result.stdout


# ============================================================================
# hello07_get_args.py tests
# ============================================================================


def test_hello07_exists():
    """hello07_get_args.py file exists"""
    assert os.path.isfile("hello07_get_args.py")


def test_hello07_runs():
    """hello07_get_args.py runs without errors"""
    result = run_program("hello07_get_args.py")
    assert result.returncode == 0


def test_hello07_default_output():
    """hello07_get_args.py prints default greeting"""
    result = run_program("hello07_get_args.py")
    assert "Hello, World" in result.stdout


def test_hello07_custom_name():
    """hello07_get_args.py accepts --name argument"""
    result = run_program("hello07_get_args.py", ["--name", "Eve"])
    assert "Hello, Eve" in result.stdout


# ============================================================================
# hello08_formatted.py tests
# ============================================================================


def test_hello08_exists():
    """hello08_formatted.py file exists"""
    assert os.path.isfile("hello08_formatted.py")


def test_hello08_runs():
    """hello08_formatted.py runs without errors"""
    result = run_program("hello08_formatted.py")
    assert result.returncode == 0


def test_hello08_default_output():
    """hello08_formatted.py prints default greeting with Tuyen"""
    result = run_program("hello08_formatted.py")
    assert "Hello, Tuyen" in result.stdout


def test_hello08_custom_name_short_flag():
    """hello08_formatted.py accepts -n argument"""
    result = run_program("hello08_formatted.py", ["-n", "Frank"])
    assert "Hello, Frank" in result.stdout


def test_hello08_custom_name_long_flag():
    """hello08_formatted.py accepts --name argument"""
    result = run_program("hello08_formatted.py", ["--name", "Grace"])
    assert "Hello, Grace" in result.stdout


if __name__ == "__main__":
    unittest.main()
