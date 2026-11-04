"""
Package executable entrypoint for school_fee_system.
Allows running with:
  python -m school_fee_system            (launches interactive menu)
  python -m school_fee_system <command>  (runs specific CLI command)
"""

import os
import sys

# Ensure project root is available for imports
curr = os.path.dirname(os.path.abspath(__file__))
proj_root = os.path.dirname(os.path.dirname(curr))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        try:
            from main import interactive_menu
            interactive_menu()
        except ImportError:
            from school_fee_system.cli import main as cli_main
            cli_main()
    else:
        from school_fee_system.cli import main as cli_main
        cli_main()
