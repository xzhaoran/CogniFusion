"""
本地副脑（Ollama）客户端模块
负责与本地 Ollama 服务通信，进行文本摘要和关键词提取
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
import json

from config import get_ollama_config, get_max_text_length, get_max_extract_length

logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama 客户端类"""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.api_url: str = "http://127.0.0.1:11434"
        self.model: str = "llama3.2"
        self._is_initialized = False
        
    async def initialize(self):
        """初始化客户端"""
        if self._is_initialized:
            return
            
        try:
            # 获取配置
            config = get_ollama_config()
            self.api_url = config["api_url"]
            self.model = config["model"]
            
            # 创建 HTTP 客户端
            self.client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=120.0,  # 长文本处理可能需要较长时间
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            # 测试连接
            await self._test_connection()
            
            self._is_initialized = True
            logger.info(f"Ollama 客户端初始化成功，API: {self.api_url}, 模型: {self.model}")
            
        except Exception as e:
            logger.error(f"Ollama 客户端初始化失败: {e}")
            await self.close()
            raise
    
    async def _test_connection(self):
        """测试 Ollama 连接"""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            
            # 清理模型名称（移除首尾空格）
            cleaned_models = [model.strip() for model in models]
            cleaned_config_model = self.model.strip()
            
            if cleaned_config_model not in cleaned_models:
                logger.warning(f"模型 '{cleaned_config_model}' 未找到，可用模型: {cleaned_models}")
                # 尝试使用第一个可用模型
                if cleaned_models:
                    self.model = cleaned_models[0]
                    logger.info(f"自动切换到模型: {self.model}")
                else:
                    raise Exception("没有可用的 Ollama 模型")
                    
            logger.info(f"Ollama 连接测试成功，可用模型: {cleaned_models}")
            
        except Exception as e:
            logger.error(f"Ollama 连接测试失败: {e}")
            raise
    
    async def summarize(self, text: str) -> str:
        """
        文本摘要：将长文本压缩为结构化大纲
        
        参数:
            text: 需要摘要的文本
            
        返回:
            结构化大纲（3-5个核心观点+专有名词）
        """
        if not self._is_initialized:
            await self.initialize()
            
        try:
            # 限制文本长度
            max_length = get_max_text_length()
            if len(text) > max_length:
                text = text[:max_length]
                logger.info(f"文本过长，截取前 {max_length} 字符")
            
            # 构建系统提示
            system_prompt = """你是一个专业的研究助手。请把以下内容压缩成一个结构化大纲。

要求：
1. 提取 3-5 个最核心的观点
2. 列出文中出现的所有专有名词（技术术语、人名、地名、机构名等）
3. 保持客观，不要添加个人观点
4. 使用中文输出

输出格式：
【核心观点】
1. 观点1
2. 观点2
3. 观点3

【专有名词】
- 名词1
- 名词2
- 名词3"""
            
            # 构建用户提示
            user_prompt = f"请对以下内容生成结构化大纲与专有名词列表：\n\n{text}"
            
            # 调用 Ollama API
            response = await self._ollama_complete(user_prompt, system=system_prompt)
            
            logger.info(f"文本摘要完成，输出长度: {len(response)} 字符")
            return response
            
        except Exception as e:
            logger.error(f"文本摘要失败: {e}")
            return f"文本摘要失败: {str(e)}"
    
    async def extract(self, text: str, keyword: str) -> str:
        """
        关键词提取：在长文本中定位包含关键词的原文段落
        
        参数:
            text: 源文本
            keyword: 关键词
            
        返回:
            包含关键词的原文段落
        """
        if not self._is_initialized:
            await self.initialize()
            
        try:
            # 限制文本长度
            max_length = get_max_extract_length()
            if len(text) > max_length:
                text = text[:max_length]
                logger.info(f"文本过长，截取前 {max_length} 字符")
            
            # 构建系统提示
            system_prompt = """你是一个研究助手。你的任务是在长文本中找出所有包含指定关键词的段落。

要求：
1. 找出文本中所有包含该关键词的段落
2. 完整摘录这些段落，不要改写
3. 保持原文的格式和标点
4. 如果找不到包含关键词的段落，返回"未找到相关段落"
5. 使用中文输出

输出格式：
【包含关键词的段落】
1. 段落1原文
2. 段落2原文
3. 段落3原文"""
            
            # 构建用户提示
            user_prompt = f"关键词：{keyword}\n\n请从以下文本中找出所有包含该关键词的段落，完整摘录原文：\n\n{text}"
            
            # 调用 Ollama API
            response = await self._ollama_complete(user_prompt, system=system_prompt)
            
            logger.info(f"关键词提取完成，关键词: '{keyword}'，输出长度: {len(response)} 字符")
            return response
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return f"关键词提取失败: {str(e)}"
    
    async def _ollama_complete(self, prompt: str, system: Optional[str] = None) -> str:
        """
        调用 Ollama API 完成文本生成
        
        参数:
            prompt: 用户提示
            system: 系统提示（可选）
            
        返回:
            生成的文本
        """
        if not self.client:
            raise Exception("Ollama 客户端未初始化")
        
        try:
            # 构建请求数据
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 低温度以获得更确定的输出
                    "top_p": 0.9,
                    "num_predict": 2000,  # 最大生成长度
                }
            }
            
            if system:
                request_data["system"] = system
            
            # 发送请求
            response = await self.client.post(
                "/api/generate",
                json=request_data,
                timeout=60.0
            )
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            result = data.get("response", "").strip()
            
            # 清理结果
            result = self._clean_response(result)
            
            return result
            
        except httpx.TimeoutException:
            logger.error("Ollama API 请求超时")
            raise Exception("Ollama 响应超时，请检查模型是否正常运行")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API HTTP 错误: {e.response.status_code}")
            raise Exception(f"Ollama API 错误: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Ollama API 调用失败: {e}")
            raise
    
    def _clean_response(self, text: str) -> str:
        """清理响应文本"""
        if not text:
            return ""
        
        # 移除多余的空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 重新组合
        cleaned_text = '\n'.join(lines)
        
        # 移除常见的模型输出前缀
        prefixes = ["当然", "好的", "以下是", "根据您的要求", "我"]
        for prefix in prefixes:
            if cleaned_text.startswith(prefix):
                # 找到第一个句号或换行
                first_period = cleaned_text.find('。')
                first_newline = cleaned_text.find('\n')
                
                if first_period > 0 and (first_newline < 0 or first_period < first_newline):
                    cleaned_text = cleaned_text[first_period + 1:].strip()
                elif first_newline > 0:
                    cleaned_text = cleaned_text[first_newline:].strip()
        
        return cleaned_text
    
    async def batch_summarize(self, texts: List[str]) -> List[str]:
        """
        批量文本摘要
        
        参数:
            texts: 文本列表
            
        返回:
            摘要列表
        """
        tasks = [self.summarize(text) for text in texts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def batch_extract(self, texts: List[str], keywords: List[str]) -> List[str]:
        """
        批量关键词提取
        
        参数:
            texts: 文本列表
            keywords: 关键词列表（与文本一一对应）
            
        返回:
            提取结果列表
        """
        if len(texts) != len(keywords):
            raise ValueError("文本列表和关键词列表长度必须相同")
        
        tasks = [self.extract(text, keyword) for text, keyword in zip(texts, keywords)]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close(self):
        """关闭客户端"""
        try:
            if self.client:
                await self.client.aclose()
                self.client = None
            
            self._is_initialized = False
            logger.info("Ollama 客户端已关闭")
            
        except Exception as e:
            logger.error(f"关闭 Ollama 客户端时出错: {e}")
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 全局 Ollama 实例
_ollama_instance: Optional[OllamaClient] = None


async def get_ollama() -> OllamaClient:
    """获取全局 Ollama 实例"""
    global _ollama_instance
    if _ollama_instance is None:
        _ollama_instance = OllamaClient()
        await _ollama_instance.initialize()
    return _ollama_instance


async def sub_brain_summarize(text: str) -> str:
    """文本摘要（便捷函数）"""
    ollama = await get_ollama()
    return await ollama.summarize(text)


async def sub_brain_extract(text: str, keyword: str) -> str:
    """关键词提取（便捷函数）"""
    ollama = await get_ollama()
    return await ollama.extract(text, keyword)


async def close_ollama():
    """关闭 Ollama 客户端（便捷函数）"""
    global _ollama_instance
    if _ollama_instance:
        await _ollama_instance.close()
        _ollama_instance = None


async def test_ollama_connection() -> Dict[str, Any]:
    """测试 Ollama 连接"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://127.0.0.1:11434/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = [model["name"] for model in data.get("models", [])]
            
            return {
                "status": "connected",
                "models": models,
                "model_count": len(models)
            }
            
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "models": [],
            "model_count": 0
        }


# 预定义的提示模板
SUMMARIZE_TEMPLATES = {
    "research": """你是一个研究助手。请把以下学术内容压缩成结构化大纲。

要求：
1. 提取 3-5 个核心研究结论
2. 列出所有关键技术术语和方法
3. 指出研究的局限性和未来方向
4. 使用中文输出

输出格式：
【研究结论】
1. 结论1
2. 结论2

【关键技术】
- 技术1
- 技术2

【局限与展望】
- 局限性1
- 未来方向1""",
    
    "news": """你是一个新闻分析助手。请把以下新闻内容压缩成结构化摘要。

要求：
1. 提取 3-5 个关键事实
2. 列出涉及的主要人物、地点、机构
3. 指出事件的时间线和影响
4. 使用中文输出

输出格式：
【关键事实】
1. 事实1
2. 事实2

【主要要素】
- 人物/地点/机构1
- 人物/地点/机构2

【时间线与影响】
- 时间点1: 事件1
- 影响1""",
    
    "technical": """你是一个技术文档助手。请把以下技术内容压缩成结构化摘要。

要求：
1. 提取 3-5 个核心技术要点
2. 列出所有技术术语和概念
3. 指出实现方法和注意事项
4. 使用中文输出

输出格式：
【技术要点】
1. 要点1
2. 要点2

【技术术语】
- 术语1
- 术语2

【实现与注意】
- 方法1
- 注意事项1"""
}


async def summarize_with_template(text: str, template_type: str = "research") -> str:
    """
    使用预定义模板进行摘要
    
    参数:
        text: 需要摘要的文本
        template_type: 模板类型（research/news/technical）
        
    返回:
        结构化摘要
    """
    if template_type not in SUMMARIZE_TEMPLATES:
        raise ValueError(f"未知的模板类型: {template_type}，可用类型: {list(SUMMARIZE_TEMPLATES.keys())}")
    
    ollama = await get_ollama()
    
    # 限制文本长度
    max_length = get_max_text_length()
    if len(text) > max_length:
        text = text[:max_length]
        logger.info(f"文本过长，截取前 {max_length} 字符")
    
    # 使用模板
    system_prompt = SUMMARIZE_TEMPLATES[template_type]
    user_prompt = f"请对以下内容生成结构化摘要：\n\n{text}"
    
    try:
        # 临时修改模型配置以使用模板
        original_model = ollama.model
        
        # 调用 API
        response = await ollama._ollama_complete(user_prompt, system=system_prompt)
        
        logger.info(f"使用模板 '{template_type}' 摘要完成")
        return response
        
    except Exception as e:
        logger.error(f"使用模板摘要失败: {e}")
        return f"使用模板摘要失败: {str(e)}"