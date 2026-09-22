"""bash工具"""
import subprocess

from .. import config


DEFINITION = {
    "name" : "bash",
    "description" : "Run a shell command.",
    "input_schema" : {
        "type" : "object",
        "properties" : {"command" : {"type" : "string"}},
        "required" : ["command"]
    }
}

def run_bash(command : str) -> str:
    try:
        result = subprocess.run(
            command,
            shell = True,
            cwd = config.WORKDIR,
            capture_output=True,#抓住stdout/stderr 不打印到终端
            text = True,#字节自动解码成str
            errors="replace",
            timeout=120
        )

        output = (result.stdout + result.stderr).strip()
        return output[:50000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error : Timeout (120s)"



def register(registry) -> None:
    registry.register(DEFINITION, run_bash)