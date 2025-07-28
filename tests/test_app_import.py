#!/usr/bin/env python3
"""
测试app导入
"""
import sys
import os

# 添加API目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'API'))

try:
    print("测试app导入...")
    import app
    print("✅ app导入成功")
    print(f"Flask应用: {app.app}")
    
    # 列出路由
    print("路由列表:")
    for rule in app.app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
except Exception as e:
    print(f"❌ app导入失败: {e}")
    import traceback
    traceback.print_exc()
