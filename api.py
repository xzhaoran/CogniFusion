"""
API 服务层 (FastAPI)
提供 RESTful API 接口，集成浏览器和副脑功能
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx

from browser_core import search_bing, get_page_content, close_browser
from ollama_client import sub_brain_summarize, sub_brain_extract, test_ollama_connection
from config import (
    load_config, save_config, update_config, validate_config,
    is_first_run, set_first_run_completed, get_api_port,
    get_user_data_dir, get_extensions, get_ollama_config,
    create_example_config
)

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="CogniFusion API",
    description="智能融合研究助手系统 API",
    version="1.0.0"
)

# 创建模板目录
import os
from pathlib import Path
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)

# 创建模板引擎
templates = Jinja2Templates(directory=str(templates_dir))


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("CogniFusion API 服务启动")
    
    # 创建示例配置文件
    create_example_config()
    
    # 检查是否是首次运行
    if is_first_run():
        logger.info("首次运行检测到，需要配置")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("CogniFusion API 服务关闭")
    
    # 关闭浏览器资源
    await close_browser()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """根路径，显示状态页面"""
    config = load_config()
    
    # 验证配置
    validation = validate_config()
    
    # 测试 Ollama 连接
    ollama_status = await test_ollama_connection()
    
    context = {
        "request": request,
        "config": config,
        "validation": validation,
        "ollama_status": ollama_status,
        "is_first_run": is_first_run(),
        "api_port": get_api_port(),
        "user_data_dir": get_user_data_dir(),
        "extensions": get_extensions(),
        "ollama_config": get_ollama_config()
    }
    
    return templates.TemplateResponse("status_simple.html", context)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "CogniFusion API"}


@app.get("/bing_search")
async def bing_search(
    q: str = Query(..., description="搜索关键词"),
    max_results: int = Query(10, description="最大返回结果数", ge=1, le=50)
):
    """
    Bing 搜索接口
    
    参数:
        q: 搜索关键词
        max_results: 最大返回结果数
        
    返回:
        搜索结果列表
    """
    try:
        logger.info(f"收到搜索请求: {q}, max_results: {max_results}")
        
        results = await search_bing(q, max_results)
        
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/page_content")
async def page_content(
    url: str = Query(..., description="网页URL"),
    allow_interactive: bool = Query(True, description="是否允许交互式登录")
):
    """
    网页内容提取接口
    
    参数:
        url: 网页URL
        allow_interactive: 是否允许交互式登录
        
    返回:
        网页内容
    """
    try:
        logger.info(f"收到网页内容请求: {url}")
        
        content = await get_page_content(url, allow_interactive)
        
        return content
        
    except Exception as e:
        logger.error(f"获取网页内容失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取网页内容失败: {str(e)}")


@app.post("/sub_brain/summarize")
async def sub_brain_summarize_api(request: Dict[str, Any]):
    """
    文本摘要接口
    
    请求体:
        {
            "text": "需要摘要的文本"
        }
        
    返回:
        结构化摘要
    """
    try:
        text = request.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        logger.info(f"收到文本摘要请求，文本长度: {len(text)}")
        
        summary = await sub_brain_summarize(text)
        
        return {
            "summary": summary,
            "text_length": len(text),
            "summary_length": len(summary)
        }
        
    except Exception as e:
        logger.error(f"文本摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"文本摘要失败: {str(e)}")


@app.post("/sub_brain/extract")
async def sub_brain_extract_api(request: Dict[str, Any]):
    """
    关键词提取接口
    
    请求体:
        {
            "text": "源文本",
            "keyword": "关键词"
        }
        
    返回:
        包含关键词的原文段落
    """
    try:
        text = request.get("text", "")
        keyword = request.get("keyword", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        if not keyword:
            raise HTTPException(status_code=400, detail="关键词不能为空")
        
        logger.info(f"收到关键词提取请求，关键词: '{keyword}'，文本长度: {len(text)}")
        
        extracts = await sub_brain_extract(text, keyword)
        
        return {
            "extracts": extracts,
            "keyword": keyword,
            "text_length": len(text),
            "extracts_length": len(extracts)
        }
        
    except Exception as e:
        logger.error(f"关键词提取失败: {e}")
        raise HTTPException(status_code=500, detail=f"关键词提取失败: {str(e)}")


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """配置页面"""
    config = load_config()
    
    context = {
        "request": request,
        "config": config,
        "is_first_run": is_first_run()
    }
    
    return templates.TemplateResponse("config_simple.html", context)


@app.post("/config/save")
async def save_config_api(
    user_data_dir: str = Form(...),
    extensions: str = Form(""),
    ollama_api: str = Form("http://127.0.0.1:11434"),
    ollama_model: str = Form("llama3.2"),
    max_text_length: int = Form(12000),
    max_extract_length: int = Form(15000),
    auto_open_browser: bool = Form(True),
    headless_mode: bool = Form(False)
):
    """
    保存配置接口
    
    参数:
        user_data_dir: 用户数据目录
        extensions: 扩展路径（逗号分隔）
        ollama_api: Ollama API地址
        ollama_model: Ollama模型名称
        max_text_length: 最大文本长度（摘要）
        max_extract_length: 最大提取长度
        auto_open_browser: 自动打开浏览器偏好
        headless_mode: 无头模式（后台运行）
    """
    try:
        # 处理扩展路径（支持逗号分隔和换行分隔）
        extensions_list = []
        if extensions:
            # 先按换行分割，再按逗号分割
            lines = extensions.split('\n')
            for line in lines:
                if ',' in line:
                    # 如果一行中有逗号，按逗号分割
                    parts = line.split(',')
                    for part in parts:
                        if part.strip():
                            extensions_list.append(part.strip())
                else:
                    # 如果一行中没有逗号，直接使用整行
                    if line.strip():
                        extensions_list.append(line.strip())
        
        # 验证数值范围
        if max_text_length < 1000 or max_text_length > 200000:
            raise HTTPException(status_code=400, detail="最大文本长度应在1000-200000之间")
        if max_extract_length < 1000 or max_extract_length > 200000:
            raise HTTPException(status_code=400, detail="最大提取长度应在1000-200000之间")
        
        # 构建配置
        config_updates = {
            "user_data_dir": user_data_dir,
            "extensions": extensions_list,
            "ollama_api": ollama_api,
            "ollama_model": ollama_model,
            "max_text_length": max_text_length,
            "max_extract_length": max_extract_length,
            "auto_open_browser": auto_open_browser,
            "headless_mode": headless_mode,
            "first_run": False  # 标记首次运行已完成
        }
        
        # 保存配置
        update_config(config_updates)
        
        logger.info(f"配置保存成功，max_text_length: {max_text_length}, max_extract_length: {max_extract_length}")
        
        # 返回成功页面
        return RedirectResponse(url="/config/saved", status_code=303)
        
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@app.get("/config/saved", response_class=HTMLResponse)
async def config_saved(request: Request):
    """配置保存成功页面"""
    context = {
        "request": request,
        "config": load_config()
    }
    
    return templates.TemplateResponse("config_saved_simple.html", context)


@app.get("/status")
async def status_api():
    """系统状态接口"""
    try:
        config = load_config()
        validation = validate_config()
        ollama_status = await test_ollama_connection()
        
        return {
            "service": "CogniFusion API",
            "status": "running",
            "config": {
                "user_data_dir": config.get("user_data_dir"),
                "has_extensions": len(config.get("extensions", [])) > 0,
                "ollama_api": config.get("ollama_api"),
                "ollama_model": config.get("ollama_model")
            },
            "validation": validation,
            "ollama": ollama_status,
            "is_first_run": is_first_run()
        }
        
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return {
            "service": "CogniFusion API",
            "status": "error",
            "error": str(e)
        }


@app.get("/test/ollama")
async def test_ollama_api():
    """测试 Ollama 连接接口"""
    try:
        status = await test_ollama_connection()
        return status
    except Exception as e:
        logger.error(f"测试 Ollama 连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试 Ollama 连接失败: {str(e)}")


@app.get("/test/search")
async def test_search_api(
    q: str = Query("人工智能", description="测试搜索关键词"),
    max_results: int = Query(3, description="测试结果数")
):
    """测试搜索接口"""
    try:
        results = await search_bing(q, max_results)
        
        return {
            "test": "search",
            "query": q,
            "results": results,
            "success": True
        }
    except Exception as e:
        logger.error(f"测试搜索失败: {e}")
        return {
            "test": "search",
            "query": q,
            "success": False,
            "error": str(e)
        }


@app.get("/test/page")
async def test_page_api(
    url: str = Query("https://www.example.com", description="测试网页URL")
):
    """测试网页内容提取接口"""
    try:
        content = await get_page_content(url, allow_interactive=False)
        
        return {
            "test": "page_content",
            "url": url,
            "content_length": len(content.get("content", "")),
            "success": True
        }
    except Exception as e:
        logger.error(f"测试网页内容提取失败: {e}")
        return {
            "test": "page_content",
            "url": url,
            "success": False,
            "error": str(e)
        }


@app.post("/test/summarize")
async def test_summarize_api():
    """测试文本摘要接口"""
    try:
        # 使用示例文本
        example_text = """人工智能（AI）是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。
这些任务包括视觉感知、语音识别、决策制定和语言翻译等。AI可以分为弱人工智能和强人工智能。
弱人工智能是设计用于执行特定任务的人工智能，如语音助手或推荐系统。强人工智能是具有自我意识、
能够解决各种问题、具有学习和适应能力的人工智能系统，目前仍处于研究阶段。"""
        
        summary = await sub_brain_summarize(example_text)
        
        return {
            "test": "summarize",
            "text_length": len(example_text),
            "summary": summary,
            "success": True
        }
    except Exception as e:
        logger.error(f"测试文本摘要失败: {e}")
        return {
            "test": "summarize",
            "success": False,
            "error": str(e)
        }


@app.post("/test/extract")
async def test_extract_api():
    """测试关键词提取接口"""
    try:
        # 使用示例文本
        example_text = """机器学习是人工智能的一个子领域。机器学习算法使计算机能够从数据中学习并做出预测或决策，
而无需明确编程。深度学习是机器学习的一个分支，使用神经网络模拟人脑的工作方式。
神经网络由相互连接的节点（神经元）组成，这些节点处理信息并从中学习。"""
        
        extracts = await sub_brain_extract(example_text, "机器学习")
        
        return {
            "test": "extract",
            "text_length": len(example_text),
            "keyword": "机器学习",
            "extracts": extracts,
            "success": True
        }
    except Exception as e:
        logger.error(f"测试关键词提取失败: {e}")
        return {
            "test": "extract",
            "success": False,
            "error": str(e)
        }


# 批量处理端点
@app.post("/batch/summarize_urls")
async def batch_summarize_urls(request: Dict[str, Any]):
    """
    批量网页摘要接口（带缓存和会话隔离）
    
    请求体:
        {
            "urls": ["url1", "url2", ...],
            "session_id": "可选的会话ID，用于会话隔离",
            "use_cache": true  # 是否使用缓存，默认为true
        }
        
    返回:
        批量摘要结果，包含缓存状态和会话信息
    """
    try:
        urls = request.get("urls", [])
        session_id = request.get("session_id")
        use_cache = request.get("use_cache", True)
        
        if not urls:
            raise HTTPException(status_code=400, detail="URL列表不能为空")
        
        if len(urls) > 10:
            raise HTTPException(status_code=400, detail="一次最多处理10个URL")
        
        logger.info(f"收到批量摘要请求，URL数量: {len(urls)}，会话ID: {session_id}，使用缓存: {use_cache}")
        
        # 导入缓存管理器
        try:
            from cache_manager import batch_summarize_with_cache, get_cache_manager
        except ImportError as e:
            logger.error(f"导入缓存管理器失败: {e}")
            # 回退到原始实现
            return await _legacy_batch_summarize(urls)
        
        if use_cache:
            # 使用带缓存的批量摘要
            results = await batch_summarize_with_cache(urls, session_id)
            
            # 统计信息
            cached_count = len([r for r in results if r.get("cached", False)])
            content_cached_count = len([r for r in results if r.get("content_cached", False)])
            error_count = len([r for r in results if "error" in r])
            
            # 构建响应
            summaries = []
            for result in results:
                if "error" in result:
                    summaries.append({
                        "url": result["url"],
                        "error": result["error"],
                        "session_id": result.get("session_id")
                    })
                else:
                    summaries.append({
                        "url": result["url"],
                        "summary": result["summary"],
                        "cached": result.get("cached", False),
                        "content_cached": result.get("content_cached", False),
                        "session_id": result.get("session_id")
                    })
            
            # 获取缓存统计
            cache_stats = get_cache_manager().get_cache_stats()
            
            return {
                "summaries": summaries,
                "total_urls": len(urls),
                "successful": len(urls) - error_count,
                "cached": cached_count,
                "content_cached": content_cached_count,
                "errors": error_count,
                "session_id": results[0].get("session_id") if results else None,
                "cache_stats": cache_stats
            }
        else:
            # 不使用缓存，使用原始实现
            return await _legacy_batch_summarize(urls)
        
    except Exception as e:
        logger.error(f"批量摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量摘要失败: {str(e)}")


async def _legacy_batch_summarize(urls: List[str]) -> Dict[str, Any]:
    """
    原始批量摘要实现（无缓存）
    
    参数:
        urls: URL列表
        
    返回:
        批量摘要结果
    """
    # 获取网页内容
    contents = []
    for url in urls:
        try:
            content = await get_page_content(url, allow_interactive=False)
            contents.append(content.get("content", ""))
        except Exception as e:
            logger.warning(f"获取网页内容失败 {url}: {e}")
            contents.append(f"获取网页内容失败: {str(e)}")
    
    # 批量摘要
    summaries = []
    for i, content in enumerate(contents):
        try:
            if content.startswith("获取网页内容失败"):
                summaries.append({"url": urls[i], "error": content})
            else:
                summary = await sub_brain_summarize(content)
                summaries.append({
                    "url": urls[i],
                    "summary": summary,
                    "content_length": len(content),
                    "summary_length": len(summary)
                })
        except Exception as e:
            logger.warning(f"摘要失败 {urls[i]}: {e}")
            summaries.append({"url": urls[i], "error": f"摘要失败: {str(e)}"})
    
    return {
        "summaries": summaries,
        "total_urls": len(urls),
        "successful": len([s for s in summaries if "error" not in s])
    }


def run_api_server(host: str = "127.0.0.1", port: int = None):
    """运行 API 服务器"""
    if port is None:
        port = get_api_port()
    
    logger.info(f"启动 API 服务器: {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行服务器
    run_api_server()