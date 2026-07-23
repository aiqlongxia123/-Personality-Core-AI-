"""
统一的配置管理 — 从环境变量 + pyproject.toml 读取。
所有可配置项集中在这里，避免散落在各处 os.getenv()。
"""
import os
from pathlib import Path
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ProjectSettings(BaseSettings):
    """项目根目录配置"""
    project_root: Path = Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class APIKeyConfig(BaseSettings):
    """API Key 配置"""
    key: str = Field(..., min_length=16)

    model_config = SettingsConfigDict(
        env_prefix="PERSONALITY_API_KEY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class OllamaConfig(BaseSettings):
    """Ollama LLM 配置"""
    host: str = Field(default="http://localhost:11434")
    model_name: str = Field(default="llama3.2:3b")
    timeout: int = Field(default=30, ge=5)

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO")
    format: str = Field(
        default="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_path: str = Field(default="./logs/personality_core.log")

    model_config = SettingsConfigDict(
        env_prefix="LOGGING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class MemoryDBConfig(BaseSettings):
    """记忆数据库配置"""
    data_dir: str = Field(default="./memory_data")
    db_name: str = Field(default="memory.db")
    wal_mode: bool = Field(default=True)
    journal_mode: str = Field(default="WAL")

    model_config = SettingsConfigDict(
        env_prefix="MEMORY_DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class SessionConfig(BaseSettings):
    """会话管理配置"""
    ttl_seconds: int = Field(default=3600)
    max_sessions: int = Field(default=50)

    model_config = SettingsConfigDict(
        env_prefix="SESSION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RateLimitConfig(BaseSettings):
    """速率限制配置"""
    window_seconds: int = Field(default=60)
    max_requests: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class SanitizationConfig(BaseSettings):
    """输入过滤配置"""
    max_input_length: int = Field(default=2000, ge=100)
    enabled: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="SANITIZATION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def setup_logging(log_config: LoggingConfig) -> logging.Logger:
    """初始化全局日志系统"""
    logger = logging.getLogger("personality_core")
    logger.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
    
    if logger.handlers:
        return logger
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_config.format))
    logger.addHandler(console_handler)
    
    # 文件处理器
    try:
        log_file = Path(log_config.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_config.format))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"日志文件创建失败，仅使用控制台输出: {e}")
    
    return logger


def load_settings() -> dict:
    api_key = APIKeyConfig()
    if not api_key.key or len(api_key.key) < 16:
        raise RuntimeError(
            "环境变量 PERSONALITY_API_KEY 未设置或长度不足 16 位"
        )
    
    settings = {
        "project": ProjectSettings(),
        "api_key": api_key,
        "ollama": OllamaConfig(),
        "logging": LoggingConfig(),
        "memory_db": MemoryDBConfig(),
        "session": SessionConfig(),
        "rate_limit": RateLimitConfig(),
        "sanitization": SanitizationConfig(),
    }
    
    settings["logger"] = setup_logging(settings["logging"])
    return settings


def get_logger() -> logging.Logger:
    """获取全局 logger（延迟初始化）"""
    return setup_logging(LoggingConfig())
