#!/usr/bin/env python3
"""
CogniFusion 主程序入口
智能融合研究助手系统 - 将 AI 从被动的信息"总结者"转变为主动的、像人类一样思考的"研究员"
"""
import asyncio
import logging
import sys
import os
from pathlib import Path
import argparse
import webbrowser
import time

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from api import run_api_server
    from mcp_server import run_mcp_server
    from config import (
        load_config, is_first_run, get_api_port, get_mcp_port,
        get_auto_open_browser, set_first_run_completed
    )
except ImportError as e:
    print(f"导入模块失败: {e}")
    print(f"当前 Python 路径: {sys.path}")
    raise

logger = logging.getLogger(__name__)


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('cognifusion.log', encoding='utf-8')
        ]
    )


def print_banner():
    """打印项目横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🧠  C O G N I F U S I O N  -  智 能 融 合 研 究 助 手      ║
    ║                                                              ║
    ║   将 AI 从被动的信息"总结者"转变为主动的、像人类一样思考的"研究员"  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    【核心功能】
    • 零成本数据源：使用真实浏览器环境，复用用户登录状态
    • 双层思考模型：本地副脑+ 云端主脑（API调用）
    • 人类化探索逻辑：完美复刻人类研究员工作流
    • 隐私保护：敏感文本在本地处理，不上传云端
    
    【MCP 工具】
    1. search(query, max_results=10) - 网络搜索
    2. summarize_urls(urls) - 网页批量摘要
    3. ask_specific_question(url, keyword) - 关键词精准提取
    4. research_topic(topic, depth='medium') - 研究主题
    5. compare_sources(urls, aspect='主要内容') - 多源对比
    6. get_system_status() - 获取系统状态
    """
    print(banner)


async def check_dependencies():
    """检查依赖"""
    logger.info("检查系统依赖...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        logger.error("需要 Python 3.8 或更高版本")
        return False
    
    # 检查必要模块
    try:
        import fastapi
        import playwright
        import httpx
        import uvicorn
        logger.info("✓ 核心依赖检查通过")
        return True
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        return False


async def start_services():
    """启动所有服务"""
    config = load_config()
    api_port = get_api_port()
    mcp_port = get_mcp_port()
    
    logger.info(f"启动 CogniFusion 服务...")
    logger.info(f"API 服务端口: {api_port}")
    logger.info(f"MCP 服务端口: {mcp_port}")
    
    # 检查是否是首次运行
    if is_first_run():
        logger.info("检测到首次运行，请先完成配置")
        print("\n" + "="*60)
        print("首次运行提示:")
        print("1. 系统将在浏览器中打开配置页面")
        print("2. 请配置浏览器用户数据目录（必填）")
        print("3. 可选配置 Ollama 和浏览器扩展")
        print("="*60 + "\n")
        
        # 等待用户确认
        input("按 Enter 键继续...")
    
    # 启动 API 服务（在子进程中）
    import subprocess
    import threading
    
    def run_api():
        """运行 API 服务"""
        try:
            run_api_server(port=api_port)
        except Exception as e:
            logger.error(f"API 服务启动失败: {e}")
    
    def run_mcp():
        """运行 MCP 服务"""
        try:
            run_mcp_server()
        except Exception as e:
            logger.error(f"MCP 服务启动失败: {e}")
    
    # 启动 API 服务线程
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # 等待 API 服务启动
    logger.info("等待 API 服务启动...")
    time.sleep(3)
    
    # 启动 MCP 服务线程
    mcp_thread = threading.Thread(target=run_mcp, daemon=True)
    mcp_thread.start()
    
    # 等待 MCP 服务启动
    logger.info("等待 MCP 服务启动...")
    time.sleep(2)
    
    # 打开浏览器
    if get_auto_open_browser():
        url = f"http://127.0.0.1:{api_port}"
        logger.info(f"在浏览器中打开: {url}")
        webbrowser.open(url)
    
    # 标记首次运行已完成
    if is_first_run():
        set_first_run_completed()
        logger.info("首次运行配置已完成")
    
    logger.info("✅ CogniFusion 服务启动完成！")
    print("\n" + "="*60)
    print("服务状态:")
    print(f"• API 服务: http://127.0.0.1:{api_port}")
    print(f"• MCP 服务: SSE 传输协议 (端口: {mcp_port})")
    print(f"• 状态页面: http://127.0.0.1:{api_port}/")
    print(f"• 配置页面: http://127.0.0.1:{api_port}/config")
    print("="*60)
    print("\n按 Ctrl+C 停止服务\n")
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务运行错误: {e}")
    
    logger.info("CogniFusion 服务已停止")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CogniFusion - 智能融合研究助手系统")
    parser.add_argument("--serve", action="store_true", help="启动 API 服务")
    parser.add_argument("--mcp", action="store_true", help="启动 MCP 服务")
    parser.add_argument("--config", action="store_true", help="打开配置页面")
    parser.add_argument("--port", type=int, help="API 服务端口")
    parser.add_argument("--mcp-port", type=int, help="MCP 服务端口")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 打印横幅
    print_banner()
    
    # 检查依赖
    if not asyncio.run(check_dependencies()):
        sys.exit(1)
    
    # 根据参数选择模式
    if args.serve:
        # 只启动 API 服务
        port = args.port or get_api_port()
        logger.info(f"启动 API 服务 (端口: {port})")
        run_api_server(port=port)
    elif args.mcp:
        # 只启动 MCP 服务
        mcp_port = args.mcp_port or get_mcp_port()
        logger.info(f"启动 MCP 服务 (端口: {mcp_port})")
        run_mcp_server()
    elif args.config:
        # 打开配置页面
        port = args.port or get_api_port()
        url = f"http://127.0.0.1:{port}/config"
        logger.info(f"打开配置页面: {url}")
        webbrowser.open(url)
    else:
        # 完整模式：启动所有服务
        asyncio.run(start_services())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        sys.exit(1)