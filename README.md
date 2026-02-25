使用用本地浏览器，参考人类递归式搜索的本地搜索mcp服务 Using a local browser, refer to human recursive search for local search MCP services
=======
# CogniFusion - 智能融合研究助手系统

## 项目概述

CogniFusion 是一个创新的智能研究助手系统，旨在将 AI 从被动的信息"总结者"转变为主动的、像人类一样思考的"研究员"。系统通过双层思考模型（本地副脑 + 云端主脑）和真实浏览器环境，实现了零成本数据源访问和人类化探索逻辑。

**核心设计理念**：将 AI 从被动的信息"总结者"转变为主动的、像人类一样思考的"研究员"

## 🚀 快速开始

### 最简单的方式
1. **下载项目**：获取完整的项目文件
2. **双击运行**：直接点击 `run.bat` 文件
3. **完成配置**：按照首次运行的引导完成浏览器用户数据目录配置
4. **开始使用**：系统会自动打开 Web UI，开始你的研究之旅

### 运行说明
- 系统会自动启动两个服务窗口（API 服务和 MCP 服务）
- Web UI 会自动在浏览器中打开（http://127.0.0.1:8765）
- 配置页面位于 http://127.0.0.1:8765/config
- 要停止服务，分别关闭两个服务窗口即可

## 🏗️ 系统架构详解

### 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   用户界面层 (Web UI)                    │
│  • 状态监控页面 (http://127.0.0.1:8765/)                │
│  • 配置管理页面 (http://127.0.0.1:8765/config)          │
│  • 实时日志查看                                         │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    API 服务层 (FastAPI)                  │
│  • RESTful API 接口 (端口: 8765)                        │
│  • 浏览器自动化接口 (Bing搜索、网页内容提取)              │
│  • 副脑处理接口 (文本摘要、关键词提取)                    │
│  • 批量处理接口 (带缓存和会话隔离)                        │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    MCP 服务层 (FastMCP)                  │
│  • MCP 标准工具 (端口: 8000)                            │
│  • SSE 传输协议支持                                      │
│  • 工具: search, summarize_urls, ask_specific_question  │
│  • 工具: research_topic, compare_sources, get_system_status │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                   核心功能层                             │
│  • 浏览器核心 (Playwright + 真实浏览器环境)              │
│  • 副脑客户端 (Ollama 本地模型集成)                      │
│  • 缓存管理器 (Redis + 本地文件缓存)                     │
│  • 配置管理 (JSON 配置文件 + 环境变量)                   │
└─────────────────────────────────────────────────────────┘
```

## 🔧 核心技术组件

### 1. 浏览器自动化核心 (`browser_core.py`)
- **技术栈**：Playwright + Chromium
- **核心特性**：
  - 真实浏览器环境：复用用户登录状态，绕过付费墙
  - 资源优化：智能拦截图片、样式等重资源，保留核心文本
  - 会话隔离：支持多会话并行处理
  - 便携式浏览器：内置 Chromium，无需额外安装

- **关键实现**：
  ```python
  class BrowserCore:
      async def search_bing(self, query: str, max_results: int = 10)
      async def get_page_content(self, url: str, allow_interactive: bool = True)
      async def _block_heavy_resources(self, route)  # 资源拦截
      async def _extract_page_text(self, page: Page)  # 文本提取
  ```

### 2. API 服务层 (`api.py`)
- **技术栈**：FastAPI + Uvicorn
- **核心接口**：
  - `GET /bing_search` - Bing 搜索接口
  - `GET /page_content` - 网页内容提取
  - `POST /sub_brain/summarize` - 文本摘要
  - `POST /sub_brain/extract` - 关键词提取
  - `POST /batch/summarize_urls` - 批量网页摘要（带缓存）
  - `GET /config` - 配置页面
  - `GET /status` - 系统状态

- **架构特点**：
  - 异步处理：所有接口均为异步，支持高并发
  - 错误处理：完善的异常捕获和错误返回
  - 配置管理：支持运行时配置更新

### 3. MCP 服务层 (`mcp_server.py`)
- **技术栈**：FastMCP + SSE 传输协议
- **提供的工具**：
  1. `search(query, max_results=10)` - 网络搜索工具
  2. `summarize_urls(urls)` - 网页批量摘要工具
  3. `ask_specific_question(url, keyword)` - 关键词精准提取工具
  4. `research_topic(topic, depth='medium')` - 研究主题工具
  5. `compare_sources(urls, aspect='主要内容')` - 多源对比工具
  6. `get_system_status()` - 系统状态工具

- **集成能力**：
  - 支持 Claude Desktop、Cursor 等 IDE
  - SSE 传输协议，实时通信
  - 标准 MCP 协议，兼容性强

### 4. 副脑客户端 (`ollama_client.py`)
- **功能**：本地 AI 模型集成
- **支持模型**：Ollama 本地模型
- **处理能力**：
  - 文本摘要：结构化摘要生成
  - 关键词提取：精准定位关键信息
  - 隐私保护：敏感文本本地处理

### 5. 配置管理系统 (`config.py`)
- **配置方式**：JSON 配置文件 + 环境变量
- **核心配置项**：
  ```json
  {
    "user_data_dir": "浏览器用户数据目录",
    "extensions": ["浏览器扩展路径"],
    "ollama_api": "http://127.0.0.1:11434",
    "ollama_model": "",
    "api_port": 8765,
    "mcp_port": 8001,
    "max_text_length": 128000,
    "max_extract_length": 128000
  }
  ```

### 6. 缓存管理系统 (`cache_manager.py`)
- **缓存策略**：Redis + 本地文件缓存
- **缓存维度**：
  - 网页内容缓存
  - 摘要结果缓存
  - 会话隔离缓存
- **缓存失效**：智能 TTL 管理

## 🛠️ 工作流程详解

### 1. 搜索流程
```
用户查询 → MCP search() → API /bing_search → BrowserCore.search_bing()
         → 结果返回 → 格式化输出 → 用户
```

### 2. 网页摘要流程
```
URL列表 → MCP summarize_urls() → API /batch/summarize_urls()
        → 缓存检查 → 网页内容获取 → 副脑摘要 → 结果缓存
        → 格式化输出 → 用户
```

### 3. 研究主题流程
```
研究主题 → MCP research_topic() → 搜索相关结果 → 选择关键网页
        → 批量摘要 → 综合分析 → 生成研究报告 → 用户
```

## 📊 性能优化策略

### 1. 资源拦截优化
- **拦截类型**：图片、样式表、字体、媒体文件
- **保留内容**：HTML、JavaScript、文本内容
- **效果**：加载速度提升 3-5 倍

### 2. 缓存策略
- **多级缓存**：内存缓存 → Redis 缓存 → 文件缓存
- **会话隔离**：不同会话使用独立缓存空间
- **智能失效**：基于内容哈希的缓存验证

### 3. 并发处理
- **异步架构**：基于 asyncio 的完全异步设计
- **连接池**：HTTP 客户端连接池复用
- **浏览器复用**：单浏览器实例，多页面并发

## 🔌 集成与扩展

### 1. MCP 客户端集成
```json
// Claude Desktop 配置示例
{
  "mcpServers": {
    "cognifusion": {
      "isActive": false,
      "name": "cognifusion",
      "type": "stdio",
      "command": "你的下载路径\\CogniFusion2\\python\\python.exe",
      "args": [
        "你的下载路径\\CogniFusion2\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "你的下载路径\\CogniFusion2",
        "PORTABLE_MODE": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "你的下载路径\\CogniFusion2\\bin\\browsers",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "MCP_TRANSPORT": "stdio"
      },
      "installSource": "unknown"
    }
  }
}

```

### 2. API 集成
```python
# Python 客户端示例
import httpx

async def search_with_cognifusion(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:8765/bing_search",
            params={"q": query, "max_results": 10}
        )
        return response.json()
```

### 3. 自定义工具扩展
```python
# 自定义 MCP 工具示例
@mcp.tool()
async def custom_research_tool(topic: str, sources: List[str]):
    """自定义研究工具"""
    # 实现自定义逻辑
    pass
```

## ⚙️ 配置说明

### 必需配置
1. **浏览器用户数据目录**：
   - Windows: `C:\Users\YourName\AppData\Local\Google\Chrome\User Data`

2. **Ollama 配置**（可选）：
   - 安装 Ollama：https://ollama.com/
   - 下载模型：推荐ollama run svjack/Qwen3-4B-Instruct-2507-heretic:latest这种256k超长上下文的4B小模型     
   - 确保服务运行：`ollama serve`

### 可选配置
- **浏览器扩展**：添加 uBlock Origin 等扩展路径
- **端口配置**：修改 API 和 MCP 服务端口
- **文本长度限制**：调整摘要和提取的最大长度

## 🐛 故障排除

### 常见问题

1. **浏览器启动失败**
   - 检查用户数据目录是否正确
   - 确保 Chromium 未在运行
   - 尝试使用无头模式

2. **搜索无结果**
   - 检查网络连接
   - 验证 Bing 搜索可用性
   - 查看浏览器控制台日志

3. **Ollama 连接失败**
   - 确认 Ollama 服务正在运行
   - 检查 API 地址和端口
   - 验证模型名称是否正确

4. **MCP 工具不可用**
   - 确认 MCP 服务已启动
   - 检查端口 8001 是否被占用
   - 验证 MCP 客户端配置

### 日志查看
- **主日志文件**：`cognifusion.log`
- **API 服务日志**：控制台输出 + 日志文件
- **MCP 服务日志**：控制台输出
- **浏览器日志**：Playwright 调试日志

## 🔮 未来规划

### 未来计划
1.适配mac和Linux 

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 鸣谢

CogniFusion 的开发和运行离不开以下优秀的开源项目：

### 核心框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [Playwright](https://playwright.dev/) - 浏览器自动化框架
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - MCP协议实现

### AI/ML工具
- [Ollama](https://ollama.com/) - 本地LLM运行环境

### 数据处理
- [Pandas](https://pandas.pydata.org/) - 数据分析库
- [NLTK](https://www.nltk.org/) - 自然语言处理工具包

### 异步处理
- [asyncio](https://docs.python.org/3/library/asyncio.html) - Python异步IO
- [httpx](https://www.python-httpx.org/) - 异步HTTP客户端

### 开发工具
- [Black](https://black.readthedocs.io/) - 代码格式化
- [Pytest](https://docs.pytest.org/) - 测试框架

感谢所有开源项目的贡献者和维护者，正是他们的工作让这个项目成为可能。

最后，还要特别感谢[deepseek](www.deepseek.com)—— 本项目从第一行代码到最后一行文档，全部由 AI 生成。作者本人并非程序员，但借助 AI 的力量，依然能够构建出这样一套完整的系统。这标志着人机协作的新可能：**想法是人类的，实现是 AI 的，成果是大家的。**

---

**CogniFusion - 让 AI 像人类一样思考，让研究像呼吸一样自然**

CogniFusion - Intelligent Fusion Research Assistant System

Project Overview

CogniFusion is an innovative intelligent research assistant system designed to transform AI from a passive information "summarizer" into an active, human-like "researcher." Through a dual-brain model (local sub-brain + cloud main brain) and a real browser environment, it achieves zero-cost data source access and human-like exploration logic.

Core Design Philosophy: Transform AI from a passive information "summarizer" into an active, human-like "researcher"

🚀 Quick Start

Easiest Way

1. Download the project: Get the complete project files
2. Double-click to run: Directly click the run.bat file
3. Complete configuration: Follow the first-run guide to configure the browser user data directory
4. Start using: The system will automatically open the Web UI, and you can begin your research journey

Running Instructions

· The system will automatically start two service windows (API service and MCP service)
· The Web UI will automatically open in your browser (http://127.0.0.1:8765)
· The configuration page is at http://127.0.0.1:8765/config
· To stop the service, simply close the two service windows

🏗️ System Architecture

Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  User Interface Layer (Web UI)          │
│  • Status Monitoring Page (http://127.0.0.1:8765/)      │
│  • Configuration Management Page (http://127.0.0.1:8765/config)│
│  • Real-time Log Viewer                                  │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    API Service Layer (FastAPI)           │
│  • RESTful API Interface (Port: 8765)                    │
│  • Browser Automation Interface (Bing search, webpage content extraction)│
│  • Sub-brain Processing Interface (text summarization, keyword extraction)│
│  • Batch Processing Interface (with caching and session isolation)│
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    MCP Service Layer (FastMCP)           │
│  • MCP Standard Tools (Port: 8000)                       │
│  • SSE Transport Protocol Support                         │
│  • Tools: search, summarize_urls, ask_specific_question  │
│  • Tools: research_topic, compare_sources, get_system_status │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                   Core Functional Layer                  │
│  • Browser Core (Playwright + Real Browser Environment)  │
│  • Sub-brain Client (Ollama Local Model Integration)     │
│  • Cache Manager (Redis + Local File Cache)              │
│  • Configuration Management (JSON config file + environment variables)│
└─────────────────────────────────────────────────────────┘
```

🔧 Core Technology Components

1. Browser Automation Core (browser_core.py)

· Tech Stack: Playwright + Chromium
· Core Features:
  · Real browser environment: Reuses user login state, bypasses paywalls
  · Resource optimization: Intelligently blocks heavy resources like images and stylesheets, retains core text
  · Session isolation: Supports parallel processing with multiple sessions
  · Portable browser: Built-in Chromium, no additional installation required
· Key Implementation:
  ```python
  class BrowserCore:
      async def search_bing(self, query: str, max_results: int = 10)
      async def get_page_content(self, url: str, allow_interactive: bool = True)
      async def _block_heavy_resources(self, route)  # Resource blocking
      async def _extract_page_text(self, page: Page)  # Text extraction
  ```

2. API Service Layer (api.py)

· Tech Stack: FastAPI + Uvicorn
· Core Endpoints:
  · GET /bing_search - Bing search endpoint
  · GET /page_content - Webpage content extraction
  · POST /sub_brain/summarize - Text summarization
  · POST /sub_brain/extract - Keyword extraction
  · POST /batch/summarize_urls - Batch webpage summarization (with caching)
  · GET /config - Configuration page
  · GET /status - System status
· Architecture Features:
  · Asynchronous processing: All endpoints are async, supporting high concurrency
  · Error handling: Comprehensive exception capture and error responses
  · Configuration management: Supports runtime configuration updates

3. MCP Service Layer (mcp_server.py)

· Tech Stack: FastMCP + SSE Transport Protocol
· Provided Tools:
  1. search(query, max_results=10) - Web search tool
  2. summarize_urls(urls) - Batch webpage summarization tool
  3. ask_specific_question(url, keyword) - Precise keyword extraction tool
  4. research_topic(topic, depth='medium') - Topic research tool
  5. compare_sources(urls, aspect='main content') - Multi-source comparison tool
  6. get_system_status() - System status tool
· Integration Capabilities:
  · Supports Claude Desktop, Cursor, and other IDEs
  · SSE transport protocol, real-time communication
  · Standard MCP protocol, strong compatibility

4. Sub-brain Client (ollama_client.py)

· Function: Local AI model integration
· Supported Models: Ollama local models
· Processing Capabilities:
  · Text summarization: Structured summary generation
  · Keyword extraction: Precise identification of key information
  · Privacy protection: Sensitive text processed locally

5. Configuration Management System (config.py)

· Configuration Method: JSON config file + environment variables
· Core Configuration Items:
  ```json
  {
    "user_data_dir": "Browser user data directory",
    "extensions": ["Browser extension paths"],
    "ollama_api": "http://127.0.0.1:11434",
    "ollama_model": "",
    "api_port": 8765,
    "mcp_port": 8001,
    "max_text_length": 128000,
    "max_extract_length": 128000
  }
  ```

6. Cache Management System (cache_manager.py)

· Cache Strategy: Redis + Local file cache
· Cache Dimensions:
  · Webpage content cache
  · Summarization result cache
  · Session isolation cache
· Cache Invalidation: Intelligent TTL management

🛠️ Workflow Details

1. Search Workflow

```
User query → MCP search() → API /bing_search → BrowserCore.search_bing()
         → Return results → Format output → User
```

2. Webpage Summarization Workflow

```
URL list → MCP summarize_urls() → API /batch/summarize_urls()
        → Cache check → Fetch webpage content → Sub-brain summarization → Cache results
        → Format output → User
```

3. Topic Research Workflow

```
Research topic → MCP research_topic() → Search related results → Select key webpages
        → Batch summarization → Comprehensive analysis → Generate research report → User
```

📊 Performance Optimization Strategies

1. Resource Blocking Optimization

· Blocked Types: Images, stylesheets, fonts, media files
· Retained Content: HTML, JavaScript, text content
· Effect: 3-5x faster loading

2. Cache Strategy

· Multi-level Cache: Memory cache → Redis cache → File cache
· Session Isolation: Different sessions use independent cache spaces
· Intelligent Invalidation: Content hash-based cache validation

3. Concurrency Handling

· Asynchronous Architecture: Fully async design based on asyncio
· Connection Pool: HTTP client connection pooling
· Browser Reuse: Single browser instance, multiple concurrent pages

🔌 Integration and Extension

1. MCP Client Integration

```json
// Claude Desktop configuration example
{
  "mcpServers": {
    "cognifusion": {
      "isActive": false,
      "name": "cognifusion",
      "type": "stdio",
      "command": "your_download_path\\CogniFusion2\\python\\python.exe",
      "args": [
        "your_download_path\\CogniFusion2\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "your_download_path\\CogniFusion2",
        "PORTABLE_MODE": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "your_download_path\\CogniFusion2\\bin\\browsers",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "MCP_TRANSPORT": "stdio"
      },
      "installSource": "unknown"
    }
  }
}
```

2. API Integration

```python
# Python client example
import httpx

async def search_with_cognifusion(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:8765/bing_search",
            params={"q": query, "max_results": 10}
        )
        return response.json()
```

3. Custom Tool Extension

```python
# Custom MCP tool example
@mcp.tool()
async def custom_research_tool(topic: str, sources: List[str]):
    """Custom research tool"""
    # Implement custom logic
    pass
```

⚙️ Configuration Instructions

Required Configuration

1. Browser User Data Directory:
   · Windows: C:\Users\YourName\AppData\Local\Google\Chrome\User Data
2. Ollama Configuration (optional):
   · Install Ollama: https://ollama.com/
   · Download model: Recommended: ollama run svjack/Qwen3-4B-Instruct-2507-heretic:latest (a 4B small model with 256k ultra-long context)
   · Ensure service is running: ollama serve

Optional Configuration

· Browser Extensions: Add paths for extensions like uBlock Origin
· Port Configuration: Modify API and MCP service ports
· Text Length Limits: Adjust maximum lengths for summarization and extraction

🐛 Troubleshooting

Common Issues

1. Browser fails to start
   · Check if the user data directory is correct
   · Ensure Chromium is not already running
   · Try headless mode
2. No search results
   · Check network connection
   · Verify Bing search availability
   · Check browser console logs
3. Ollama connection failure
   · Confirm Ollama service is running
   · Check API address and port
   · Verify model name is correct
4. MCP tools unavailable
   · Confirm MCP service is started
   · Check if port 8001 is occupied
   · Verify MCP client configuration

Log Viewing

· Main log file: cognifusion.log
· API service logs: Console output + log file
· MCP service logs: Console output
· Browser logs: Playwright debug logs

🔮 Future Plans

Upcoming Plans

1. Adapt for macOS and Linux

📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

🙏 Acknowledgements

The development and operation of CogniFusion rely on the following excellent open-source projects:

Core Frameworks

· FastAPI - Modern, fast web framework
· Playwright - Browser automation framework
· FastMCP - MCP protocol implementation

AI/ML Tools

· Ollama - Local LLM runtime environment

Data Processing

· Pandas - Data analysis library
· NLTK - Natural language processing toolkit

Asynchronous Processing

· asyncio - Python asynchronous I/O
· httpx - Asynchronous HTTP client

Development Tools

· Black - Code formatter
· Pytest - Testing framework

Thank you to all contributors and maintainers of open-source projects; their work makes this project possible.

Finally, a special thanks to DeepSeek — from the first line of code to the last line of documentation, this entire project was generated by AI. The author is not a programmer, but with the power of AI, they were able to build such a complete system. This marks a new possibility for human-AI collaboration: Ideas are human, implementation is AI, and the成果 belong to everyone.

---

<<<<<<< HEAD
CogniFusion - Let AI think like humans, let research be as natural as breathing
=======
CogniFusion - Let AI think like humans, let research be as natural as breathin
>>>>>>> 62a0a326baa6b7fadb482fee4afb9d4456d02845
