"""
Unit tests for the Stateful Real Terminal Sandbox (Bash, Python REPL, and Interactive Menu).
"""

import os
import unittest

from web_terminal.shell import RealTerminalEngine, TerminalShell


class TestRealTerminalEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RealTerminalEngine()

    def test_help_command(self):
        res = self.engine.execute("help")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("STUDENT LAB CHEATSHEET", res["output"])
        self.assertIn("python main.py", res["output"])

    def test_ls_and_pwd(self):
        res_ls = self.engine.execute("ls")
        self.assertEqual(res_ls["exit_code"], 0)
        self.assertIn("main.py", res_ls["output"])
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

    def test_python_interactive_repl(self):
        # 1. Enter REPL
        res_enter = self.engine.execute("python")
        self.assertEqual(res_enter["exit_code"], 0)
        self.assertIn("Python 3.12", res_enter["output"])
        self.assertEqual(res_enter["prompt"]["path"], ">>>")

        # 2. Assign variable
        res_assign = self.engine.execute("val = 15 * 4")
        self.assertEqual(res_assign["exit_code"], 0)

        # 3. Evaluate expression
        res_eval = self.engine.execute("val + 2")
        self.assertEqual(res_eval["exit_code"], 0)
        self.assertIn("62", res_eval["output"])

        # 4. Exit REPL
        res_exit = self.engine.execute("exit()")
        self.assertEqual(res_exit["exit_code"], 0)
        self.assertIn("Exited Python REPL", res_exit["output"])
        self.assertEqual(res_exit["prompt"]["symbol"], "$")

    def test_python_main_py_interactive_menu(self):
        # 1. Launch interactive console
        res_launch = self.engine.execute("python main.py")
        self.assertEqual(res_launch["exit_code"], 0)
        self.assertIn("INTERACTIVE SCHOOL FEE CONSOLE", res_launch["output"])
        self.assertIn("List All Enrolled Students", res_launch["output"])
        self.assertEqual(self.engine.mode, "menu")

        # 2. Select option 1 (List Students)
        res_students = self.engine.execute("1")
        self.assertEqual(res_students["exit_code"], 0)
        self.assertIn("ENROLLED SCHOLARS", res_students["output"])
        self.assertIn("Aarav Sharma", res_students["output"])

        # 3. Select option 4 (Defaulters)
        res_defaulters = self.engine.execute("4")
        self.assertEqual(res_defaulters["exit_code"], 0)
        self.assertIn("OVERDUE FEE DEFAULTERS", res_defaulters["output"])

        # 4. Test payment sub-flow
        res_pay1 = self.engine.execute("3")
        self.assertEqual(self.engine.mode, "menu_pay_step1")
        res_pay2 = self.engine.execute("1")
        self.assertEqual(self.engine.mode, "menu_pay_step2")
        res_pay3 = self.engine.execute("2500")
        self.assertEqual(self.engine.mode, "menu_pay_step3")
        res_pay4 = self.engine.execute("UPI")
        self.assertIn("PAYMENT RECORDED SUCCESSFULLY", res_pay4["output"])
        self.assertEqual(self.engine.mode, "menu")

        # 5. Select option 0 (Exit)
        res_exit = self.engine.execute("0")
        self.assertEqual(res_exit["exit_code"], 0)
        self.assertIn("Exited School Fee Management Console", res_exit["output"])
        self.assertEqual(self.engine.mode, "bash")
        self.assertEqual(res_exit["prompt"]["symbol"], "$")

    def test_python_cli_students_list(self):
        res = self.engine.execute("python -m school_fee_system students list")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("Aarav Sharma", res["output"])
        self.assertIn("Class 10-A", res["output"])

    def test_python_inline_code(self):
        res = self.engine.execute('python -c "print(40 + 2)"')
        self.assertEqual(res["exit_code"], 0)
        self.assertEqual(res["output"].strip(), "42")

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
