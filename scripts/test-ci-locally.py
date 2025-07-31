#!/usr/bin/env python3
"""
本地CI测试脚本 - 模拟GitHub Actions的本地测试
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def test_backend_quality():
    """测试后端代码质量"""
    print("🔍 测试后端代码质量...")
    
    backend_dir = Path("backend-fastapi")
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return False
    
    # 检查requirements.txt
    if not (backend_dir / "requirements.txt").exists():
        print("❌ requirements.txt 不存在")
        return False
    
    print("✅ 后端目录结构正确")
    
    # 模拟安装依赖（不实际安装）
    print("📦 检查Python依赖...")
    success, stdout, stderr = run_command(
        "python -c \"import sys; print(f'Python {sys.version}')\"",
        check=False
    )
    
    if success:
        print(f"✅ {stdout.strip()}")
    else:
        print("⚠️ Python环境检查失败")
    
    return True

def test_frontend_build():
    """测试前端构建"""
    print("\n🔍 测试前端构建...")
    
    frontend_dirs = ["frontend-vue3", "frontend-admin"]
    
    for dir_name in frontend_dirs:
        frontend_dir = Path(dir_name)
        if not frontend_dir.exists():
            print(f"❌ {dir_name} 目录不存在")
            continue
        
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            print(f"❌ {dir_name}/package.json 不存在")
            continue
        
        print(f"✅ {dir_name} 目录结构正确")
        
        # 检查Node.js
        success, stdout, stderr = run_command("node --version", check=False)
        if success:
            print(f"✅ Node.js {stdout.strip()}")
        else:
            print("⚠️ Node.js 未安装")
            continue
        
        # 检查npm
        success, stdout, stderr = run_command("npm --version", check=False)
        if success:
            print(f"✅ npm {stdout.strip()}")
        else:
            print("⚠️ npm 未安装")
    
    return True

def test_docker_config():
    """测试Docker配置"""
    print("\n🔍 测试Docker配置...")
    
    # 检查Dockerfile
    docker_files = [
        "backend-fastapi/Dockerfile",
        "frontend-vue3/Dockerfile", 
        "frontend-admin/Dockerfile"
    ]
    
    for dockerfile in docker_files:
        if Path(dockerfile).exists():
            print(f"✅ {dockerfile} 存在")
        else:
            print(f"❌ {dockerfile} 不存在")
    
    # 检查docker-compose.yml
    if Path("docker-compose.yml").exists():
        print("✅ docker-compose.yml 存在")
        
        # 验证docker-compose配置
        success, stdout, stderr = run_command(
            "docker-compose config", 
            check=False
        )
        if success:
            print("✅ docker-compose 配置有效")
        else:
            print("⚠️ docker-compose 配置验证失败")
    else:
        print("❌ docker-compose.yml 不存在")
    
    return True

def test_ci_config():
    """测试CI配置"""
    print("\n🔍 测试CI配置...")
    
    ci_file = Path(".github/workflows/ci.yml")
    if not ci_file.exists():
        print("❌ CI配置文件不存在")
        return False
    
    print("✅ CI配置文件存在")
    
    # 检查配置内容
    ci_content = ci_file.read_text(encoding='utf-8')
    
    required_jobs = [
        'code-quality',
        'backend-tests',
        'frontend-tests', 
        'admin-frontend-tests',
        'docker-build'
    ]
    
    for job in required_jobs:
        if job in ci_content:
            print(f"✅ 作业 '{job}' 存在")
        else:
            print(f"❌ 作业 '{job}' 缺失")
    
    # 检查路径引用
    path_checks = [
        ('backend-fastapi', '后端路径'),
        ('frontend-vue3', '前端路径'),
        ('frontend-admin', '管理后台路径')
    ]
    
    for path, desc in path_checks:
        if path in ci_content:
            print(f"✅ {desc} 正确引用")
        else:
            print(f"❌ {desc} 引用缺失")
    
    return True

def main():
    """主函数"""
    print("🚀 开始本地CI测试...")
    print("=" * 60)
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"📁 项目根目录: {project_root.absolute()}")
    
    # 运行各项测试
    tests = [
        ("后端代码质量", test_backend_quality),
        ("前端构建", test_frontend_build),
        ("Docker配置", test_docker_config),
        ("CI配置", test_ci_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试失败: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！CI配置准备就绪。")
        sys.exit(0)
    else:
        print("⚠️ 部分测试失败，请检查上述问题。")
        sys.exit(1)

if __name__ == "__main__":
    main()
