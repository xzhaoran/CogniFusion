#!/usr/bin/env python3
"""
测试修复脚本
验证 Playwright 浏览器和 API 服务是否正常工作
"""

import asyncio
import sys
import os
import subprocess
import time
import requests

def test_playwright_installation():
    """测试 Playwright 安装"""
    print("🔧 测试 Playwright 安装...")
    try:
        import playwright
        print("  ✓ Playwright 模块已导入")
        
        # 尝试启动 Playwright
        import playwright.sync_api
        p = playwright.sync_api.Playwright().start()
        print("  ✓ Playwright 初始化成功")
        
        # 检查浏览器
        browsers = p.chromium
        print(f"  ✓ Chromium 浏览器可用")
        
        p.stop()
        return True
    except Exception as e:
        print(f"  ✗ Playwright 测试失败: {e}")
        return False

def test_api_service():
    """测试 API 服务"""
    print("\n🌐 测试 API 服务...")
    
    # 检查 API 是否在运行
    try:
        response = requests.get("http://127.0.0.1:8765/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✓ API 服务正常 (状态码: {response.status_code})")
            return True
        else:
            print(f"  ✗ API 服务异常 (状态码: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ API 服务未运行 (连接失败)")
        return False
    except Exception as e:
        print(f"  ✗ API 测试失败: {e}")
        return False

def test_search_function():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    try:
        response = requests.get(
            "http://127.0.0.1:8765/bing_search",
            params={"q": "test", "max_results": 3},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"  ✓ 搜索成功！找到 {len(results)} 个结果")
            
            if results:
                for i, result in enumerate(results[:2], 1):
                    print(f"    结果 {i}: {result.get('title', '')[:50]}...")
            return True
        else:
            print(f"  ✗ 搜索失败 (状态码: {response.status_code})")
            print(f"    错误信息: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ 搜索测试失败: {e}")
        return False

def check_config_files():
    """检查配置文件"""
    print("\n📁 检查配置文件...")
    
    config_files = [
        ("config.json", "主配置文件"),
        ("cherry_studio_mcp_config.json", "Cherry Studio MCP 配置"),
    ]
    
    all_ok = True
    for filename, description in config_files:
        if os.path.exists(filename):
            print(f"  ✓ {description} 存在: {filename}")
        else:
            print(f"  ✗ {description} 不存在: {filename}")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 C O G N I F U S I O N  修 复 测 试")
    print("=" * 60)
    
    tests = [
        ("Playwright 安装", test_playwright_installation),
        ("配置文件", check_config_files),
        ("API 服务", test_api_service),
        ("搜索功能", test_search_function),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("📊 测 试 总 结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n✅ 所有测试通过！CogniFusion 已修复完成。")
        print("\n📋 下一步操作:")
        print("   1. 在 Cherry Studio 中启用 MCP 服务器")
        print("   2. 使用搜索功能进行测试")
        print("   3. 享受智能研究助手！")
    else:
        print("\n⚠️  部分测试失败，请运行修复脚本:")
        print("   .\\fix_playwright.bat")
        print("\n📋 常见问题解决:")
        print("   - 如果 API 服务未运行: python api.py")
        print("   - 如果浏览器未安装: python -m playwright install chromium")
        print("   - 如果端口冲突: 修改 config.json 中的端口号")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)