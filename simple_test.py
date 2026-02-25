#!/usr/bin/env python3
"""
简单的Python测试脚本
"""
import sys

def main():
    print("=" * 50)
    print("Python 环境测试")
    print("=" * 50)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查Python版本是否满足要求
    version_info = sys.version_info
    print(f"主版本: {version_info.major}")
    print(f"次版本: {version_info.minor}")
    print(f"微版本: {version_info.micro}")
    
    # 检查是否满足要求
    if version_info.major == 3 and version_info.minor >= 8:
        print("✅ Python版本满足要求 (3.8+)")
    else:
        print(f"❌ Python版本不满足要求: 需要3.8+, 当前{version_info.major}.{version_info.minor}")
    
    # 尝试导入一些基本模块
    print("\n尝试导入基本模块:")
    modules = ["os", "sys", "json", "asyncio", "typing"]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"测试失败: {e}")
        sys.exit(1)