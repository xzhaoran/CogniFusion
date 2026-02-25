"""
缓存管理器
提供文章缓存和会话隔离功能，防止上下文污染和重复处理
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器类"""
    
    def __init__(self, cache_dir: str = None):
        """
        初始化缓存管理器
        
        参数:
            cache_dir: 缓存目录路径，如果为None则使用默认目录
        """
        if cache_dir is None:
            # 使用项目根目录下的 .cache 目录
            self.cache_dir = Path(__file__).parent / ".cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        # 创建缓存目录
        self.cache_dir.mkdir(exist_ok=True)
        
        # 缓存文件路径
        self.summary_cache_file = self.cache_dir / "summaries.json"
        self.content_cache_file = self.cache_dir / "contents.json"
        
        # 加载现有缓存
        self.summary_cache = self._load_cache(self.summary_cache_file)
        self.content_cache = self._load_cache(self.content_cache_file)
        
        # 会话管理
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 会话超时时间（秒）
        
        logger.info(f"缓存管理器初始化完成，缓存目录: {self.cache_dir}")
    
    def _load_cache(self, cache_file: Path) -> Dict[str, Any]:
        """加载缓存文件"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载缓存文件失败 {cache_file}: {e}")
        
        return {}
    
    def _save_cache(self, cache_file: Path, cache_data: Dict[str, Any]):
        """保存缓存文件"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存文件失败 {cache_file}: {e}")
    
    def _generate_cache_key(self, url: str, operation: str = "summary") -> str:
        """
        生成缓存键
        
        参数:
            url: URL地址
            operation: 操作类型（summary/content）
            
        返回:
            缓存键
        """
        # 使用URL和操作类型生成MD5哈希作为缓存键
        key_string = f"{url}:{operation}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get_cached_summary(self, url: str) -> Optional[str]:
        """
        获取缓存的摘要
        
        参数:
            url: URL地址
            
        返回:
            缓存的摘要内容，如果不存在则返回None
        """
        cache_key = self._generate_cache_key(url, "summary")
        cached_data = self.summary_cache.get(cache_key)
        
        if cached_data:
            # 检查缓存是否过期（默认缓存7天）
            cache_time = cached_data.get("timestamp", 0)
            cache_ttl = cached_data.get("ttl", 604800)  # 7天
            
            if time.time() - cache_time < cache_ttl:
                logger.info(f"从缓存获取摘要: {url}")
                return cached_data.get("content")
            else:
                # 缓存过期，删除
                del self.summary_cache[cache_key]
                self._save_cache(self.summary_cache_file, self.summary_cache)
        
        return None
    
    def cache_summary(self, url: str, summary: str, ttl: int = 604800):
        """
        缓存摘要
        
        参数:
            url: URL地址
            summary: 摘要内容
            ttl: 缓存生存时间（秒），默认7天
        """
        cache_key = self._generate_cache_key(url, "summary")
        
        self.summary_cache[cache_key] = {
            "url": url,
            "content": summary,
            "timestamp": time.time(),
            "ttl": ttl,
            "length": len(summary)
        }
        
        self._save_cache(self.summary_cache_file, self.summary_cache)
        logger.info(f"缓存摘要: {url}，长度: {len(summary)} 字符")
    
    def get_cached_content(self, url: str) -> Optional[str]:
        """
        获取缓存的网页内容
        
        参数:
            url: URL地址
            
        返回:
            缓存的网页内容，如果不存在则返回None
        """
        cache_key = self._generate_cache_key(url, "content")
        cached_data = self.content_cache.get(cache_key)
        
        if cached_data:
            # 检查缓存是否过期（默认缓存1天）
            cache_time = cached_data.get("timestamp", 0)
            cache_ttl = cached_data.get("ttl", 86400)  # 1天
            
            if time.time() - cache_time < cache_ttl:
                logger.info(f"从缓存获取网页内容: {url}")
                return cached_data.get("content")
            else:
                # 缓存过期，删除
                del self.content_cache[cache_key]
                self._save_cache(self.content_cache_file, self.content_cache)
        
        return None
    
    def cache_content(self, url: str, content: str, ttl: int = 86400):
        """
        缓存网页内容
        
        参数:
            url: URL地址
            content: 网页内容
            ttl: 缓存生存时间（秒），默认1天
        """
        cache_key = self._generate_cache_key(url, "content")
        
        self.content_cache[cache_key] = {
            "url": url,
            "content": content,
            "timestamp": time.time(),
            "ttl": ttl,
            "length": len(content)
        }
        
        self._save_cache(self.content_cache_file, self.content_cache)
        logger.info(f"缓存网页内容: {url}，长度: {len(content)} 字符")
    
    def create_session(self, session_id: str = None) -> str:
        """
        创建新会话
        
        参数:
            session_id: 可选的会话ID，如果为None则自动生成
            
        返回:
            会话ID
        """
        if session_id is None:
            session_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()[:12]
        
        self.sessions[session_id] = {
            "created_at": time.time(),
            "last_activity": time.time(),
            "urls": [],
            "summaries": {},
            "context": {}
        }
        
        logger.info(f"创建新会话: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        参数:
            session_id: 会话ID
            
        返回:
            会话信息字典，如果会话不存在或已过期则返回None
        """
        session = self.sessions.get(session_id)
        
        if session:
            # 检查会话是否过期
            if time.time() - session["last_activity"] > self.session_timeout:
                logger.info(f"会话已过期: {session_id}")
                del self.sessions[session_id]
                return None
            
            # 更新最后活动时间
            session["last_activity"] = time.time()
            return session
        
        return None
    
    def add_url_to_session(self, session_id: str, url: str, summary: str = None):
        """
        添加URL到会话
        
        参数:
            session_id: 会话ID
            url: URL地址
            summary: 可选的摘要内容
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"会话不存在: {session_id}")
            return
        
        if url not in session["urls"]:
            session["urls"].append(url)
        
        if summary:
            session["summaries"][url] = {
                "summary": summary,
                "timestamp": time.time()
            }
        
        logger.debug(f"添加URL到会话 {session_id}: {url}")
    
    def get_session_summaries(self, session_id: str) -> Dict[str, str]:
        """
        获取会话中的所有摘要
        
        参数:
            session_id: 会话ID
            
        返回:
            会话摘要字典 {url: summary}
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {url: data["summary"] for url, data in session["summaries"].items()}
    
    def clear_expired_sessions(self):
        """清理过期的会话"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"清理过期会话: {session_id}")
    
    def clear_cache(self, cache_type: str = "all"):
        """
        清理缓存
        
        参数:
            cache_type: 缓存类型（summary/content/all）
        """
        if cache_type in ["summary", "all"]:
            self.summary_cache = {}
            self._save_cache(self.summary_cache_file, self.summary_cache)
            logger.info("清理摘要缓存")
        
        if cache_type in ["content", "all"]:
            self.content_cache = {}
            self._save_cache(self.content_cache_file, self.content_cache)
            logger.info("清理内容缓存")
        
        if cache_type == "all":
            self.sessions = {}
            logger.info("清理所有会话")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        返回:
            缓存统计字典
        """
        return {
            "summary_cache": {
                "size": len(self.summary_cache),
                "total_chars": sum(data.get("length", 0) for data in self.summary_cache.values())
            },
            "content_cache": {
                "size": len(self.content_cache),
                "total_chars": sum(data.get("length", 0) for data in self.content_cache.values())
            },
            "sessions": {
                "count": len(self.sessions),
                "active_sessions": len([s for s in self.sessions.values() 
                                      if time.time() - s["last_activity"] < self.session_timeout])
            }
        }


# 全局缓存管理器实例
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


async def batch_summarize_with_cache(urls: List[str], session_id: str = None) -> List[Dict[str, Any]]:
    """
    带缓存的批量摘要
    
    参数:
        urls: URL列表
        session_id: 可选的会话ID，用于会话隔离
        
    返回:
        摘要结果列表
    """
    from browser_core import get_page_content
    from ollama_client import sub_brain_summarize
    
    cache_manager = get_cache_manager()
    
    # 如果没有提供会话ID，创建新会话
    if session_id is None:
        session_id = cache_manager.create_session()
    
    results = []
    
    for url in urls:
        try:
            # 检查缓存
            cached_summary = cache_manager.get_cached_summary(url)
            
            if cached_summary:
                # 使用缓存
                results.append({
                    "url": url,
                    "summary": cached_summary,
                    "cached": True,
                    "session_id": session_id
                })
                
                # 添加到会话
                cache_manager.add_url_to_session(session_id, url, cached_summary)
                continue
            
            # 获取网页内容（检查内容缓存）
            cached_content = cache_manager.get_cached_content(url)
            
            if cached_content:
                content = cached_content
                content_cached = True
            else:
                # 获取网页内容
                content_data = await get_page_content(url, allow_interactive=False)
                content = content_data.get("content", "")
                content_cached = False
                
                # 缓存内容
                if content and not content.startswith("无法访问网页"):
                    cache_manager.cache_content(url, content)
            
            # 生成摘要
            if content and not content.startswith("无法访问网页"):
                summary = await sub_brain_summarize(content)
                
                # 缓存摘要
                cache_manager.cache_summary(url, summary)
                
                # 添加到会话
                cache_manager.add_url_to_session(session_id, url, summary)
                
                results.append({
                    "url": url,
                    "summary": summary,
                    "cached": False,
                    "content_cached": content_cached,
                    "session_id": session_id
                })
            else:
                results.append({
                    "url": url,
                    "error": content if content else "获取网页内容失败",
                    "cached": False,
                    "session_id": session_id
                })
                
        except Exception as e:
            logger.error(f"处理URL失败 {url}: {e}")
            results.append({
                "url": url,
                "error": f"处理失败: {str(e)}",
                "session_id": session_id
            })
    
    return results


def test_cache_manager():
    """测试缓存管理器"""
    print("🧪 测试缓存管理器...")
    print("=" * 50)
    
    try:
        cache_manager = CacheManager()
        
        # 测试缓存功能
        test_url = "https://example.com/test"
        test_summary = "这是一个测试摘要"
        
        # 缓存摘要
        cache_manager.cache_summary(test_url, test_summary, ttl=10)
        print(f"✅ 缓存摘要: {test_url}")
        
        # 获取缓存
        cached = cache_manager.get_cached_summary(test_url)
        if cached == test_summary:
            print(f"✅ 获取缓存成功: {cached[:50]}...")
        else:
            print(f"❌ 获取缓存失败")
        
        # 测试会话功能
        session_id = cache_manager.create_session()
        print(f"✅ 创建会话: {session_id}")
        
        cache_manager.add_url_to_session(session_id, test_url, test_summary)
        print(f"✅ 添加URL到会话")
        
        session_summaries = cache_manager.get_session_summaries(session_id)
        print(f"✅ 获取会话摘要: {len(session_summaries)} 个")
        
        # 获取统计信息
        stats = cache_manager.get_cache_stats()
        print(f"✅ 缓存统计: {stats}")
        
        print("\n🎉 缓存管理器测试通过！")
        
    except Exception as e:
        print(f"❌ 缓存管理器测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_cache_manager()