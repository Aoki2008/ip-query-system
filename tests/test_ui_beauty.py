#!/usr/bin/env python3
"""
测试UI美化效果的脚本
"""

import requests
import time

def test_services():
    """测试服务状态"""
    print("🔍 检查服务状态...")
    
    try:
        # 测试API服务
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
        else:
            print(f"❌ API服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API服务连接失败: {e}")
        return False
    
    try:
        # 测试前端服务
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常运行")
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端服务连接失败: {e}")
        return False
    
    return True

def check_css_updates():
    """检查CSS文件是否包含美化样式"""
    print("\n🎨 检查CSS美化样式...")
    
    try:
        response = requests.get("http://localhost:3000/css/style.css", timeout=5)
        if response.status_code == 200:
            css_content = response.text
            
            # 检查关键美化样式
            checks = [
                ("导入区域渐变背景", "linear-gradient(135deg, rgba(99, 102, 241, 0.05)"),
                ("导入按钮3D效果", "box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3)"),
                ("拖拽区域美化", "background: radial-gradient(circle at center"),
                ("导出按钮颜色主题", "#export-csv"),
                ("加载动画", "@keyframes spin"),
                ("成功反馈动画", "@keyframes successPulse"),
                ("错误反馈动画", "@keyframes errorShake"),
                ("闪烁效果", "@keyframes shimmer"),
                ("响应式设计", "@media (max-width: 768px)"),
            ]
            
            for name, pattern in checks:
                if pattern in css_content:
                    print(f"✅ {name}: 已应用")
                else:
                    print(f"❌ {name}: 未找到")
                    
        else:
            print(f"❌ CSS文件加载失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CSS文件检查失败: {e}")

def check_js_updates():
    """检查JavaScript文件是否包含状态管理"""
    print("\n⚙️ 检查JavaScript状态管理...")
    
    try:
        response = requests.get("http://localhost:3000/js/script.js", timeout=5)
        if response.status_code == 200:
            js_content = response.text
            
            # 检查关键功能
            checks = [
                ("导入按钮状态管理", "resetImportButton"),
                ("导出按钮状态管理", "resetExportButton"),
                ("加载状态类", "classList.add('loading')"),
                ("成功状态类", "classList.add('success')"),
                ("错误状态类", "classList.add('error')"),
                ("导出状态类", "classList.add('exporting')"),
            ]
            
            for name, pattern in checks:
                if pattern in js_content:
                    print(f"✅ {name}: 已实现")
                else:
                    print(f"❌ {name}: 未找到")
                    
        else:
            print(f"❌ JavaScript文件加载失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ JavaScript文件检查失败: {e}")

def test_batch_query():
    """测试批量查询功能"""
    print("\n🧪 测试批量查询功能...")
    
    try:
        test_data = {"ips": ["8.8.8.8", "1.1.1.1"]}
        response = requests.post(
            "http://localhost:5000/api/query-batch",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 批量查询成功: {data.get('total', 0)}个IP")
            return True
        else:
            print(f"❌ 批量查询失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 批量查询异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始UI美化效果验证...")
    print("=" * 60)
    
    # 检查服务状态
    if not test_services():
        print("\n❌ 服务检查失败")
        return
    
    # 检查CSS美化
    check_css_updates()
    
    # 检查JavaScript增强
    check_js_updates()
    
    # 测试功能
    test_batch_query()
    
    print("\n" + "=" * 60)
    print("🎨 UI美化验证完成!")
    
    print("\n📋 手动测试建议:")
    print("1. 打开浏览器访问: http://localhost:3000")
    print("2. 切换到'批量查询'标签页")
    print("3. 观察导入区域的视觉效果:")
    print("   - 渐变背景容器")
    print("   - 3D导入按钮效果")
    print("   - 拖拽区域悬停变化")
    print("4. 测试导入功能并观察加载动画")
    print("5. 执行批量查询")
    print("6. 观察导出区域的美化效果:")
    print("   - 结果统计徽章")
    print("   - 分色主题按钮")
    print("   - 悬停和点击效果")
    print("7. 测试导出功能并观察状态反馈")
    print("8. 调整浏览器窗口大小测试响应式效果")
    
    print("\n📖 详细说明请查看: UI美化验证.md")
    print("\n🎉 美化验证完成!")

if __name__ == "__main__":
    main()
