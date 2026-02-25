"""
配置管理模块
负责加载、保存和管理系统配置
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "user_data_dir": "",  # 浏览器用户数据目录（必填）
    "extensions": [],     # 浏览器扩展列表
    "ollama_api": "http://127.0.0.1:11434",  # Ollama API地址
    "ollama_model": "llama3.2",  # Ollama模型名称
    "auto_open_browser": True,  # 自动打开浏览器偏好
    "headless_mode": False,  # 无头模式（后台运行）
    "first_run": True,  # 首次运行标志
    "api_port": 8765,  # API服务端口
    "mcp_port": 8000,  # MCP服务端口
    "max_text_length": 12000,  # 最大文本长度（摘要）
    "max_extract_length": 15000,  # 最大提取长度
}

CONFIG_FILE = Path(__file__).parent / "config.json"


def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    返回:
        配置字典，如果文件不存在则返回默认配置
    """
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"配置文件加载成功: {CONFIG_FILE}")
                return {**DEFAULT_CONFIG, **config}  # 用文件配置覆盖默认值
        else:
            logger.info("配置文件不存在，使用默认配置")
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """
    保存配置文件
    
    参数:
        config: 配置字典
        
    返回:
        保存是否成功
    """
    try:
        # 确保只保存必要的配置项
        config_to_save = {}
        for key in DEFAULT_CONFIG.keys():
            if key in config:
                config_to_save[key] = config[key]
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置文件保存成功: {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        return False


def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新配置
    
    参数:
        updates: 要更新的配置项
        
    返回:
        更新后的完整配置
    """
    config = load_config()
    config.update(updates)
    save_config(config)
    return config


def get_user_data_dir() -> Optional[Path]:
    """
    获取用户数据目录路径
    
    返回:
        Path对象或None（如果未配置）
    """
    config = load_config()
    user_data_dir = config.get("user_data_dir")
    if user_data_dir and os.path.exists(user_data_dir):
        return Path(user_data_dir)
    return None


def get_extensions() -> List[str]:
    """
    获取浏览器扩展列表
    
    返回:
        扩展路径列表
    """
    config = load_config()
    extensions = config.get("extensions", [])
    # 过滤掉不存在的扩展路径
    return [ext for ext in extensions if os.path.exists(ext)]


def get_ollama_config() -> Dict[str, str]:
    """
    获取Ollama配置
    
    返回:
        包含API地址和模型的字典
    """
    config = load_config()
    return {
        "api_url": config.get("ollama_api", "http://127.0.0.1:11434"),
        "model": config.get("ollama_model", "llama3.2")
    }


def is_first_run() -> bool:
    """
    检查是否是首次运行
    
    返回:
        是否是首次运行
    """
    config = load_config()
    return config.get("first_run", True)


def set_first_run_completed():
    """
    标记首次运行已完成
    """
    update_config({"first_run": False})


def get_auto_open_browser() -> bool:
    """
    获取自动打开浏览器偏好
    
    返回:
        是否自动打开浏览器
    """
    config = load_config()
    return config.get("auto_open_browser", True)


def set_auto_open_browser(value: bool):
    """
    设置自动打开浏览器偏好
    
    参数:
        value: 是否自动打开浏览器
    """
    update_config({"auto_open_browser": value})




def get_headless_mode() -> bool:
    """
    获取无头模式设置
    
    返回:
        是否启用无头模式
    """
    config = load_config()
    return config.get("headless_mode", False)


def set_headless_mode(value: bool):
    """
    设置无头模式
    
    参数:
        value: 是否启用无头模式
    """
    update_config({"headless_mode": value})


def get_api_port() -> int:
    """
    获取API服务端口
    
    返回:
        端口号
    """
    config = load_config()
    return config.get("api_port", 8765)


def get_mcp_port() -> int:
    """
    获取MCP服务端口
    
    返回:
        端口号
    """
    config = load_config()
    return config.get("mcp_port", 8000)


def get_max_text_length() -> int:
    """
    获取最大文本长度
    
    返回:
        最大字符数
    """
    config = load_config()
    return config.get("max_text_length", 12000)


def get_max_extract_length() -> int:
    """
    获取最大提取长度
    
    返回:
        最大字符数
    """
    config = load_config()
    return config.get("max_extract_length", 15000)


def validate_config() -> Dict[str, List[str]]:
    """
    验证配置的有效性
    
    返回:
        包含错误和警告的字典
    """
    config = load_config()
    errors = []
    warnings = []
    
    # 检查用户数据目录
    user_data_dir = config.get("user_data_dir")
    if not user_data_dir:
        errors.append("用户数据目录未配置")
    elif not os.path.exists(user_data_dir):
        warnings.append(f"用户数据目录不存在: {user_data_dir}")
    
    # 检查扩展
    extensions = config.get("extensions", [])
    for ext in extensions:
        if not os.path.exists(ext):
            warnings.append(f"扩展路径不存在: {ext}")
    
    # 检查Ollama配置
    ollama_api = config.get("ollama_api")
    if not ollama_api.startswith("http"):
        warnings.append(f"Ollama API地址格式可能不正确: {ollama_api}")
    
    return {"errors": errors, "warnings": warnings}


def create_example_config():
    """
    创建示例配置文件
    """
    example_config = {
        "user_data_dir": "C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data",
        "extensions": [
            "C:\\path\\to\\uBlock-Origin",
            "C:\\path\\to\\other-extension"
        ],
        "ollama_api": "http://127.0.0.1:11434",
        "ollama_model": "llama3.2",
        "auto_open_browser": True,
        "first_run": True,
        "api_port": 8765,
        "mcp_port": 8000,
        "max_text_length": 12000,
        "max_extract_length": 15000
    }
    
    example_file = Path(__file__).parent / "config.example.json"
    try:
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        logger.info(f"示例配置文件创建成功: {example_file}")
    except Exception as e:
        logger.error(f"创建示例配置文件失败: {e}")


# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)