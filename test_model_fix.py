#!/usr/bin/env python3
"""
测试模型名称修复
"""

import asyncio
import sys
from ollama_client import test_ollama_connection, get_ollama

async def test_model_detection():
    """测试模型检测功能"""
    print("🧪 测试模型检测功能")
    print("=" * 50)
    
    # 1. 测试连接
    print("\n1. 测试 Ollama 连接...")
    connection_status = await test_ollama_connection()
    
    if connection_status["status"] == "connected":
        print(f"   ✓ Ollama 连接成功")
        print(f"   可用模型: {connection_status['models']}")
        print(f"   模型数量: {connection_status['model_count']}")
    else:
        print(f"   ✗ Ollama 连接失败: {connection_status['error']}")
        return False
    
    # 2. 测试客户端初始化
    print("\n2. 测试 Ollama 客户端初始化...")
    try:
        ollama = await get_ollama()
        print(f"   ✓ Ollama 客户端初始化成功")
        print(f"   当前模型: {ollama.model}")
        print(f"   API 地址: {ollama.api_url}")
        
        # 3. 测试文本摘要
        print("\n3. 测试文本摘要功能...")
        test_text = """钠离子电池是一种新型的电池技术，与锂离子电池相比具有成本低、资源丰富的优势。
钠离子电池的工作原理与锂离子电池类似，都是通过离子在正负极之间的迁移来实现充放电。
钠离子电池的优点是钠资源丰富、成本低、安全性好，缺点是能量密度较低、循环寿命较短。
目前钠离子电池主要应用于储能系统、低速电动车等领域。"""
        
        summary = await ollama.summarize(test_text)
        print(f"   ✓ 文本摘要成功")
        print(f"   摘要长度: {len(summary)} 字符")
        print(f"   摘要内容前100字符: {summary[:100]}...")
        
        # 4. 测试关键词提取
        print("\n4. 测试关键词提取功能...")
        extracts = await ollama.extract(test_text, "钠离子电池")
        print(f"   ✓ 关键词提取成功")
        print(f"   提取长度: {len(extracts)} 字符")
        print(f"   提取内容前100字符: {extracts[:100]}...")
        
        # 清理
        await ollama.close()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_config_loading():
    """测试配置加载"""
    print("\n🔧 测试配置加载")
    print("=" * 50)
    
    from config import load_config, get_ollama_config
    
    try:
        # 加载配置
        config = load_config()
        print(f"   配置文件加载成功")
        print(f"   模型配置: {config.get('ollama_model')}")
        
        # 获取 Ollama 配置
        ollama_config = get_ollama_config()
        print(f"   Ollama 配置: {ollama_config}")
        
        # 检查模型名称是否有空格
        model_name = config.get('ollama_model', '')
        if model_name != model_name.strip():
            print(f"   ⚠️  模型名称有空格问题: '{model_name}'")
            print(f"      清理后: '{model_name.strip()}'")
        else:
            print(f"   ✓ 模型名称格式正确")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 配置加载失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 C O G N I F U S I O N - 模型检测修复测试")
    print("=" * 60)
    
    try:
        # 运行测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 测试配置加载
        success1 = loop.run_until_complete(test_config_loading())
        
        # 测试模型检测
        success2 = loop.run_until_complete(test_model_detection())
        
        loop.close()
        
        if success1 and success2:
            print("\n🎉 所有测试通过！")
            print("\n📋 系统状态:")
            print("   • Ollama 连接: ✓ 正常")
            print("   • 模型检测: ✓ 正常")
            print("   • 文本处理: ✓ 正常")
            print("   • 配置加载: ✓ 正常")
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