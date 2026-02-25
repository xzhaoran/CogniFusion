"""
浏览器自动化核心模块
使用 Playwright 进行浏览器自动化，支持真实浏览器环境和资源优化
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, quote_plus

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
import httpx

from config import get_user_data_dir, get_extensions, get_auto_open_browser, get_headless_mode

logger = logging.getLogger(__name__)

# 要拦截的资源类型
BLOCK_RESOURCES = ["image", "stylesheet", "font", "media"]


class BrowserCore:
    """浏览器自动化核心类"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._is_initialized = False
        
    async def initialize(self):
        """初始化浏览器环境"""
        if self._is_initialized:
            return
            
        try:
            self.playwright = await async_playwright().start()
            
            # 获取配置
            user_data_dir = get_user_data_dir()
            extensions = get_extensions()
            headless_mode = get_headless_mode()
            
            logger.info(f"浏览器配置: headless={headless_mode}, user_data_dir={user_data_dir}")
            
            if user_data_dir and user_data_dir.exists():
                logger.info(f"使用用户数据目录: {user_data_dir}")
                
                try:
                    # 尝试使用用户数据目录创建持久化上下文
                    self.context = await self.playwright.chromium.launch_persistent_context(
                        user_data_dir=str(user_data_dir),
                        headless=headless_mode,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                        ],
                        viewport={'width': 1280, 'height': 720},
                        ignore_https_errors=True,
                    )
                    logger.info("浏览器上下文创建成功（使用用户数据目录）")
                except Exception as e:
                    logger.warning(f"使用用户数据目录失败: {e}，尝试使用临时上下文")
                    # 回退到临时上下文
                    self.browser = await self.playwright.chromium.launch(headless=headless_mode)
                    self.context = await self.browser.new_context(
                        viewport={'width': 1280, 'height': 720},
                        ignore_https_errors=True,
                    )
            else:
                logger.warning("用户数据目录未配置或不存在，使用临时上下文")
                self.browser = await self.playwright.chromium.launch(headless=headless_mode)
                self.context = await self.browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    ignore_https_errors=True,
                )
            
            # 设置资源拦截
            await self._setup_resource_interception()
            logger.info("浏览器上下文创建成功")
                
            self._is_initialized = True
            logger.info("浏览器核心初始化完成")
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            await self.close()
            raise
    
    async def _setup_resource_interception(self):
        """设置资源拦截"""
        if not self.context:
            return
            
        await self.context.route("**/*", self._block_heavy_resources)
        logger.info("资源拦截已设置")
    
    async def _block_heavy_resources(self, route):
        """拦截图片、样式、字体等，保留 HTML/JS 以获取纯文本内容"""
        if route.request.resource_type in BLOCK_RESOURCES:
            await route.abort()
        else:
            await route.continue_()
    
    async def search_bing(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        使用 Bing 进行搜索
        
        参数:
            query: 搜索关键词
            max_results: 最大返回结果数
            
        返回:
            搜索结果列表，每个结果包含 title, description, link
        """
        if not self._is_initialized:
            await self.initialize()
            
        try:
            # 创建新页面
            page = await self.context.new_page()
            
            # 编码搜索关键词
            encoded_query = quote_plus(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}"
            
            logger.info(f"开始搜索: {query}")
            await page.goto(search_url, wait_until="networkidle")
            
            # 等待搜索结果加载
            await page.wait_for_selector("#b_results", timeout=10000)
            
            # 提取搜索结果
            results = []
            
            # 查找所有搜索结果项
            result_elements = await page.query_selector_all(".b_algo")
            
            for i, element in enumerate(result_elements[:max_results]):
                try:
                    # 提取标题
                    title_elem = await element.query_selector("h2 a")
                    title = await title_elem.text_content() if title_elem else ""
                    
                    # 提取链接
                    link = await title_elem.get_attribute("href") if title_elem else ""
                    
                    # 提取描述
                    desc_elem = await element.query_selector(".b_caption p")
                    description = await desc_elem.text_content() if desc_elem else ""
                    
                    if title and link:
                        results.append({
                            "title": title.strip(),
                            "description": description.strip() if description else "",
                            "link": link.strip()
                        })
                        
                        logger.debug(f"找到结果 {i+1}: {title[:50]}...")
                        
                except Exception as e:
                    logger.warning(f"提取结果 {i+1} 时出错: {e}")
                    continue
            
            await page.close()
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    async def get_page_content(self, url: str, allow_interactive: bool = True) -> Dict[str, str]:
        """
        获取网页内容
        
        参数:
            url: 网页URL
            allow_interactive: 是否允许交互式登录
            
        返回:
            包含url和content的字典
        """
        if not self._is_initialized:
            await self.initialize()
            
        try:
            page = await self.context.new_page()
            
            logger.info(f"获取网页内容: {url}")
            
            # 设置超时
            timeout = 30000  # 30秒
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                
                # 等待页面基本加载
                await page.wait_for_load_state("domcontentloaded")
                
                # 检查是否需要登录
                if allow_interactive:
                    login_detected = await self._detect_login_page(page)
                    if login_detected:
                        logger.info("检测到登录页面，等待用户手动登录...")
                        # 这里可以添加等待用户登录的逻辑
                        # 暂时只是记录日志
                
                # 获取页面文本内容
                content = await self._extract_page_text(page)
                
                # 清理文本
                cleaned_content = self._clean_page_text(content)
                
                await page.close()
                
                logger.info(f"网页内容提取成功，长度: {len(cleaned_content)} 字符")
                
                return {
                    "url": url,
                    "content": cleaned_content
                }
                
            except Exception as e:
                logger.error(f"访问网页失败: {e}")
                await page.close()
                return {
                    "url": url,
                    "content": f"无法访问网页: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"获取网页内容失败: {e}")
            return {
                "url": url,
                "content": f"获取网页内容失败: {str(e)}"
            }
    
    async def _detect_login_page(self, page: Page) -> bool:
        """检测是否是登录页面"""
        try:
            # 检查常见的登录页面特征
            page_text = await page.content()
            login_indicators = [
                "login", "sign in", "log in", "password", "username",
                "email", "登录", "密码", "用户名", "邮箱"
            ]
            
            page_text_lower = page_text.lower()
            for indicator in login_indicators:
                if indicator in page_text_lower:
                    return True
                    
            # 检查登录表单
            login_form = await page.query_selector("input[type='password'], input[name*='password']")
            if login_form:
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"检测登录页面时出错: {e}")
            return False
    
    async def _extract_page_text(self, page: Page) -> str:
        """提取页面文本内容"""
        try:
            # 尝试获取主要文章内容
            article_selectors = [
                "article", "main", ".article", ".post", ".content",
                "#content", "#main", ".main-content", "[role='main']"
            ]
            
            for selector in article_selectors:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and len(text.strip()) > 100:  # 确保有足够的内容
                        return text
            
            # 如果没有找到文章区域，获取整个body
            body = await page.query_selector("body")
            if body:
                return await body.text_content()
            
            # 最后尝试获取整个页面
            return await page.content()
            
        except Exception as e:
            logger.warning(f"提取页面文本时出错: {e}")
            # 回退到获取整个页面
            try:
                return await page.content()
            except:
                return ""
    
    def _clean_page_text(self, text: str) -> str:
        """清理页面文本"""
        if not text:
            return ""
        
        # 移除多余的空格和换行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 合并连续的空白行
        cleaned_lines = []
        for line in lines:
            if line:  # 非空行
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1]:  # 空行，但前一行不是空行
                cleaned_lines.append("")
        
        # 重新组合文本
        cleaned_text = '\n'.join(cleaned_lines)
        
        # 移除过长的连续空格
        import re
        cleaned_text = re.sub(r'\s{3,}', '  ', cleaned_text)
        
        return cleaned_text
    
    async def close(self):
        """关闭浏览器资源"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
                
            if self.browser:
                await self.browser.close()
                self.browser = None
                
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
            self._is_initialized = False
            logger.info("浏览器资源已关闭")
            
        except Exception as e:
            logger.error(f"关闭浏览器资源时出错: {e}")
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 全局浏览器实例
_browser_instance: Optional[BrowserCore] = None


async def get_browser() -> BrowserCore:
    """获取全局浏览器实例"""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserCore()
        await _browser_instance.initialize()
    return _browser_instance


async def search_bing(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """搜索Bing（便捷函数）"""
    browser = await get_browser()
    return await browser.search_bing(query, max_results)


async def get_page_content(url: str, allow_interactive: bool = True) -> Dict[str, str]:
    """获取网页内容（便捷函数）"""
    browser = await get_browser()
    return await browser.get_page_content(url, allow_interactive)


async def close_browser():
    """关闭浏览器（便捷函数）"""
    global _browser_instance
    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None


def _is_portable_mode() -> bool:
    """检测是否处于便携版模式"""
    return os.environ.get('PORTABLE_MODE') == '1'


def _get_browser_executable_path() -> Optional[str]:
    """获取便携版浏览器可执行文件路径"""
    if not _is_portable_mode():
        return None
    
    browsers_root = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
    if not browsers_root:
        return None
    
    # 查找Chromium可执行文件
    chromium_path = Path(browsers_root) / "chromium" / "chrome-win" / "chrome.exe"
    if chromium_path.exists():
        return str(chromium_path)
    
    return None