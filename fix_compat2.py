"""
fix_compat2.py  —  run from bci_raspy root
Fixes remaining Monitor-unwrapping issues in callbacks.py.
"""
import re, shutil
from pathlib import Path

cb = Path("SJtools/copilot/callbacks.py")
src = cb.read_text(encoding="utf-8")
original = src

# All direct env/eval_env attribute accesses that need .env. inserted.
# Pattern: self.(eval_env|env).ATTR  where ATTR is NOT already '.env.'
attrs = [
    "use_curriculum",
    "curriculum",
    "trialResults",
    "taskGame",
    "rewardClass",
    "targetSize",
    "CSvalue",
    "softmax_type",
    "holdTimeThres",
]

for attr in attrs:
    # self.eval_env.ATTR  →  self.eval_env.env.ATTR  (avoid double-patching)
    src = re.sub(
        rf'self\.eval_env\.(?!env\.)({attr})\b',
        r'self.eval_env.env.\1',
        src
    )
    # self.env.ATTR  →  self.env.env.ATTR  (avoid double-patching)
    src = re.sub(
        rf'self\.env\.(?!env\.)({attr})\b',
        r'self.env.env.\1',
        src
    )

# Also fix the TensorboardLoggerCallback.__init__ which stores env/eval_env
# and accesses taskGame directly during __init__ (not via self.env):
#   self.tickLength = self.eval_env.taskGame.tickLength
# These were already caught by 'taskGame' above.

if src != original:
    shutil.copy(cb, cb.with_suffix(".py.bak2"))
    cb.write_text(src, encoding="utf-8")
    print(f"Patched {cb}  (backup: callbacks.py.bak2)")
    # Show what changed
    import difflib
    diff = list(difflib.unified_diff(
        original.splitlines(), src.splitlines(),
        lineterm='', n=0
    ))
    for line in diff[:60]:
        print(line)
else:
    print("No changes needed.")
