import enum
from typing import Optional

import typer

import np_envs

app = typer.Typer()

class EnvType(enum.Enum):
    conda = 'conda'
    venv = 'venv'

@app.command()
def update(env_name: str, env_type: EnvType, python_version: Optional[str] = None) -> None:
    """Update ENV_NAME, e.g. np_pipeline_qc"""
    env = getattr(np_envs, env_type.value)
    env(env_name, python_version=python_version).update()
    
@app.command()
def activate(env_name: str, env_type: EnvType, python_version: Optional[str] = None):
    env = getattr(np_envs, env_type.value)
    print(env(env_name, python_version=python_version).activate_path)
    
@app.command()
def python(env_name: str, env_type: EnvType, python_version: Optional[str] = None):
    env = getattr(np_envs, env_type.value)
    print(env(env_name, python_version=python_version).python)

def main():
    app()
    
if __name__ == '__main__':
    main()