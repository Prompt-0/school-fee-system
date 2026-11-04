"""
Unit tests for the Real Terminal Sandbox (web_terminal engine & CLI execution).
"""

import os
import unittest

from web_terminal.shell import RealTerminalEngine, TerminalShell


class TestRealTerminalEngine(unittest.TestCase):
    def setUp(self):
        # Point to the actual project repository
        self.engine = RealTerminalEngine()

    def test_help_command(self):
        res = self.engine.execute("help")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("STUDENT LAB CHEATSHEET", res["output"])
        self.assertIn("python -m school_fee_system", res["output"])

    def test_ls_and_pwd(self):
        res_ls = self.engine.execute("ls")
        self.assertEqual(res_ls["exit_code"], 0)
        self.assertIn("pyproject.toml", res_ls["output"])
        self.assertIn("README.md", res_ls["output"])

        res_pwd = self.engine.execute("pwd")
        self.assertEqual(res_pwd["exit_code"], 0)
        self.assertIn(self.engine.project_root, res_pwd["output"])

    def test_cd_navigation(self):
        res_cd = self.engine.execute("cd src")
        self.assertEqual(res_cd["exit_code"], 0)
        self.assertEqual(self.engine.get_display_path(), "~/school-fee-system/src")

        # cd back to root
        res_back = self.engine.execute("cd ~")
        self.assertEqual(res_back["exit_code"], 0)
        self.assertEqual(self.engine.get_display_path(), "~/school-fee-system")

    def test_python_cli_help(self):
        res = self.engine.execute("python -m school_fee_system --help")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("School Student Fee Management System", res["output"])
        self.assertIn("students", res["output"])
        self.assertIn("invoices", res["output"])

    def test_python_cli_students_list(self):
        res = self.engine.execute("python -m school_fee_system students list")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("Aarav Sharma", res["output"])
        self.assertIn("Class 10-A", res["output"])

    def test_python_cli_defaulters(self):
        res = self.engine.execute("python -m school_fee_system defaulters")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("DEFALUTERS LIST", res["output"])

    def test_python_inline_code(self):
        res = self.engine.execute('python -c "print(40 + 2)"')
        self.assertEqual(res["exit_code"], 0)
        self.assertEqual(res["output"].strip(), "42")

    def test_plain_python_returns_friendly_repl_guide(self):
        res = self.engine.execute("python")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("Interactive Python Mode Tip", res["output"])

    def test_safety_filter_blocks_destructive_commands(self):
        res_sudo = self.engine.execute("sudo rm -rf /")
        self.assertEqual(res_sudo["exit_code"], 126)
        self.assertIn("Permission denied", res_sudo["output"])

    def test_banner_command(self):
        res = self.engine.execute("banner")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("DELHI PUBLIC ACADEMY", res["output"])


if __name__ == "__main__":
    unittest.main()
