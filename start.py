#!/usr/bin/env python3
"""
CogniFusion 简化启动脚本
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main
    print("=" * 60)
    print("启动 CogniFusion 系统...")
    print("=" * 60)
    main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请确保已安装所有依赖:")
    print("1. 运行 fix_dependencies.bat")
    print("2. 或手动安装: pip install -r requirements_simple.txt")
    input("\n按 Enter 键退出...")
    sys.exit(1)
except Exception as e:
    print(f"启动错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按 Enter 键退出...")
    sys.exit(1)