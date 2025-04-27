from pathlib import Path
from typing import Union
import os

class PathManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize base paths for the project."""
        self.root_dir = Path(__file__).parent.parent.absolute()
        self.data_dir = self.root_dir / 'data'
        self.models_dir = self.root_dir / 'models'
        self.config_dir = self.root_dir / 'config'
        
        # Ensure critical directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
    
    def get_path(self, *parts: Union[str, Path]) -> Path:
        """
        Get an absolute path relative to the project root.
        
        Args:
            *parts: Path parts to join with the root directory
            
        Returns:
            Path: Absolute path to the requested location
        """
        return self.root_dir.joinpath(*parts)
    
    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists and create it if it doesn't.
        
        Args:
            path: Path to the directory
            
        Returns:
            Path: Path to the created/existing directory
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def relative_to_root(self, path: Union[str, Path]) -> Path:
        """
        Convert an absolute path to a path relative to the project root.
        
        Args:
            path: Absolute path to convert
            
        Returns:
            Path: Relative path from project root
        """
        return Path(path).relative_to(self.root_dir)

# Global instance
path_manager = PathManager() 