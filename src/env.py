import sys
from pathlib import Path

from environs import Env

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    env_dir = Path(getattr(sys, "_MEIPASS"))
else:
    env_dir = Path.cwd()

ENV = Env()
ENV.read_env(str(env_dir.joinpath("app.env")))