#!/usr/bin/env python3
"""
CogniFusion 环境检查脚本
检查系统环境是否满足项目要求
"""
import sys
import os
import subprocess
import platform

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def check_python():
    """检查Python环境"""
    print_header("检查 Python 环境")
    
    try:
        # 检查Python版本
        python_version = sys.version_info
        print(f"✅ Python 版本: {sys.version}")
        
        if python_version.major == 3 and python_version.minor >= 8:
            print("✅ Python 版本满足要求 (3.8+)")
        else:
            print(f"❌ Python 版本不满足要求: 需要 3.8+, 当前 {python_version.major}.{python_version.minor}")
            return False
        
        # 检查Python路径
        python_exe = sys.executable
        print(f"Python 可执行文件: {python_exe}")
        
        return True
    except Exception as e:
        print(f"❌ Python 检查失败: {e}")
        return False

def check_pip():
    """检查pip"""
    print_header("检查 pip")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ pip 已安装: {result.stdout.strip()}")
            
            # 检查pip版本
            version_line = result.stdout.strip()
            print(f"pip 信息: {version_line}")
            
            return True
        else:
            print("❌ pip 未安装或不可用")
            print(f"错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ pip 检查失败: {e}")
        return False

def check_system():
    """检查系统信息"""
    print_header("检查系统信息")
    
    try:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        
        print(f"操作系统: {system} {release} ({version})")
        print(f"系统架构: {machine}")
        print(f"处理器: {platform.processor()}")
        
        # 检查内存（仅Windows）
        if system == "Windows":
            try:
                import psutil
                memory = psutil.virtual_memory()
                total_gb = memory.total / (1024**3)
                available_gb = memory.available / (1024**3)
                print(f"内存: {total_gb:.1f} GB (可用: {available_gb:.1f} GB)")
                
                if total_gb >= 8:
                    print("✅ 内存满足要求 (8GB+)")
                else:
                    print(f"⚠️  内存可能不足: {total_gb:.1f} GB < 8GB")
            except ImportError:
                print("⚠️  无法检查内存信息，请安装 psutil: pip install psutil")
        
        return True
    except Exception as e:
        print(f"⚠️  系统检查失败: {e}")
        return True  # 系统检查不是关键

def check_dependencies():
    """检查关键依赖"""
    print_header("检查关键依赖")
    
    dependencies = [
        ("asyncio", "异步编程"),
        ("aiohttp", "HTTP客户端"),
        ("playwright", "浏览器自动化"),
        ("fastapi", "Web框架"),
        ("httpx", "HTTP客户端"),
        ("pydantic", "数据验证"),
    ]
    
    all_ok = True
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name}) 可用")
        except ImportError as e:
            print(f"❌ {description} ({module_name}) 未安装: {e}")
            all_ok = False
    
    return all_ok

def check_project_files():
    """检查项目文件"""
    print_header("检查项目文件")
    
    required_files = [
        "requirements.txt",
        "config.example.json",
        "main.py",
        "api.py",
        "browser_core.py",
        "ollama_client.py",
        "mcp_server.py",
        "config.py",
        "run.bat",
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print("=" * 60)
    print("CogniFusion 环境检查")
    print("=" * 60)
    
    checks = [
        ("Python环境", check_python),
        ("pip包管理器", check_pip),
        ("系统信息", check_system),
        ("关键依赖", check_dependencies),
        ("项目文件", check_project_files),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 检查: {check_name}")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ 检查 {check_name} 异常: {e}")
            results.append((check_name, False))
    
    # 输出总结
    print_header("检查结果总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
    
    print(f"\n总计: {total} 项检查")
    print(f"通过: {passed} 项")
    print(f"失败: {total - passed} 项")
    
    if passed == total:
        print("\n🎉 所有检查通过！环境已准备好运行 CogniFusion")
        print("\n下一步:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 安装浏览器: playwright install chromium")
        print("3. 启动系统: run.bat")
        return 0
    else:
        print("\n⚠️  有检查失败，请解决以下问题:")
        for check_name, result in results:
            if not result:
                print(f"  - {check_name}")
        
        print("\n建议:")
        print("1. 确保Python 3.8+已安装并添加到PATH")
        print("2. 运行: python -m pip install --upgrade pip")
        print("3. 安装缺失的依赖")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        sys.exit(1)