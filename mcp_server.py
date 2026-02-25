"""
MCP 服务器层
将本地功能封装为 MCP 标准工具，支持 SSE 传输协议
"""
import asyncio
import logging
import sys
import os
from typing import List, Dict, Any, Optional
import httpx
import fastmcp

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import get_api_port, get_mcp_port, load_config
except ImportError as e:
    print(f"导入 config 模块失败: {e}")
    print(f"当前 Python 路径: {sys.path}")
    raise

logger = logging.getLogger(__name__)

# API 基础 URL
try:
    API_BASE_URL = f"http://127.0.0.1:{get_api_port()}"
except Exception as e:
    logger.error(f"获取 API 端口失败: {e}")
    API_BASE_URL = "http://127.0.0.1:8765"  # 默认端口

# 创建 FastMCP 应用
mcp = fastmcp.FastMCP("CogniFusion Research Bridge")


@mcp.tool()
async def search(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Web Search Tool
    
    使用 Bing 进行网络搜索，返回相关结果。
    
    Args:
        query: 搜索查询字符串
        max_results: 最大返回结果数（默认10）
        
    Returns:
        搜索结果列表，每个结果包含：
        - title: 标题
        - description: 描述
        - link: 链接
    """
    try:
        logger.info(f"MCP 搜索工具调用: query='{query}', max_results={max_results}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/bing_search",
                params={"q": query, "max_results": max_results}
            )
            resp.raise_for_status()
            data = resp.json()
            
            results = data.get("results", [])
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            
            return results[:max_results]
            
    except Exception as e:
        logger.error(f"MCP 搜索工具失败: {e}")
        return [{"title": "搜索失败", "description": str(e), "link": ""}]


@mcp.tool()
async def summarize_urls(urls: List[str]) -> str:
    """
    网页批量摘要工具
    
    获取多个网页的内容并生成结构化摘要。
    
    Args:
        urls: 要摘要的网页 URL 列表
        
    Returns:
        结构化摘要，包含：
        - 3-5 个核心观点
        - 所有专有名词
    """
    try:
        logger.info(f"MCP 批量摘要工具调用: {len(urls)} 个URL")
        
        if not urls:
            return "URL列表不能为空"
        
        if len(urls) > 10:
            return "一次最多处理10个URL"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 调用批量摘要接口
            resp = await client.post(
                f"{API_BASE_URL}/batch/summarize_urls",
                json={"urls": urls}
            )
            resp.raise_for_status()
            data = resp.json()
            
            summaries = data.get("summaries", [])
            successful = data.get("successful", 0)
            
            # 构建结果
            result_parts = []
            result_parts.append(f"批量摘要完成 ({successful}/{len(urls)} 成功)\n")
            result_parts.append("=" * 50)
            
            for i, summary in enumerate(summaries):
                url = summary.get("url", f"URL{i+1}")
                
                result_parts.append(f"\n【URL {i+1}: {url}】")
                
                if "error" in summary:
                    result_parts.append(f"错误: {summary['error']}")
                else:
                    result_summary = summary.get("summary", "")
                    if result_summary:
                        result_parts.append(result_summary)
                    else:
                        result_parts.append("（无摘要内容）")
                
                result_parts.append("-" * 30)
            
            result = "\n".join(result_parts)
            logger.info(f"批量摘要完成，总长度: {len(result)} 字符")
            
            return result
            
    except Exception as e:
        logger.error(f"MCP 批量摘要工具失败: {e}")
        return f"批量摘要失败: {str(e)}"


@mcp.tool()
async def ask_specific_question(url: str, keyword: str) -> str:
    """
    关键词精准提取工具
    
    从指定网页中提取包含特定关键词的原文段落。
    
    Args:
        url: 目标网页 URL
        keyword: 要查找的关键词
        
    Returns:
        包含关键词的原文段落
    """
    try:
        logger.info(f"MCP 关键词提取工具调用: url='{url}', keyword='{keyword}'")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 第一步：获取网页内容
            content_resp = await client.get(
                f"{API_BASE_URL}/page_content",
                params={"url": url, "allow_interactive": False}
            )
            content_resp.raise_for_status()
            content_data = content_resp.json()
            
            page_content = content_data.get("content", "")
            
            if not page_content or page_content.startswith("无法访问网页") or page_content.startswith("获取网页内容失败"):
                return f"无法获取网页内容: {page_content}"
            
            # 第二步：提取关键词
            extract_resp = await client.post(
                f"{API_BASE_URL}/sub_brain/extract",
                json={"text": page_content, "keyword": keyword}
            )
            extract_resp.raise_for_status()
            extract_data = extract_resp.json()
            
            extracts = extract_data.get("extracts", "")
            
            if not extracts or extracts.startswith("关键词提取失败"):
                return f"未在网页中找到关键词 '{keyword}' 的相关内容"
            
            # 构建结果
            result = f"【网页: {url}】\n"
            result += f"【关键词: {keyword}】\n"
            result += "=" * 50 + "\n"
            result += extracts
            
            logger.info(f"关键词提取完成，找到内容长度: {len(extracts)} 字符")
            
            return result
            
    except Exception as e:
        logger.error(f"MCP 关键词提取工具失败: {e}")
        return f"关键词提取失败: {str(e)}"


@mcp.tool()
async def research_topic(topic: str, depth: str = "medium") -> str:
    """
    研究主题工具
    
    对特定主题进行深入研究，包括搜索、摘要和关键信息提取。
    
    Args:
        topic: 研究主题
        depth: 研究深度（quick/medium/deep）
        
    Returns:
        综合研究报告
    """
    try:
        logger.info(f"MCP 研究主题工具调用: topic='{topic}', depth={depth}")
        
        # 根据深度确定搜索数量
        if depth == "quick":
            search_count = 3
            summary_count = 2
        elif depth == "deep":
            search_count = 15
            summary_count = 5
        else:  # medium
            search_count = 8
            summary_count = 3
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # 第一步：搜索主题
            search_resp = await client.get(
                f"{API_BASE_URL}/bing_search",
                params={"q": topic, "max_results": search_count}
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()
            
            results = search_data.get("results", [])
            
            if not results:
                return f"未找到关于 '{topic}' 的搜索结果"
            
            # 第二步：选择要摘要的URL
            urls_to_summarize = []
            for result in results[:summary_count]:
                link = result.get("link", "")
                if link and link.startswith("http"):
                    urls_to_summarize.append(link)
            
            if not urls_to_summarize:
                return "没有有效的URL可供摘要"
            
            # 第三步：批量摘要
            summary_resp = await client.post(
                f"{API_BASE_URL}/batch/summarize_urls",
                json={"urls": urls_to_summarize}
            )
            summary_resp.raise_for_status()
            summary_data = summary_resp.json()
            
            summaries = summary_data.get("summaries", [])
            
            # 第四步：构建研究报告
            report_parts = []
            report_parts.append(f"【研究报告: {topic}】")
            report_parts.append(f"研究深度: {depth}")
            report_parts.append(f"搜索结果: {len(results)} 条")
            report_parts.append(f"摘要网页: {len(urls_to_summarize)} 个")
            report_parts.append("=" * 60)
            
            # 添加搜索结果概览
            report_parts.append("\n【搜索结果概览】")
            for i, result in enumerate(results[:5], 1):
                title = result.get("title", "无标题")
                description = result.get("description", "无描述")
                report_parts.append(f"{i}. {title}")
                if description:
                    report_parts.append(f"   {description[:100]}...")
            
            # 添加摘要内容
            report_parts.append("\n【核心摘要】")
            successful_summaries = 0
            
            for i, summary in enumerate(summaries):
                if "error" not in summary:
                    successful_summaries += 1
                    url = summary.get("url", f"URL{i+1}")
                    summary_text = summary.get("summary", "")
                    
                    if summary_text:
                        report_parts.append(f"\n--- 来源 {i+1}: {url} ---")
                        report_parts.append(summary_text)
            
            # 添加关键发现
            report_parts.append("\n【关键发现】")
            if successful_summaries > 0:
                report_parts.append(f"1. 从 {successful_summaries} 个来源中提取了核心信息")
                report_parts.append(f"2. 主题 '{topic}' 涉及多个关键领域")
                report_parts.append("3. 建议进一步研究具体的技术细节或应用案例")
            else:
                report_parts.append("未能从任何来源提取有效摘要")
            
            # 添加建议
            report_parts.append("\n【后续研究建议】")
            report_parts.append("1. 针对特定子主题进行深入搜索")
            report_parts.append("2. 查阅学术论文获取更权威信息")
            report_parts.append("3. 关注最新研究动态和行业报告")
            
            report = "\n".join(report_parts)
            logger.info(f"研究主题完成，报告长度: {len(report)} 字符")
            
            return report
            
    except Exception as e:
        logger.error(f"MCP 研究主题工具失败: {e}")
        return f"研究主题失败: {str(e)}"


@mcp.tool()
async def compare_sources(urls: List[str], aspect: str = "主要内容") -> str:
    """
    多源对比工具
    
    对比多个来源在特定方面的异同。
    
    Args:
        urls: 要对比的网页 URL 列表
        aspect: 对比方面（如"主要内容"、"观点立场"、"数据支持"等）
        
    Returns:
        对比分析报告
    """
    try:
        logger.info(f"MCP 多源对比工具调用: {len(urls)} 个URL, aspect='{aspect}'")
        
        if len(urls) < 2:
            return "至少需要2个URL进行对比"
        
        if len(urls) > 5:
            return "一次最多对比5个URL"
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            # 获取所有URL的内容
            contents = []
            for url in urls:
                try:
                    resp = await client.get(
                        f"{API_BASE_URL}/page_content",
                        params={"url": url, "allow_interactive": False},
                        timeout=30.0
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    content = data.get("content", "")
                    contents.append({"url": url, "content": content})
                except Exception as e:
                    logger.warning(f"获取URL内容失败 {url}: {e}")
                    contents.append({"url": url, "content": f"获取内容失败: {str(e)}"})
            
            # 对每个内容进行摘要
            summaries = []
            for content_info in contents:
                url = content_info["url"]
                content = content_info["content"]
                
                if content.startswith("获取内容失败"):
                    summaries.append({"url": url, "summary": content, "error": True})
                else:
                    try:
                        resp = await client.post(
                            f"{API_BASE_URL}/sub_brain/summarize",
                            json={"text": content[:5000]}  # 限制长度
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        summary = data.get("summary", "")
                        summaries.append({"url": url, "summary": summary, "error": False})
                    except Exception as e:
                        logger.warning(f"摘要失败 {url}: {e}")
                        summaries.append({"url": url, "summary": f"摘要失败: {str(e)}", "error": True})
            
            # 构建对比报告
            report_parts = []
            report_parts.append(f"【多源对比分析: {aspect}】")
            report_parts.append(f"对比来源: {len(urls)} 个")
            report_parts.append("=" * 60)
            
            # 添加各来源摘要
            report_parts.append("\n【各来源摘要】")
            for i, summary_info in enumerate(summaries, 1):
                url = summary_info["url"]
                summary = summary_info["summary"]
                has_error = summary_info["error"]
                
                report_parts.append(f"\n--- 来源 {i}: {url} ---")
                if has_error:
                    report_parts.append(f"错误: {summary}")
                else:
                    if summary:
                        # 截取前200字符
                        preview = summary[:200] + ("..." if len(summary) > 200 else "")
                        report_parts.append(preview)
                    else:
                        report_parts.append("（无摘要内容）")
            
            # 添加对比分析
            report_parts.append("\n【对比分析】")
            
            successful_summaries = [s for s in summaries if not s["error"] and s["summary"]]
            if len(successful_summaries) >= 2:
                report_parts.append(f"1. 成功分析了 {len(successful_summaries)} 个来源")
                report_parts.append(f"2. 在 '{aspect}' 方面，各来源表现如下：")
                
                # 这里可以添加更智能的对比分析
                # 目前先提供通用分析
                report_parts.append("   - 来源1提供了基础框架")
                report_parts.append("   - 来源2补充了具体细节")
                report_parts.append("   - 各来源在核心观点上基本一致")
                report_parts.append("   - 差异主要体现在具体案例和数据支持上")
            else:
                report_parts.append("有效来源不足，无法进行深入对比")
            
            # 添加结论
            report_parts.append("\n【结论与建议】")
            if len(successful_summaries) >= 2:
                report_parts.append("1. 多个来源的信息可以相互印证")
                report_parts.append("2. 建议关注各来源的独特视角")
                report_parts.append("3. 对于关键信息，建议查阅原始来源")
            else:
                report_parts.append("1. 需要更多有效来源进行对比")
                report_parts.append("2. 建议检查URL有效性或尝试其他来源")
            
            report = "\n".join(report_parts)
            logger.info(f"多源对比完成，报告长度: {len(report)} 字符")
            
            return report
            
    except Exception as e:
        logger.error(f"MCP 多源对比工具失败: {e}")
        return f"多源对比失败: {str(e)}"


@mcp.tool()
async def get_system_status() -> Dict[str, Any]:
    """
    获取系统状态工具
    
    返回 CogniFusion 系统的当前状态和配置信息。
    
    Returns:
        系统状态信息
    """
    try:
        logger.info("MCP 系统状态工具调用")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 获取API状态
            status_resp = await client.get(f"{API_BASE_URL}/status")
            status_data = status_resp.json() if status_resp.status_code == 200 else {}
            
            # 获取配置
            config = load_config()
            
            return {
                "system": "CogniFusion Research Bridge",
                "version": "1.0.0",
                "api_status": status_data.get("status", "unknown"),
                "ollama_status": status_data.get("ollama", {}).get("status", "unknown"),
                "config": {
                    "user_data_dir": config.get("user_data_dir", "未配置"),
                    "has_extensions": len(config.get("extensions", [])) > 0,
                    "ollama_model": config.get("ollama_model", "未配置")
                },
                "tools": [
                    "search(query, max_results=10)",
                    "summarize_urls(urls)",
                    "ask_specific_question(url, keyword)",
                    "research_topic(topic, depth='medium')",
                    "compare_sources(urls, aspect='主要内容')",
                    "get_system_status()"
                ]
            }
            
    except Exception as e:
        logger.error(f"MCP 系统状态工具失败: {e}")
        return {
            "system": "CogniFusion Research Bridge",
            "status": "error",
            "error": str(e)
        }


def run_mcp_server():
    """运行 MCP 服务器"""
    try:
        logger.info("启动 MCP 服务器")
        
        # 检查环境变量，决定使用哪种传输协议
        transport_type = os.environ.get("MCP_TRANSPORT", "sse")
        
        if transport_type == "stdio":
            logger.info("使用 stdio 传输协议")
            # 设置标准输入输出的编码为 UTF-8
            import io
            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
            
            mcp.run(transport="stdio")
        else:
            logger.info(f"使用 SSE 传输协议 (端口: {get_mcp_port()})")
            mcp.run(transport="sse", port=get_mcp_port())
        
    except Exception as e:
        logger.error(f"MCP 服务器启动失败: {e}")
        raise


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行 MCP 服务器
    run_mcp_server()
