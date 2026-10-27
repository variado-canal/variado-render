#!/usr/bin/env python3
"""Isolated 30 FPS Remotion runner. The checked-out repository is ephemeral."""
import pathlib,subprocess,sys,os
job,out=sys.argv[1:3]
root=pathlib.Path("remotion/src/Root.tsx")
src=root.read_text(encoding="utf-8")
assert "const FPS = 60;" in src, "Unexpected original FPS configuration"
root.write_text(src.replace("const FPS = 60;","const FPS = 30;"),encoding="utf-8")
try:
    subprocess.run([sys.executable,"render_remotion.py",job,out],check=True,env=os.environ.copy())
finally:
    root.write_text(src,encoding="utf-8")
