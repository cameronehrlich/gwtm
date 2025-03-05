"""IDE integration utilities for Git WorkTree Manager."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List


class IDEHandler:
    """Handles opening worktrees in different IDEs."""
    
    def __init__(self, ide_paths: dict):
        self.ide_paths = ide_paths
    
    def get_ide_path(self, ide: str) -> Optional[str]:
        """Get the path to the IDE executable."""
        return self.ide_paths.get(ide.lower())
    
    def open_in_ide(self, worktree_path: str, ide: str) -> bool:
        """Open a worktree in the specified IDE."""
        ide_path = self.get_ide_path(ide)
        if not ide_path or not os.path.exists(ide_path):
            return False
            
        abs_path = os.path.abspath(worktree_path)
        
        if ide.lower() == "xcode":
            return self._open_in_xcode(abs_path, ide_path)
        elif ide.lower() == "androidstudio":
            return self._open_in_android_studio(abs_path, ide_path)
        else:
            return False
    
    def _open_in_xcode(self, path: str, ide_path: str) -> bool:
        """Open a worktree in Xcode."""
        # Make sure the path exists
        if not os.path.exists(path):
            print(f"Error: Path does not exist: {path}")
            return False
            
        # Verify the IDE path
        if not os.path.exists(ide_path):
            print(f"Error: Xcode not found at: {ide_path}")
            print(f"Check your .gwtmrc file and make sure the path is correct.")
            return False
            
        # First, check if there's a specific 'ios' directory
        ios_dir = os.path.join(path, "ios")
        if os.path.isdir(ios_dir):
            print(f"Found iOS directory at: {ios_dir}")
            search_path = ios_dir
        else:
            # If no ios directory, use the original path
            search_path = path
            
        # Look for .xcodeproj or .xcworkspace files
        xcodeproj = list(Path(search_path).glob("**/*.xcodeproj"))
        xcworkspace = list(Path(search_path).glob("**/*.xcworkspace"))
        
        if xcworkspace:
            project_path = xcworkspace[0]
            print(f"Found Xcode workspace: {project_path}")
        elif xcodeproj:
            project_path = xcodeproj[0]
            print(f"Found Xcode project: {project_path}")
        else:
            print(f"Error: No Xcode project or workspace found in {search_path}")
            return False
            
        if platform.system() == "Darwin":  # macOS
            try:
                print(f"Opening Xcode with project: {project_path}")
                result = subprocess.run(["open", "-a", ide_path, str(project_path)], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error running: open -a '{ide_path}' '{project_path}'")
                    print(f"Error output: {result.stderr}")
                    return False
                print(f"Successfully opened Xcode with project: {project_path}")
                return True
            except Exception as e:
                print(f"Exception while opening Xcode: {e}")
                return False
        else:
            print(f"Xcode is only supported on macOS")
            return False
    
    def _open_in_android_studio(self, path: str, ide_path: str) -> bool:
        """Open a worktree in Android Studio."""
        # Make sure the path exists
        if not os.path.exists(path):
            print(f"Error: Path does not exist: {path}")
            return False
            
        # Verify the IDE path
        if not os.path.exists(ide_path):
            print(f"Error: Android Studio not found at: {ide_path}")
            print(f"Check your .gwtmrc file and make sure the path is correct.")
            print(f"Current configured path: {ide_path}")
            print(f"You can create a .gwtmrc file in your home directory with:")
            print(f"[paths]")
            print(f"androidstudio = /path/to/Android Studio.app")
            return False
        
        # First, check if there's a specific 'android' directory
        android_dir = os.path.join(path, "android")
        if os.path.isdir(android_dir):
            print(f"Found Android directory at: {android_dir}")
            project_path = android_dir
        else:
            # If no android directory, use the original path
            project_path = path
            
        # Look for Android project indicators in the selected path
        gradle_files = list(Path(project_path).glob("**/build.gradle"))
        android_manifests = list(Path(project_path).glob("**/AndroidManifest.xml"))
        java_files = list(Path(project_path).glob("**/*.java"))
        kotlin_files = list(Path(project_path).glob("**/*.kt"))
        
        # Project indicators found?
        if not (gradle_files or android_manifests or java_files or kotlin_files):
            print(f"Warning: No Android project files found in {project_path}")
            print(f"Continuing anyway - Android Studio will open the directory.")
            # Continue anyway - user might know what they're doing
            
        if platform.system() == "Darwin":  # macOS
            try:
                print(f"Opening Android Studio with path: {project_path}")
                result = subprocess.run(["open", "-a", ide_path, project_path], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error running: open -a '{ide_path}' '{project_path}'")
                    print(f"Error output: {result.stderr}")
                    return False
                print(f"Successfully opened Android Studio with project: {project_path}")
                return True
            except Exception as e:
                print(f"Exception while opening Android Studio: {e}")
                return False
        elif platform.system() == "Linux":
            try:
                print(f"Opening Android Studio with path: {project_path}")
                subprocess.run([ide_path, project_path])
                print(f"Successfully opened Android Studio with project: {project_path}")
                return True
            except Exception as e:
                print(f"Exception while opening Android Studio: {e}")
                return False
        elif platform.system() == "Windows":
            try:
                print(f"Opening Android Studio with path: {project_path}")
                subprocess.run([ide_path, project_path], shell=True)
                print(f"Successfully opened Android Studio with project: {project_path}")
                return True
            except Exception as e:
                print(f"Exception while opening Android Studio: {e}")
                return False
        else:
            print(f"Unsupported operating system: {platform.system()}")
            return False
    
    @staticmethod
    def get_supported_ides() -> List[str]:
        """Get a list of supported IDEs."""
        return ["xcode", "androidstudio"]