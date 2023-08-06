"""
# using default python version
>>> env = EnvPath('np_pipeline_qc')
>>> env.venv.pip_cache == env.conda.pip_cache
True
>>> env.venv.python.exists()
True
>>> env.conda.python.exists()
True

# using specific python version
>>> env = EnvPath('np_pipeline_qc', python_version='4.10.5')
>>> env.conda.python.exists()
False
"""
from __future__ import annotations

import configparser
import pathlib
import subprocess
import sys

import np_config
import np_logging
import np_tools

import np_envs.config as config

logger = np_logging.getLogger(__name__)

ON_WINDOWS: bool = sys.platform == 'win32'

class EnvPython:
    
    project_root: pathlib.Path
    """Root folder for all envs for the specified project, and platform/OS."""
    python: pathlib.Path
    """Path to python interpreter in this env."""
    version: str
    """Python version in this env, e.g. '3.8.5' or '3.8.*'"""
    
    def __init__(self, project_name_or_root_path: str | pathlib.Path, python_version: str | None = None, **kwargs):
        path = pathlib.Path(project_name_or_root_path)
        if len(tuple(path.parents)) == 1:
            # not a path, just an env name
            self.project_root = config.PLATFORM_ROOT / path.name
        else:
            self.project_root = np_config.normalize_path(path)
            
        if python_version is None:
            python_version = config.PROJECT_TO_PYTHON_VERSION.get(self.name, config.DEFAULT_PYTHON_VERSION)
        assert python_version and python_version.split('.')[-1] in '*0123456789'
        self.version = python_version
        
        if not self.root.exists():
            logger.warning(f'{self!r} does not exist: build with `env.create({self.version})')
            
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.project_root})'

    @property
    def name(self) -> str:
        return self.project_root.name

    @property
    def root(self) -> pathlib.Path:
        """Root folder for this specific env (e.g. `.venv/`)."""
        return self.project_root / self.version.split('.*')[0] # can't have `*` in path
    
    def create(self, *args, **kwargs) -> None:
        raise NotImplementedError
    
    def update(self, *args, **kwargs) -> None:
        raise NotImplementedError
    
    def remove(self, *args, **kwargs) -> None:
        raise NotImplementedError
        
    def activate_shell(self, *args, **kwargs) -> None:
        raise NotImplementedError
    
class PipManaged(EnvPython):
    
    def create(self, *args, **kwargs) -> None:
        if self.python.exists():
            logger.warning(f'{self.name} {self.version} already exists at {self.root}: aborting creation.')
            return
        logger.info('Creating %s', self)
        self.run_create_cmd(*args, **kwargs)
        logger.info('Finished creating %s', self)
        self.add_pip_config()
        
    
    def run_create_cmd(self, python_version: str, *args, **kwargs) -> None:
        raise NotImplementedError
    
    @property
    def pip_ini(self) -> pathlib.Path:
        return self.root / 'pip.ini'

    @property
    def pip_cache(self) -> pathlib.Path:
        """Shared cache, across versions and across env types (not platforms)."""
        return config.ROOT / '.pip-cache'
    
    @property 
    def pip_ini_config(self) -> configparser.ConfigParser:
        pip_ini_config = configparser.ConfigParser()
        pip_ini_config.read_dict(
            config.PROJECT_TO_PIP_CONFIG.get(self.name,
            config.PROJECT_TO_PIP_CONFIG['default']),
        )
        pip_ini_config.set('global', 'cache-dir', np_config.normalize_path(self.pip_cache).as_posix())
        return pip_ini_config
    
    def add_pip_config(self):
        if not self.root.exists():
            raise FileNotFoundError(f'Cannot add pip config: {self.root} does not exist')
        if not self.pip_ini.parent.exists():
            self.pip_ini.parent.mkdir(parents=True)
        with open(self.pip_ini, 'w') as f:
            self.pip_ini_config.write(f)
        logger.debug('Pip config written to %s', self.pip_ini)

    @property
    def requirements_txt(self) -> pathlib.Path:
        """Path to requirements.txt file (may not exist)."""
        return config.REQUIREMENTS_TXT_ROOT / f'{self.name}.requirements.txt'
        
    def update(self, requirements: pathlib.Path | None = None, **kwargs) -> None:
        if not self.python.exists():
            self.create()
        if requirements is None:
            requirements = self.requirements_txt
        if not requirements.exists():
            raise FileNotFoundError(f'Cannot update {self}: {requirements} does not exist')
        logger.info('Updating %s', self)
        self.add_pip_config()
        self.run_update_cmd(requirements, **kwargs)
        logger.info('Finished updating %s', self)

    def run_update_cmd(self, requirements: pathlib.Path) -> None:
        subprocess.run(f'{self.python} -m pip install -U -r {requirements}', check=True)

    
class PipManagedConda(PipManaged):
    
    @property
    def root(self) -> pathlib.Path:
        return super().root / 'conda'
    
    @property
    def python(self) -> pathlib.Path:
        return self.root / 'python.exe' if ON_WINDOWS else self.root / 'bin' / 'python'
    
    def run_create_cmd(self, *args, **kwargs) -> None:
        subprocess.run(
            f'conda create -p {self.root} python={self.version} -y --copy --no-shortcuts {" ".join(args)}',
            check=True,
            )
    
    def remove(self) -> None:
        subprocess.run(f'conda env remove -n {self.name} --all -y', check=True)
        if self.root.exists():
            self.root.rmdir()
    
class PipManagedVenv(PipManaged):    
    
    @property
    def root(self) -> pathlib.Path:
        return super().root / '.venv'
    
    @property
    def python(self) -> pathlib.Path:
        return self.root / 'Scripts' / 'python.exe' if ON_WINDOWS else self.root / 'bin' / 'python'
    
    def run_create_cmd(self, *args, **kwargs) -> None:
        # we need a python version to create the venv
        # pyenv would be lighter weight, but it's not usually available on windows
        conda_env = PipManagedConda(self.project_root, self.version)
        if not conda_env.python.exists():
            conda_env.create('--no-default-packages')
        subprocess.run(
            f'{conda_env.python} -m venv --copies {self.root} {" ".join(args)}',
            check=True,
            )

    def activate(self) -> None:
        activation_script = self.root / ('Scripts' if ON_WINDOWS else 'bin') / 'activate_this.py'
        if not activation_script.exists():
            np_tools.copy(config.PKG_ROOT / 'assets' / activation_script.name, activation_script)
        exec(activation_script.read_text(), {'__file__': activation_script})

    @property
    def activate_path(self) -> pathlib.Path:
        if ON_WINDOWS:
            return self.root / "scripts" / "activate"
        return self.root / "bin" / "activate"

    def activate_shell(self) -> None:
        subprocess.run(self.activate_path, check=True, shell=True)

class EnvPath(pathlib.WindowsPath if ON_WINDOWS else pathlib.PosixPath): # type: ignore
    """
    >>> env = EnvPath('np_pipeline_qc')
    """

    version: str
    """Python version to used for any envs, e.g. '3.8.5' or '3.8.*'."""
    
    def __new__(cls, env_name: str, **kwargs):
        path = config.PLATFORM_ROOT / env_name
        return super().__new__(cls, path, **kwargs)
    
    def __init__(self, *args, python_version: str | None = None, **kwargs):
        if python_version is None:
            python_version = config.PROJECT_TO_PYTHON_VERSION[self.name]
        self.version = python_version
            
    def __repr__(self) -> str:
        return super().__repr__()
    
    @property
    def conda(self) -> EnvPython:
        if not hasattr(self, '_conda'):
            self._conda = PipManagedConda(self, self.version)
        return self._conda
    
    @property
    def venv(self) -> EnvPython:
        if not hasattr(self, '_venv'):
            self._venv = PipManagedVenv(self, self.version)
        return self._venv
    
    
if __name__ == '__main__':
    PipManagedVenv('np_pipeline_qc')
    import doctest
    doctest.testmod()