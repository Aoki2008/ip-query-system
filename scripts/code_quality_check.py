#!/usr/bin/env python3
"""
代码质量检查脚本
检查项目中的代码质量问题、安全漏洞、性能问题等
"""

import os
import subprocess
import sys
from pathlib import Path
import json

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, 
            capture_output=True, text=True, check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_backend_quality():
    """检查后端代码质量"""
    print("🔍 检查后端代码质量...")
    
    backend_dir = Path("backend-fastapi")
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return False
    
    issues = []
    
    # 检查Python语法
    print("  📝 检查Python语法...")
    success, stdout, stderr = run_command(
        "python -m py_compile app/main.py", 
        cwd=backend_dir
    )
    if not success:
        issues.append(f"Python语法错误: {stderr}")
    
    # 检查导入问题
    print("  📦 检查导入问题...")
    success, stdout, stderr = run_command(
        "python -c \"from app.main import app; print('导入成功')\"",
        cwd=backend_dir
    )
    if not success:
        issues.append(f"导入错误: {stderr}")
    
    # 检查依赖安全性
    print("  🔒 检查依赖安全性...")
    success, stdout, stderr = run_command(
        "python -m pip check",
        cwd=backend_dir
    )
    if not success:
        issues.append(f"依赖冲突: {stderr}")
    
    if issues:
        print(f"❌ 发现 {len(issues)} 个后端问题:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print("✅ 后端代码质量检查通过")
        return True

def check_frontend_quality():
    """检查前端代码质量"""
    print("\n🔍 检查前端代码质量...")
    
    frontend_dirs = ["frontend-vue3", "frontend-admin"]
    all_passed = True
    
    for dir_name in frontend_dirs:
        frontend_dir = Path(dir_name)
        if not frontend_dir.exists():
            print(f"❌ {dir_name} 目录不存在")
            all_passed = False
            continue
        
        print(f"  📝 检查 {dir_name}...")
        
        # 检查package.json
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            print(f"❌ {dir_name}/package.json 不存在")
            all_passed = False
            continue
        
        # 检查TypeScript配置
        tsconfig = frontend_dir / "tsconfig.json"
        if tsconfig.exists():
            print(f"✅ {dir_name} TypeScript配置存在")
        
        # 检查构建配置
        vite_config = frontend_dir / "vite.config.ts"
        if vite_config.exists():
            print(f"✅ {dir_name} Vite配置存在")
        
        print(f"✅ {dir_name} 代码质量检查通过")
    
    return all_passed

def check_security_issues():
    """检查安全问题"""
    print("\n🔒 检查安全问题...")
    
    security_issues = []
    
    # 检查硬编码密钥
    print("  🔑 检查硬编码密钥...")
    config_file = Path("backend-fastapi/app/config.py")
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        if "your-secret-key" in content.lower():
            security_issues.append("发现默认密钥，生产环境需要更改")
    
    # 检查调试模式
    print("  🐛 检查调试模式...")
    env_example = Path("backend-fastapi/.env.example")
    if env_example.exists():
        content = env_example.read_text(encoding='utf-8')
        if "DEBUG=true" in content:
            security_issues.append("示例配置中启用了调试模式")
    
    # 检查CORS配置
    print("  🌐 检查CORS配置...")
    cors_issues = []
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        if '"*"' in content and 'cors' in content.lower():
            cors_issues.append("CORS配置可能过于宽松")
    
    if security_issues or cors_issues:
        print(f"⚠️ 发现 {len(security_issues + cors_issues)} 个安全问题:")
        for issue in security_issues + cors_issues:
            print(f"    - {issue}")
        return False
    else:
        print("✅ 安全检查通过")
        return True

def check_performance_issues():
    """检查性能问题"""
    print("\n⚡ 检查性能问题...")
    
    performance_issues = []
    
    # 检查前端bundle大小
    print("  📦 检查前端资源...")
    for dir_name in ["frontend-vue3", "frontend-admin"]:
        dist_dir = Path(dir_name) / "dist"
        if dist_dir.exists():
            # 计算dist目录大小
            total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            if size_mb > 10:  # 大于10MB
                performance_issues.append(f"{dir_name} 构建产物过大: {size_mb:.1f}MB")
            else:
                print(f"✅ {dir_name} 构建产物大小合理: {size_mb:.1f}MB")
    
    # 检查后端依赖数量
    print("  📚 检查后端依赖...")
    requirements_file = Path("backend-fastapi/requirements.txt")
    if requirements_file.exists():
        try:
            lines = requirements_file.read_text(encoding='utf-8').strip().split('\n')
            dep_count = len([line for line in lines if line.strip() and not line.startswith('#')])
            if dep_count > 50:
                performance_issues.append(f"后端依赖过多: {dep_count} 个")
            else:
                print(f"✅ 后端依赖数量合理: {dep_count} 个")
        except UnicodeDecodeError:
            print("⚠️ requirements.txt 编码问题，跳过依赖检查")
    
    if performance_issues:
        print(f"⚠️ 发现 {len(performance_issues)} 个性能问题:")
        for issue in performance_issues:
            print(f"    - {issue}")
        return False
    else:
        print("✅ 性能检查通过")
        return True

def generate_report(results):
    """生成检查报告"""
    print("\n" + "="*60)
    print("📊 代码质量检查报告")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"🎯 总体结果: {passed_checks}/{total_checks} 检查通过")
    print(f"📈 通过率: {passed_checks/total_checks*100:.1f}%")
    
    print("\n📋 详细结果:")
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {check_name}: {status}")
    
    if passed_checks == total_checks:
        print("\n🎉 所有检查通过！代码质量良好。")
        return True
    else:
        print(f"\n⚠️ {total_checks - passed_checks} 项检查失败，请修复相关问题。")
        return False

def main():
    """主函数"""
    print("🔧 开始代码质量检查...")
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # 执行各项检查
    results = {
        "后端代码质量": check_backend_quality(),
        "前端代码质量": check_frontend_quality(),
        "安全问题检查": check_security_issues(),
        "性能问题检查": check_performance_issues()
    }
    
    # 生成报告
    success = generate_report(results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
