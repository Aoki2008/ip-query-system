#!/usr/bin/env python3
"""
验证导入导出功能的完整性
"""

import requests
import json
import os

def verify_frontend_files():
    """验证前端文件是否正确更新"""
    print("🔍 验证前端文件...")
    
    # 检查HTML文件是否包含新的UI元素
    html_file = "IP查询工具/index.html"
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('导入按钮', 'import-btn'),
            ('文件拖拽区域', 'file-drop-zone'),
            ('导出按钮', 'export-csv'),
            ('结果头部', 'results-header'),
        ]
        
        for name, element_id in checks:
            if element_id in content:
                print(f"✅ {name}: 已添加")
            else:
                print(f"❌ {name}: 未找到")
    else:
        print(f"❌ HTML文件不存在: {html_file}")

def verify_css_styles():
    """验证CSS样式是否正确添加"""
    print("\n🎨 验证CSS样式...")
    
    css_file = "IP查询工具/css/style.css"
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('导入控件样式', '.import-controls'),
            ('拖拽区域样式', '.file-drop-zone'),
            ('导出按钮样式', '.export-btn'),
            ('结果头部样式', '.results-header'),
            ('响应式设计', '@media (max-width: 768px)'),
        ]
        
        for name, selector in checks:
            if selector in content:
                print(f"✅ {name}: 已添加")
            else:
                print(f"❌ {name}: 未找到")
    else:
        print(f"❌ CSS文件不存在: {css_file}")

def verify_javascript_functions():
    """验证JavaScript功能是否正确添加"""
    print("\n⚙️ 验证JavaScript功能...")
    
    js_file = "IP查询工具/js/script.js"
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('导入功能初始化', 'initImportFeature'),
            ('导出功能初始化', 'initExportFeature'),
            ('文件处理函数', 'processImportFile'),
            ('CSV导出函数', 'exportToCSV'),
            ('JSON导出函数', 'exportToJSON'),
            ('Excel导出函数', 'exportToExcel'),
            ('文件下载函数', 'downloadFile'),
            ('结果数据存储', 'batchQueryResults'),
        ]
        
        for name, function_name in checks:
            if function_name in content:
                print(f"✅ {name}: 已添加")
            else:
                print(f"❌ {name}: 未找到")
    else:
        print(f"❌ JavaScript文件不存在: {js_file}")

def verify_test_files():
    """验证测试文件是否存在"""
    print("\n📁 验证测试文件...")
    
    test_files = [
        ('CSV测试文件', 'test_ips.csv'),
        ('TXT测试文件', 'test_ips.txt'),
        ('功能说明文档', '导入导出功能说明.md'),
    ]
    
    for name, filename in test_files:
        if os.path.exists(filename):
            print(f"✅ {name}: 存在")
        else:
            print(f"❌ {name}: 不存在")

def verify_api_functionality():
    """验证API功能"""
    print("\n🔌 验证API功能...")
    
    try:
        # 测试健康检查
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API健康检查: 正常")
        else:
            print(f"❌ API健康检查: 失败 ({response.status_code})")
            return False
            
        # 测试批量查询
        test_data = {"ips": ["8.8.8.8", "1.1.1.1"]}
        response = requests.post(
            "http://localhost:5000/api/query-batch",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('total') == 2:
                print("✅ 批量查询API: 正常")
                return True
            else:
                print(f"❌ 批量查询API: 结果数量不正确")
                return False
        else:
            print(f"❌ 批量查询API: 失败 ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 开始验证导入导出功能...")
    print("=" * 60)
    
    # 验证前端文件
    verify_frontend_files()
    
    # 验证CSS样式
    verify_css_styles()
    
    # 验证JavaScript功能
    verify_javascript_functions()
    
    # 验证测试文件
    verify_test_files()
    
    # 验证API功能
    api_ok = verify_api_functionality()
    
    print("\n" + "=" * 60)
    print("📋 验证总结:")
    
    if api_ok:
        print("✅ 所有功能验证完成")
        print("\n🎯 下一步操作:")
        print("1. 打开浏览器访问: http://localhost:3000")
        print("2. 切换到'批量查询'标签页")
        print("3. 测试导入功能 (使用 test_ips.csv 或 test_ips.txt)")
        print("4. 执行批量查询")
        print("5. 测试导出功能 (CSV、JSON、Excel)")
        print("\n📖 详细说明请查看: 导入导出功能说明.md")
    else:
        print("❌ 部分功能验证失败，请检查服务状态")
    
    print("\n🎉 验证完成!")

if __name__ == "__main__":
    main()
