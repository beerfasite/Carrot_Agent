import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)


#项目根目录(Carrot_Agent/),skills固定放在这里
PROJECT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_DIR / "skills"


#工作目录：agent读写文件，跑bash的根目录，默认是启动时所在目录，可用-d覆盖
WORKDIR = Path.cwd()

#不存在情况默认ds
MODEL = os.environ.get("MODEL_ID","deepseek-chat")
MAX_TOKENS = 8000


# OpenAI 兼容 client：base_url 指向目标厂商，api_key 是厂商密钥。
# 用占位 key 避免未配置 .env 时 import 就报错；真正调 API 需真实 key。
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY") or "MISSING_API_KEY",
    base_url=os.environ.get("OPENAI_BASE_URL") or None,
)


def configure_workdir(path:str | Path)->None:
    """能够修改agent的工作目录"""
    global WORKDIR
    WORKDIR = Path(path).resolve()



def data_dir()->Path:
    """所有运行时数据统一放在工作目录的 .carrot/ 下。"""
    return WORKDIR / ".carrot"




#配置在WORKDIR下面的目录
def memory_dir()->Path:
    return data_dir() / "memory"
def transcript_dir() -> Path:
    return data_dir() / "transcripts"
def tool_results_dir() -> Path:
    return data_dir() / "tool-results"
def tasks_dir() -> Path:
    return data_dir() / "tasks"










