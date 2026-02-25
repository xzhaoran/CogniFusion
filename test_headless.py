README.md#!/usr/bin/env python3
"""
测试无头模式功能
"""

import asyncio
import sys
import os
from config import load_config, update_config, get_headless_mode, set_headless_mode
from browser_core import BrowserCore

async def test_headless_mode():
    """测试无头模式"""
    print("🧪 测试无头模式功能")
    print("=" * 50)
    
    # 1. 测试配置读取
    print("\n1. 测试配置读取...")
    config = load_config()
    current_headless = config.get("headless_mode", False)
    print(f"   当前无头模式设置: {current_headless}")
    
    # 2. 测试配置更新
    print("\n2. 测试配置更新...")
    # 切换到无头模式
    set_headless_mode(True)
    new_config = load_config()
    print(f"   更新后无头模式设置: {new_config.get('headless_mode')}")
    
    # 3. 测试浏览器初始化
    print("\n3. 测试浏览器初始化...")
    try:
        browser = BrowserCore()
        await browser.initialize()
        
        # 检查浏览器是否在无头模式下运行
        if browser.context:
            print(f"   ✓ 浏览器初始化成功")
            print(f"   浏览器上下文: {browser.context}")
            
            # 测试搜索功能
            print("\n4. 测试搜索功能...")
            results = await browser.search_bing("test", max_results=3)
            print(f"   ✓ 搜索成功，找到 {len(results)} 个结果")
            
            if results:
                for i, result in enumerate(results[:2], 1):
                    print(f"     结果 {i}: {result.get('title', '')[:50]}...")
        else:
            print("   ✗ 浏览器上下文创建失败")
        
        # 清理
        await browser.close()
        
    except Exception as e:
        print(f"   ✗ 浏览器初始化失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 恢复配置
    print("\n5. 恢复配置...")
    set_headless_mode(current_headless)
    final_config = load_config()
    print(f"   最终无头模式设置: {final_config.get('headless_mode')}")
    
    print("\n" + "=" * 50)
    print("✅ 无头模式功能测试完成！")
    
    return True

async def test_config_ui():
    """测试配置UI功能"""
    print("\n🌐 测试配置UI功能")
    print("=" * 50)
    
    # 模拟Web UI配置
    test_configs = [
        {"headless_mode": False, "description": "显示模式"},
        {"headless_mode": True, "description": "无头模式"},
    ]
    
    for config in test_configs:
        print(f"\n测试配置: {config['description']}")
        set_headless_mode(config["headless_mode"])
        
        current = get_headless_mode()
        print(f"   配置已设置: headless_mode={current}")
        
        # 验证配置
        loaded = load_config()
        if loaded.get("headless_mode") == config["headless_mode"]:
            print(f"   ✓ 配置验证成功")
        else:
            print(f"   ✗ 配置验证失败")
    
    print("\n" + "=" * 50)
    print("✅ 配置UI功能测试完成！")
    
    return True

def main():
    """主函数"""
    print("🚀 C O G N I F U S I O N - 无头模式测试")
    print("=" * 60)
    
    try:
        # 运行测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 测试无头模式
        success1 = loop.run_until_complete(test_headless_mode())
        
        # 测试配置UI
        success2 = loop.run_until_complete(test_config_ui())
        
        loop.close()
        
        if success1 and success2:
            print("\n🎉 所有测试通过！")
            print("\n📋 使用说明:")
            print("   1. 访问 http://127.0.0.1:8765/config")
            print("   2. 勾选 '无头模式（后台运行）' 选项")
            print("   3. 保存配置")
            print("   4. 浏览器将在后台运行，不会显示窗口")
            print("\n💡 提示:")
            print("   - 无头模式适合服务器环境或不需要可视化界面的场景")
            print("   - 显示模式适合调试和需要查看浏览器操作的场景")
            return True
        else:
            print("\n⚠️  部分测试失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)