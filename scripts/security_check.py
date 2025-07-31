#!/usr/bin/env python3
"""
安全检查脚本
自动化安全扫描和漏洞检测
"""
import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))


class SecurityChecker:
    """安全检查器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.report_dir = self.project_root / "security_reports"
        self.report_dir.mkdir(exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.security_issues = []
    
    def run_full_security_scan(self) -> Dict[str, Any]:
        """
        运行完整的安全扫描
        
        Returns:
            Dict[str, Any]: 扫描结果报告
        """
        self.logger.info("开始安全扫描...")
        
        report = {
            "scan_time": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "checks": {}
        }
        
        # 1. Python依赖安全检查
        report["checks"]["python_dependencies"] = self._check_python_dependencies()
        
        # 2. Node.js依赖安全检查
        report["checks"]["nodejs_dependencies"] = self._check_nodejs_dependencies()
        
        # 3. 代码安全扫描
        report["checks"]["code_security"] = self._check_code_security()
        
        # 4. 配置安全检查
        report["checks"]["configuration"] = self._check_configuration_security()
        
        # 5. 文件权限检查
        report["checks"]["file_permissions"] = self._check_file_permissions()
        
        # 6. 密钥和敏感信息检查
        report["checks"]["secrets"] = self._check_secrets()
        
        # 7. 网络安全检查
        report["checks"]["network"] = self._check_network_security()
        
        # 生成总结
        report["summary"] = self._generate_summary(report["checks"])
        
        # 保存报告
        self._save_report(report)
        
        self.logger.info("安全扫描完成")
        return report
    
    def _check_python_dependencies(self) -> Dict[str, Any]:
        """检查Python依赖安全性"""
        self.logger.info("检查Python依赖安全性...")
        
        result = {
            "status": "success",
            "vulnerabilities": [],
            "recommendations": []
        }
        
        try:
            # 使用pip-audit检查漏洞
            cmd = ["pip-audit", "--format=json", "--desc"]
            process = subprocess.run(
                cmd,
                cwd=self.project_root / "backend-fastapi",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.returncode == 0:
                if process.stdout.strip():
                    audit_result = json.loads(process.stdout)
                    result["vulnerabilities"] = audit_result.get("vulnerabilities", [])
                    
                    if result["vulnerabilities"]:
                        result["status"] = "warning"
                        result["recommendations"].append("更新存在漏洞的依赖包")
            else:
                result["status"] = "error"
                result["error"] = process.stderr
                
        except subprocess.TimeoutExpired:
            result["status"] = "error"
            result["error"] = "pip-audit执行超时"
        except FileNotFoundError:
            result["status"] = "error"
            result["error"] = "pip-audit未安装，请运行: pip install pip-audit"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _check_nodejs_dependencies(self) -> Dict[str, Any]:
        """检查Node.js依赖安全性"""
        self.logger.info("检查Node.js依赖安全性...")
        
        result = {
            "status": "success",
            "vulnerabilities": [],
            "recommendations": []
        }
        
        # 检查前端项目
        for frontend_dir in ["frontend-vue3", "frontend-admin"]:
            frontend_path = self.project_root / frontend_dir
            if not frontend_path.exists():
                continue
                
            try:
                cmd = ["npm", "audit", "--json"]
                process = subprocess.run(
                    cmd,
                    cwd=frontend_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if process.stdout.strip():
                    audit_result = json.loads(process.stdout)
                    vulnerabilities = audit_result.get("vulnerabilities", {})
                    
                    if vulnerabilities:
                        result["vulnerabilities"].append({
                            "project": frontend_dir,
                            "vulnerabilities": vulnerabilities
                        })
                        result["status"] = "warning"
                        result["recommendations"].append(f"修复{frontend_dir}中的漏洞: npm audit fix")
                        
            except Exception as e:
                result["status"] = "error"
                result["error"] = f"{frontend_dir}: {str(e)}"
        
        return result
    
    def _check_code_security(self) -> Dict[str, Any]:
        """检查代码安全性"""
        self.logger.info("检查代码安全性...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 使用bandit检查Python代码
        try:
            cmd = ["bandit", "-r", "backend-fastapi/", "-f", "json"]
            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.stdout.strip():
                bandit_result = json.loads(process.stdout)
                issues = bandit_result.get("results", [])
                
                if issues:
                    result["issues"] = issues
                    result["status"] = "warning"
                    result["recommendations"].append("修复代码中的安全问题")
                    
        except FileNotFoundError:
            result["recommendations"].append("安装bandit进行代码安全检查: pip install bandit")
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _check_configuration_security(self) -> Dict[str, Any]:
        """检查配置安全性"""
        self.logger.info("检查配置安全性...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查环境变量文件
        env_files = [".env", ".env.local", ".env.production", ".env.security"]
        for env_file in env_files:
            env_path = self.project_root / "backend-fastapi" / env_file
            if env_path.exists():
                with open(env_path, 'r') as f:
                    content = f.read()
                    
                # 检查默认密钥
                if "dev-secret-key" in content or "change-this" in content:
                    result["issues"].append(f"{env_file}: 使用默认密钥")
                    result["status"] = "warning"
                
                # 检查弱密码
                if "password=123" in content or "password=admin" in content:
                    result["issues"].append(f"{env_file}: 使用弱密码")
                    result["status"] = "warning"
        
        # 检查数据库配置
        db_path = self.project_root / "backend-fastapi" / "data" / "admin.db"
        if db_path.exists():
            stat = db_path.stat()
            if oct(stat.st_mode)[-3:] != "600":
                result["issues"].append("数据库文件权限过于宽松")
                result["recommendations"].append("设置数据库文件权限为600")
                result["status"] = "warning"
        
        return result
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """检查文件权限"""
        self.logger.info("检查文件权限...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查敏感文件权限
        sensitive_files = [
            "backend-fastapi/.env",
            "backend-fastapi/.env.security",
            "backend-fastapi/data/admin.db",
            "scripts/security_backup.py"
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                permissions = oct(stat.st_mode)[-3:]
                
                # 敏感文件应该只有所有者可读写
                if permissions not in ["600", "700"]:
                    result["issues"].append(f"{file_path}: 权限{permissions}过于宽松")
                    result["recommendations"].append(f"设置{file_path}权限为600")
                    result["status"] = "warning"
        
        return result
    
    def _check_secrets(self) -> Dict[str, Any]:
        """检查密钥和敏感信息"""
        self.logger.info("检查密钥和敏感信息...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 敏感信息模式
        sensitive_patterns = [
            r"password\s*=\s*['\"].*['\"]",
            r"secret\s*=\s*['\"].*['\"]",
            r"api_key\s*=\s*['\"].*['\"]",
            r"token\s*=\s*['\"].*['\"]",
            r"-----BEGIN.*PRIVATE KEY-----"
        ]
        
        # 检查代码文件
        code_files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js")) + list(self.project_root.rglob("*.ts"))
        
        for file_path in code_files:
            if ".git" in str(file_path) or "node_modules" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in sensitive_patterns:
                    import re
                    if re.search(pattern, content, re.IGNORECASE):
                        result["issues"].append(f"{file_path}: 可能包含硬编码的敏感信息")
                        result["status"] = "warning"
                        break
                        
            except Exception:
                continue
        
        if result["issues"]:
            result["recommendations"].append("将敏感信息移至环境变量或配置文件")
        
        return result
    
    def _check_network_security(self) -> Dict[str, Any]:
        """检查网络安全配置"""
        self.logger.info("检查网络安全配置...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查本地服务是否运行
        try:
            # 检查API服务
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                # 检查安全头
                headers = response.headers
                
                security_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection",
                    "Strict-Transport-Security"
                ]
                
                missing_headers = [h for h in security_headers if h not in headers]
                if missing_headers:
                    result["issues"].append(f"缺少安全响应头: {', '.join(missing_headers)}")
                    result["recommendations"].append("添加缺少的安全响应头")
                    result["status"] = "warning"
                    
        except requests.RequestException:
            result["issues"].append("无法连接到API服务进行安全检查")
        
        return result
    
    def _generate_summary(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """生成扫描总结"""
        total_issues = 0
        critical_issues = 0
        warnings = 0
        
        for check_name, check_result in checks.items():
            if check_result["status"] == "error":
                critical_issues += 1
            elif check_result["status"] == "warning":
                warnings += 1
                
            # 统计具体问题数量
            if "issues" in check_result:
                total_issues += len(check_result["issues"])
            if "vulnerabilities" in check_result:
                total_issues += len(check_result["vulnerabilities"])
        
        # 确定总体安全等级
        if critical_issues > 0:
            security_level = "critical"
        elif warnings > 3:
            security_level = "high_risk"
        elif warnings > 0:
            security_level = "medium_risk"
        else:
            security_level = "low_risk"
        
        return {
            "security_level": security_level,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "checks_passed": len([c for c in checks.values() if c["status"] == "success"]),
            "checks_total": len(checks)
        }
    
    def _save_report(self, report: Dict[str, Any]):
        """保存扫描报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"security_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"安全报告已保存: {report_file}")
        
        # 同时保存最新报告
        latest_report = self.report_dir / "latest_security_report.json"
        with open(latest_report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    checker = SecurityChecker()
    report = checker.run_full_security_scan()
    
    # 打印总结
    summary = report["summary"]
    print(f"\n🔒 安全扫描完成")
    print(f"安全等级: {summary['security_level']}")
    print(f"总问题数: {summary['total_issues']}")
    print(f"严重问题: {summary['critical_issues']}")
    print(f"警告: {summary['warnings']}")
    print(f"通过检查: {summary['checks_passed']}/{summary['checks_total']}")
    
    # 如果有严重问题，返回非零退出码
    if summary['critical_issues'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
