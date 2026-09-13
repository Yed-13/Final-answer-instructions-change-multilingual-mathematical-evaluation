"""Regenerate saved-response analyses and publication tables."""
import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
for name in ['analyse_focused_study.py','analyse_format_followup.py','analyse_revision.py','analyse_replication.py','independent_pair_check.py','render_focused_tables.py','plot_focused_study.py','render_revision.py','render_replication.py']:
 result=subprocess.run([sys.executable,str(R/'analysis'/name)],cwd=R,capture_output=True,text=True)
 if result.returncode:
  print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
 print('Completed',name)
print('Results: audit/; tables and figures: manuscript/')
