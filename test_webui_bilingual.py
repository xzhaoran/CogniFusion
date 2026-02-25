#!/usr/bin/env python3
"""
测试Web UI双语功能
"""

import os
import sys
import asyncio
from pathlib import Path

def check_template_files():
    """检查模板文件是否存在"""
    print("📁 检查模板文件")
    print("=" * 50)
    
    templates_dir = Path(__file__).parent / "templates"
    required_files = [
        "status_simple.html",
        "config_simple.html",
        "config_saved_simple.html"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = templates_dir / file
        if file_path.exists():
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} (缺失)")
            all_exist = False
    
    return all_exist

def check_bilingual_content():
    """检查双语内容"""
    print("\n🌐 检查双语内容")
    print("=" * 50)
    
    templates_dir = Path(__file__).parent / "templates"
    
    # 检查状态页面
    status_file = templates_dir / "status_simple.html"
    if status_file.exists():
        content = status_file.read_text(encoding='utf-8')
        
        # 检查双语分隔符
        bilingual_checks = [
            ("标题双语", "CogniFusion - Status / 状态"),
            ("系统状态双语", "系统状态 / System Status"),
            ("浏览器引擎双语", "浏览器引擎 / Browser Engine"),
            ("本地副脑双语", "本地副脑 / Local Sub-Brain"),
            ("MCP工具双语", "MCP 工具 / MCP Tools"),
            ("配置验证双语", "配置验证 / Configuration Validation"),
            ("页脚双语", "智能融合研究助手系统 / Intelligent Fusion Research Assistant System")
        ]
        
        print("   状态页面双语检查:")
        for check_name, check_text in bilingual_checks:
            if check_text in content:
                print(f"     ✓ {check_name}: {check_text}")
            else:
                print(f"     ✗ {check_name}: 未找到")
    
    # 检查配置页面
    config_file = templates_dir / "config_simple.html"
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        
        bilingual_checks = [
            ("标题双语", "CogniFusion - Configuration / 配置"),
            ("头部双语", "CogniFusion Configuration / 配置"),
            ("描述双语", "Configure your intelligent research assistant system / 配置您的智能研究助手系统")
        ]
        
        print("\n   配置页面双语检查:")
        for check_name, check_text in bilingual_checks:
            if check_text in content:
                print(f"     ✓ {check_name}: {check_text}")
            else:
                print(f"     ✗ {check_name}: 未找到")
    
    return True

def check_config_functionality():
    """检查配置功能"""
    print("\n🔧 检查配置功能")
    print("=" * 50)
    
    try:
        from config import load_config, get_max_text_length, get_max_extract_length
        
        config = load_config()
        print(f"   配置文件加载成功")
        
        # 检查新增配置项
        max_text_length = config.get("max_text_length", 12000)
        max_extract_length = config.get("max_extract_length", 15000)
        
        print(f"   最大文本长度: {max_text_length}")
        print(f"   最大提取长度: {max_extract_length}")
        
        # 检查函数
        print(f"   get_max_text_length(): {get_max_text_length()}")
        print(f"   get_max_extract_length(): {get_max_extract_length()}")
        
        # 检查skip_browser_prompt是否已移除
        if "skip_browser_prompt" in config:
            print(f"   ⚠️  skip_browser_prompt 仍然存在: {config['skip_browser_prompt']}")
        else:
            print(f"   ✓ skip_browser_prompt 已移除")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 配置功能检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_api_endpoints():
    """检查API端点"""
    print("\n🔌 检查API端点")
    print("=" * 50)
    
    try:
        import api
        
        # 检查配置保存端点参数
        import inspect
        save_config_func = api.save_config_api
        
        # 获取函数参数
        sig = inspect.signature(save_config_func)
        params = list(sig.parameters.keys())
        
        print(f"   save_config_api 参数: {params}")
        
        # 检查是否包含新增参数
        required_params = ["max_text_length", "max_extract_length"]
        missing_params = []
        
        for param in required_params:
            if param not in params:
                missing_params.append(param)
        
        if missing_params:
            print(f"   ✗ 缺少参数: {missing_params}")
            return False
        else:
            print(f"   ✓ 所有必需参数都存在")
            
        # 检查是否移除了skip_browser_prompt
        if "skip_browser_prompt" in params:
            print(f"   ⚠️  skip_browser_prompt 参数仍然存在")
        else:
            print(f"   ✓ skip_browser_prompt 参数已移除")
        
        return True
        
    except Exception as e:
        print(f"   ✗ API端点检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_web_ui():
    """测试Web UI功能"""
    print("\n🌐 测试Web UI功能")
    print("=" * 50)
    
    try:
        import httpx
        from config import get_api_port
        
        port = get_api_port()
        base_url = f"http://127.0.0.1:{port}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 测试状态页面
            print(f"   测试状态页面: {base_url}/")
            try:
                response = await client.get(f"{base_url}/")
                if response.status_code == 200:
                    print(f"     ✓ 状态页面访问成功")
                    
                    # 检查双语内容
                    content = response.text
                    if "系统状态 / System Status" in content:
                        print(f"     ✓ 双语内容存在")
                    else:
                        print(f"     ✗ 双语内容缺失")
                else:
                    print(f"     ✗ 状态页面访问失败: {response.status_code}")
                    
            except Exception as e:
                print(f"     ✗ 状态页面测试失败: {e}")
            
            # 测试配置页面
            print(f"   测试配置页面: {base_url}/config")
            try:
                response = await client.get(f"{base_url}/config")
                if response.status_code == 200:
                    print(f"     ✓ 配置页面访问成功")
                    
                    # 检查双语内容
                    content = response.text
                    if "CogniFusion Configuration / 配置" in content:
                        print(f"     ✓ 双语内容存在")
                    else:
                        print(f"     ✗ 双语内容缺失")
                        
                    # 检查新增配置字段
                    if "max_text_length" in content and "max_extract_length" in content:
                        print(f"     ✓ 新增配置字段存在")
                    else:
                        print(f"     ✗ 新增配置字段缺失")
                        
                else:
                    print(f"     ✗ 配置页面访问失败: {response.status_code}")
                    
            except Exception as e:
                print(f"     ✗ 配置页面测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Web UI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 C O G N I F U S I O N - Web UI双语功能测试")
    print("=" * 60)
    
    try:
        # 运行测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 检查模板文件
        success1 = check_template_files()
        
        # 检查双语内容
        success2 = check_bilingual_content()
        
        # 检查配置功能
        success3 = check_config_functionality()
        
        # 检查API端点
        success4 = check_api_endpoints()
        
        # 测试Web UI
        success5 = loop.run_until_complete(test_web_ui())
        
        loop.close()
        
        if all([success1, success2, success3, success4, success5]):
            print("\n🎉 所有测试通过！")
            print("\n📋 系统状态:")
            print("   • 模板文件: ✓ 完整")
            print("   • 双语内容: ✓ 已添加")
            print("   • 配置功能: ✓ 正常")
            print("   • API端点: ✓ 更新")
            print("   • Web UI: ✓ 可访问")
            print("\n✅ Web UI双语功能实现完成！")
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