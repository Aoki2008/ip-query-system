#!/usr/bin/env python3
"""
调试app模块加载
"""
import sys
import os

# 添加API目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'API'))

try:
    print("开始导入app模块...")
    
    # 逐步导入
    print("1. 导入基础模块...")
    from flask import Flask
    print("   ✅ Flask导入成功")
    
    print("2. 导入工具模块...")
    from utils.logger import app_logger
    print("   ✅ logger导入成功")
    
    print("3. 导入监控模块...")
    from utils.monitoring import metrics_collector, alert_manager, health_checker
    print("   ✅ monitoring导入成功")
    
    print("4. 导入app模块...")
    import app
    print("   ✅ app模块导入成功")
    
    print("5. 检查Flask应用...")
    print(f"   Flask应用: {app.app}")
    print(f"   应用名称: {app.app.name}")
    
    print("6. 检查路由...")
    routes = []
    for rule in app.app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    
    print(f"   路由数量: {len(routes)}")
    for route in routes:
        print(f"   {route}")
    
    # 检查监控路由是否存在
    monitoring_routes = [r for r in routes if 'monitoring' in r]
    print(f"\n监控路由数量: {len(monitoring_routes)}")
    for route in monitoring_routes:
        print(f"   {route}")
    
    if monitoring_routes:
        print("✅ 监控路由已正确注册")
    else:
        print("❌ 监控路由未注册")
        
        # 尝试手动注册监控路由
        print("\n尝试手动注册监控路由...")
        
        @app.app.route('/api/test-monitoring')
        def test_monitoring():
            return {"test": "monitoring"}
        
        print("手动注册测试路由完成")
        
        # 再次检查路由
        new_routes = []
        for rule in app.app.url_map.iter_rules():
            new_routes.append(f"{rule.rule} -> {rule.endpoint}")
        
        print(f"新路由数量: {len(new_routes)}")
        test_routes = [r for r in new_routes if 'test-monitoring' in r]
        if test_routes:
            print("✅ 手动路由注册成功")
        else:
            print("❌ 手动路由注册失败")

except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
