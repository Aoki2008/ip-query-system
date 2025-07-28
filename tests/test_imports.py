#!/usr/bin/env python3
"""
测试导入
"""
import sys
import os

# 添加API目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'API'))

try:
    print("测试基础导入...")
    from utils.monitoring import metrics_collector, alert_manager, health_checker
    print("✅ monitoring模块导入成功")
    
    print("测试app导入...")
    import app
    print("✅ app模块导入成功")
    
    print("测试Flask应用...")
    print(f"Flask应用: {app.app}")
    print(f"路由数量: {len(app.app.url_map._rules)}")
    
    # 列出所有路由
    print("所有路由:")
    for rule in app.app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
