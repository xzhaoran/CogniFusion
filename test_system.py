#!/usr/bin/env python3
"""
CogniFusion 系统测试脚本
"""
import sys
import asyncio
from pathlib import Path

def test_imports():
    """测试所有核心模块导入"""
    print("=" * 60)
    print("测试模块导入")
    print("=" * 60)
    
    modules = [
        ("fastapi", "Web框架"),
        ("playwright", "浏览器自动化"),
        ("httpx", "HTTP客户端"),
        ("uvicorn", "ASGI服务器"),
        ("aiohttp", "异步HTTP"),
        ("pydantic", "数据验证"),
        ("loguru", "日志系统"),
        ("aiofiles", "异步文件操作"),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name:15} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:15} - {description}: {e}")
            all_ok = False
    
    return all_ok

def test_playwright():
    """测试Playwright浏览器"""
    print("\n" + "=" * 60)
    print("测试Playwright浏览器")
    print("=" * 60)
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            print("✅ Playwright浏览器启动成功")
            browser.close()
        return True
    except Exception as e:
        print(f"❌ Playwright测试失败: {e}")
        return False

def test_fastapi():
    """测试FastAPI"""
    print("\n" + "=" * 60)
    print("测试FastAPI")
    print("=" * 60)
    
    try:
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        print("✅ FastAPI应用创建成功")
        return True
    except Exception as e:
        print(f"❌ FastAPI测试失败: {e}")
        return False

def test_config_files():
    """测试配置文件"""
    print("\n" + "=" * 60)
    print("测试配置文件")
    print("=" * 60)
    
    required_files = [
        "config.py",
        "browser_core.py", 
        "ollama_client.py",
        "api.py",
        "main.py",
        "mcp_server.py",
        "run.bat",
        "requirements_simple.txt",
    ]
    
    all_ok = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name:20} - 存在")
        else:
            print(f"❌ {file_name:20} - 不存在")
            all_ok = False
    
    return all_ok

def test_portable_python():
    """测试便携式Python"""
    print("\n" + "=" * 60)
    print("测试便携式Python")
    print("=" * 60)
    
    python_exe = Path("python/python.exe")
    if python_exe.exists():
        print(f"✅ 便携式Python: {python_exe}")
        print(f"   大小: {python_exe.stat().st_size / 1024 / 1024:.1f} MB")
        
        # 检查pip
        pip_exe = Path("python/Scripts/pip.exe")
        if pip_exe.exists():
            print(f"✅ pip: {pip_exe}")
        else:
            print(f"❌ pip不存在")
            return False
        return True
    else:
        print("❌ 便携式Python不存在")
        return False

async def test_async():
    """测试异步功能"""
    print("\n" + "=" * 60)
    print("测试异步功能")
    print("=" * 60)
    
    try:
        import asyncio
        import httpx
        
        async def test_http():
            async with httpx.AsyncClient() as client:
                response = await client.get("https://httpbin.org/get")
                return response.status_code
        
        status = await test_http()
        print(f"✅ 异步HTTP请求成功: 状态码 {status}")
        return True
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧠 CogniFusion 系统测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 模块导入
    results.append(("模块导入", test_imports()))
    
    # 测试2: 配置文件
    results.append(("配置文件", test_config_files()))
    
    # 测试3: 便携式Python
    results.append(("便携式Python", test_portable_python()))
    
    # 测试4: FastAPI
    results.append(("FastAPI", test_fastapi()))
    
    # 测试5: Playwright
    results.append(("Playwright", test_playwright()))
    
    # 测试6: 异步功能
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results.append(("异步功能", loop.run_until_complete(test_async())))
    loop.close()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20} - {status}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n下一步:")
        print("  1. 运行 run.bat 启动系统")
        print("  2. 按照提示配置浏览器数据目录")
        print("  3. 访问 http://localhost:8765 查看状态")
        print("  4. 配置MCP客户端使用系统")
        return 0
    else:
        print("⚠️  部分测试失败，请检查问题。")
        print("\n常见问题:")
        print("  1. 确保已运行 fix_dependencies.bat")
        print("  2. 确保便携式Python安装正确")
        print("  3. 检查网络连接")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)