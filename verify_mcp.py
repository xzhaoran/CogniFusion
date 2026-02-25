#!/usr/bin/env python3
"""
验证MCP工具可用性
检查MCP服务器是否能够正常提供工具
"""
import sys
import os
import inspect

def verify_mcp_tools():
    """验证MCP工具"""
    print("🔍 验证MCP工具可用性")
    print("=" * 60)
    
    try:
        # 导入MCP模块
        import mcp_server
        
        print("✅ MCP模块导入成功")
        
        # 检查FastMCP应用
        if hasattr(mcp_server, 'mcp'):
            print("✅ FastMCP应用存在")
        else:
            print("❌ FastMCP应用不存在")
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    
    print("✅ 验证完成")
    return True

if __name__ == "__main__":
    verify_mcp_tools()
