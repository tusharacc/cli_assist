"""
Environment Manager for Safe Code Execution
Manages virtual environments and language-specific execution
"""

import os
import subprocess
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .debug_logger import debug_logger

console = Console()

@dataclass
class EnvironmentInfo:
    """Information about a language environment"""
    name: str
    version: str
    executable: str
    package_manager: str
    virtual_env: bool
    path: str

class EnvironmentManager:
    """Manages language environments for safe code execution"""
    
    def __init__(self):
        self.console = console
        self.environments = {}
        self.temp_dirs = []
        self._detect_environments()
    
    def _detect_environments(self):
        """Detect available language environments"""
        self.console.print("[cyan]🔍 Detecting language environments...[/cyan]")
        
        # Detect Python
        python_info = self._detect_python()
        if python_info:
            self.environments["python"] = python_info
        
        # Detect Node.js
        node_info = self._detect_nodejs()
        if node_info:
            self.environments["nodejs"] = node_info
        
        # Detect Go
        go_info = self._detect_go()
        if go_info:
            self.environments["go"] = go_info
        
        # Detect .NET
        dotnet_info = self._detect_dotnet()
        if dotnet_info:
            self.environments["dotnet"] = dotnet_info
        
        # Detect Java
        java_info = self._detect_java()
        if java_info:
            self.environments["java"] = java_info
        
        self.console.print(f"[green]✅ Detected {len(self.environments)} environments[/green]")
    
    def _detect_python(self) -> Optional[EnvironmentInfo]:
        """Detect Python environment"""
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                return EnvironmentInfo(
                    name="Python",
                    version=version,
                    executable="python3",
                    package_manager="pip",
                    virtual_env=os.environ.get("VIRTUAL_ENV") is not None,
                    path=shutil.which("python3")
                )
        except FileNotFoundError:
            pass
        
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                return EnvironmentInfo(
                    name="Python",
                    version=version,
                    executable="python",
                    package_manager="pip",
                    virtual_env=os.environ.get("VIRTUAL_ENV") is not None,
                    path=shutil.which("python")
                )
        except FileNotFoundError:
            pass
        
        return None
    
    def _detect_nodejs(self) -> Optional[EnvironmentInfo]:
        """Detect Node.js environment"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                return EnvironmentInfo(
                    name="Node.js",
                    version=version,
                    executable="node",
                    package_manager="npm",
                    virtual_env=False,  # Node.js uses nvm or similar
                    path=shutil.which("node")
                )
        except FileNotFoundError:
            pass
        
        return None
    
    def _detect_go(self) -> Optional[EnvironmentInfo]:
        """Detect Go environment"""
        try:
            result = subprocess.run(["go", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                return EnvironmentInfo(
                    name="Go",
                    version=version,
                    executable="go",
                    package_manager="go mod",
                    virtual_env=False,
                    path=shutil.which("go")
                )
        except FileNotFoundError:
            pass
        
        return None
    
    def _detect_dotnet(self) -> Optional[EnvironmentInfo]:
        """Detect .NET environment"""
        try:
            result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                return EnvironmentInfo(
                    name=".NET",
                    version=version,
                    executable="dotnet",
                    package_manager="nuget",
                    virtual_env=False,
                    path=shutil.which("dotnet")
                )
        except FileNotFoundError:
            pass
        
        return None
    
    def _detect_java(self) -> Optional[EnvironmentInfo]:
        """Detect Java environment"""
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stderr.strip().split('\n')[0]  # Java version goes to stderr
                return EnvironmentInfo(
                    name="Java",
                    version=version,
                    executable="java",
                    package_manager="maven",
                    virtual_env=False,
                    path=shutil.which("java")
                )
        except FileNotFoundError:
            pass
        
        return None
    
    def create_virtual_environment(self, language: str, name: str = None) -> Optional[str]:
        """Create a virtual environment for the specified language"""
        if language not in self.environments:
            self.console.print(f"[red]❌ Language {language} not detected[/red]")
            return None
        
        env_info = self.environments[language]
        
        if not name:
            name = f"lumos_{language}_{len(self.temp_dirs)}"
        
        try:
            # Create temporary directory for the environment
            temp_dir = tempfile.mkdtemp(prefix=f"lumos_{name}_")
            self.temp_dirs.append(temp_dir)
            
            if language == "python":
                return self._create_python_venv(temp_dir, env_info)
            elif language == "nodejs":
                return self._create_nodejs_env(temp_dir, env_info)
            elif language == "go":
                return self._create_go_env(temp_dir, env_info)
            elif language == "dotnet":
                return self._create_dotnet_env(temp_dir, env_info)
            elif language == "java":
                return self._create_java_env(temp_dir, env_info)
            else:
                self.console.print(f"[red]❌ Unsupported language: {language}[/red]")
                return None
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to create environment: {str(e)}[/red]")
            debug_logger.error(f"Failed to create environment: {e}")
            return None
    
    def _create_python_venv(self, temp_dir: str, env_info: EnvironmentInfo) -> str:
        """Create Python virtual environment"""
        venv_path = os.path.join(temp_dir, "venv")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Creating Python virtual environment", total=None)
            
            result = subprocess.run([
                env_info.executable, "-m", "venv", venv_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to create venv: {result.stderr}")
            
            progress.update(task, description="Python virtual environment created")
        
        return venv_path
    
    def _create_nodejs_env(self, temp_dir: str, env_info: EnvironmentInfo) -> str:
        """Create Node.js environment"""
        package_json_path = os.path.join(temp_dir, "package.json")
        
        # Create package.json
        package_json = {
            "name": "lumos-nodejs-env",
            "version": "1.0.0",
            "description": "Lumos Node.js environment",
            "main": "index.js",
            "scripts": {
                "start": "node index.js"
            },
            "dependencies": {}
        }
        
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        return temp_dir
    
    def _create_go_env(self, temp_dir: str, env_info: EnvironmentInfo) -> str:
        """Create Go environment"""
        go_mod_path = os.path.join(temp_dir, "go.mod")
        
        # Create go.mod
        go_mod_content = """module lumos-go-env

go 1.21

"""
        
        with open(go_mod_path, 'w') as f:
            f.write(go_mod_content)
        
        return temp_dir
    
    def _create_dotnet_env(self, temp_dir: str, env_info: EnvironmentInfo) -> str:
        """Create .NET environment"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Creating .NET project", total=None)
            
            result = subprocess.run([
                "dotnet", "new", "console", "-n", "LumosApp", "--output", temp_dir
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to create .NET project: {result.stderr}")
            
            progress.update(task, description=".NET project created")
        
        return temp_dir
    
    def _create_java_env(self, temp_dir: str, env_info: EnvironmentInfo) -> str:
        """Create Java environment"""
        # Create simple Java project structure
        src_dir = os.path.join(temp_dir, "src", "main", "java")
        os.makedirs(src_dir, exist_ok=True)
        
        # Create a simple Main.java
        main_java = os.path.join(src_dir, "Main.java")
        with open(main_java, 'w') as f:
            f.write("""public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Lumos Java environment!");
    }
}
""")
        
        return temp_dir
    
    def execute_code(self, code: str, language: str, env_path: str = None) -> Tuple[bool, str, str]:
        """Execute code in a safe environment"""
        if language not in self.environments:
            return False, "", f"Language {language} not supported"
        
        env_info = self.environments[language]
        
        try:
            if language == "python":
                return self._execute_python(code, env_path, env_info)
            elif language == "nodejs":
                return self._execute_nodejs(code, env_path, env_info)
            elif language == "go":
                return self._execute_go(code, env_path, env_info)
            elif language == "dotnet":
                return self._execute_dotnet(code, env_path, env_info)
            elif language == "java":
                return self._execute_java(code, env_path, env_info)
            else:
                return False, "", f"Unsupported language: {language}"
                
        except Exception as e:
            debug_logger.error(f"Code execution failed: {e}")
            return False, "", str(e)
    
    def _execute_python(self, code: str, env_path: str, env_info: EnvironmentInfo) -> Tuple[bool, str, str]:
        """Execute Python code"""
        if env_path:
            python_exe = os.path.join(env_path, "bin", "python")
        else:
            python_exe = env_info.executable
        
        result = subprocess.run(
            [python_exe, "-c", code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0, result.stdout, result.stderr
    
    def _execute_nodejs(self, code: str, env_path: str, env_info: EnvironmentInfo) -> Tuple[bool, str, str]:
        """Execute Node.js code"""
        # Write code to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            result = subprocess.run(
                [env_info.executable, temp_file.name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        finally:
            os.unlink(temp_file.name)
    
    def _execute_go(self, code: str, env_path: str, env_info: EnvironmentInfo) -> Tuple[bool, str, str]:
        """Execute Go code"""
        # Write code to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False)
        temp_file.write(code)
        temp_file.close()
        
        try:
            # Compile and run
            result = subprocess.run(
                [env_info.executable, "run", temp_file.name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        finally:
            os.unlink(temp_file.name)
    
    def _execute_dotnet(self, code: str, env_path: str, env_info: EnvironmentInfo) -> Tuple[bool, str, str]:
        """Execute .NET code"""
        # Write code to Program.cs
        program_cs = os.path.join(env_path, "Program.cs")
        with open(program_cs, 'w') as f:
            f.write(code)
        
        # Run the project
        result = subprocess.run(
            ["dotnet", "run"],
            cwd=env_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0, result.stdout, result.stderr
    
    def _execute_java(self, code: str, env_path: str, env_info: EnvironmentInfo) -> Tuple[bool, str, str]:
        """Execute Java code"""
        # Write code to Main.java
        main_java = os.path.join(env_path, "src", "main", "java", "Main.java")
        with open(main_java, 'w') as f:
            f.write(code)
        
        # Compile and run
        compile_result = subprocess.run(
            ["javac", main_java],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if compile_result.returncode != 0:
            return False, "", compile_result.stderr
        
        # Run the compiled class
        run_result = subprocess.run(
            ["java", "-cp", os.path.dirname(main_java), "Main"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return run_result.returncode == 0, run_result.stdout, run_result.stderr
    
    def list_environments(self) -> None:
        """List available environments"""
        self.console.print("\n[bold]Available Environments:[/bold]")
        self.console.print("=" * 50)
        
        for lang, env_info in self.environments.items():
            status = "✅ Available" if env_info.path else "❌ Not found"
            venv_status = " (Virtual)" if env_info.virtual_env else ""
            
            self.console.print(f"\n[bold]{env_info.name}[/bold]{venv_status}:")
            self.console.print(f"  Version: {env_info.version}")
            self.console.print(f"  Executable: {env_info.executable}")
            self.console.print(f"  Package Manager: {env_info.package_manager}")
            self.console.print(f"  Status: {status}")
    
    def cleanup(self) -> None:
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                debug_logger.error(f"Failed to cleanup {temp_dir}: {e}")
        
        self.temp_dirs.clear()
        self.console.print("[green]✅ Cleaned up temporary environments[/green]")

# Global environment manager instance
env_manager = EnvironmentManager()

def get_environment_manager() -> EnvironmentManager:
    """Get the global environment manager"""
    return env_manager
