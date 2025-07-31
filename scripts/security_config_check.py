#!/usr/bin/env python3
"""
安全配置检查脚本
验证系统安全配置是否正确
"""
import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from backend_fastapi.app.config import settings


class SecurityConfigChecker:
    """安全配置检查器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.recommendations = []
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def run_full_check(self) -> Dict[str, Any]:
        """运行完整的安全配置检查"""
        self.logger.info("🔍 开始安全配置检查...")
        
        results = {
            "timestamp": self._get_timestamp(),
            "checks": {
                "environment": self._check_environment_config(),
                "ssl_tls": self._check_ssl_tls_config(),
                "headers": self._check_security_headers(),
                "authentication": self._check_authentication_config(),
                "error_handling": self._check_error_handling(),
                "file_permissions": self._check_file_permissions(),
                "dependencies": self._check_dependency_config()
            },
            "summary": {}
        }
        
        # 生成总结
        results["summary"] = self._generate_summary(results["checks"])
        
        self.logger.info("✅ 安全配置检查完成")
        return results
    
    def _check_environment_config(self) -> Dict[str, Any]:
        """检查环境配置"""
        self.logger.info("🌍 检查环境配置...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查调试模式
        if settings.debug:
            result["issues"].append("调试模式在生产环境中启用")
            result["recommendations"].append("在生产环境中禁用调试模式")
            result["status"] = "warning"
        
        # 检查密钥配置
        if hasattr(settings, 'admin_secret_key'):
            if len(settings.admin_secret_key) < 32:
                result["issues"].append("JWT密钥长度不足")
                result["recommendations"].append("使用至少32字符的强随机密钥")
                result["status"] = "warning"
        
        # 检查数据库配置
        if hasattr(settings, 'database_url'):
            if "sqlite" in settings.database_url.lower():
                result["recommendations"].append("生产环境建议使用PostgreSQL或MySQL")
        
        # 检查Redis配置
        if not settings.redis_enabled:
            result["recommendations"].append("启用Redis缓存以提升性能")
        
        return result
    
    def _check_ssl_tls_config(self) -> Dict[str, Any]:
        """检查SSL/TLS配置"""
        self.logger.info("🔒 检查SSL/TLS配置...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查SSL证书文件
        ssl_dir = self.project_root / "docker" / "nginx" / "ssl"
        ssl_files = ["cert.pem", "key.pem", "dhparam.pem"]
        
        missing_files = []
        for file_name in ssl_files:
            if not (ssl_dir / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            result["issues"].append(f"缺少SSL文件: {', '.join(missing_files)}")
            result["recommendations"].append("运行 scripts/generate_ssl_cert.sh 生成SSL证书")
            result["status"] = "warning"
        
        # 检查SSL配置文件
        ssl_conf = self.project_root / "docker" / "nginx" / "ssl.conf"
        if not ssl_conf.exists():
            result["issues"].append("缺少SSL配置文件")
            result["recommendations"].append("确保ssl.conf文件存在并正确配置")
            result["status"] = "warning"
        
        return result
    
    def _check_security_headers(self) -> Dict[str, Any]:
        """检查安全响应头"""
        self.logger.info("🛡️ 检查安全响应头...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": [],
            "headers_found": []
        }
        
        try:
            # 尝试访问本地API
            response = requests.get("http://localhost:8000/health", timeout=5)
            headers = response.headers
            
            # 检查必需的安全头
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Content-Security-Policy"
            ]
            
            missing_headers = []
            for header in required_headers:
                if header in headers:
                    result["headers_found"].append(header)
                else:
                    missing_headers.append(header)
            
            if missing_headers:
                result["issues"].append(f"缺少安全响应头: {', '.join(missing_headers)}")
                result["recommendations"].append("确保安全中间件正确配置")
                result["status"] = "warning"
            
        except requests.RequestException:
            result["issues"].append("无法连接到API服务检查响应头")
            result["recommendations"].append("确保API服务正在运行")
            result["status"] = "error"
        
        return result
    
    def _check_authentication_config(self) -> Dict[str, Any]:
        """检查认证配置"""
        self.logger.info("🔐 检查认证配置...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查密码策略配置
        password_config = {
            "min_length": getattr(settings, 'password_min_length', 8),
            "require_uppercase": getattr(settings, 'password_require_uppercase', False),
            "require_lowercase": getattr(settings, 'password_require_lowercase', False),
            "require_numbers": getattr(settings, 'password_require_numbers', False),
            "require_symbols": getattr(settings, 'password_require_symbols', False)
        }
        
        if password_config["min_length"] < 12:
            result["issues"].append("密码最小长度不足12位")
            result["recommendations"].append("设置密码最小长度为12位或更多")
            result["status"] = "warning"
        
        if not all([
            password_config["require_uppercase"],
            password_config["require_lowercase"], 
            password_config["require_numbers"],
            password_config["require_symbols"]
        ]):
            result["issues"].append("密码复杂度要求不足")
            result["recommendations"].append("启用所有密码复杂度要求")
            result["status"] = "warning"
        
        # 检查JWT配置
        jwt_expire = getattr(settings, 'admin_access_token_expire_minutes', 30)
        if jwt_expire > 60:
            result["issues"].append("JWT令牌有效期过长")
            result["recommendations"].append("设置JWT令牌有效期不超过60分钟")
            result["status"] = "warning"
        
        return result
    
    def _check_error_handling(self) -> Dict[str, Any]:
        """检查错误处理配置"""
        self.logger.info("⚠️ 检查错误处理配置...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查错误处理中间件文件
        error_handler_file = self.project_root / "backend-fastapi" / "app" / "core" / "error_handler.py"
        if not error_handler_file.exists():
            result["issues"].append("缺少错误处理中间件")
            result["recommendations"].append("确保error_handler.py文件存在")
            result["status"] = "error"
        
        # 检查调试模式
        if settings.debug:
            result["issues"].append("调试模式可能暴露敏感错误信息")
            result["recommendations"].append("生产环境禁用调试模式")
            result["status"] = "warning"
        
        return result
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """检查文件权限"""
        self.logger.info("📁 检查文件权限...")
        
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
            "docker/nginx/ssl/key.pem"
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    stat = full_path.stat()
                    permissions = oct(stat.st_mode)[-3:]
                    
                    if permissions not in ["600", "700"]:
                        result["issues"].append(f"{file_path}: 权限{permissions}过于宽松")
                        result["recommendations"].append(f"设置{file_path}权限为600")
                        result["status"] = "warning"
                except Exception as e:
                    result["issues"].append(f"无法检查{file_path}权限: {e}")
        
        return result
    
    def _check_dependency_config(self) -> Dict[str, Any]:
        """检查依赖配置"""
        self.logger.info("📦 检查依赖配置...")
        
        result = {
            "status": "success",
            "issues": [],
            "recommendations": []
        }
        
        # 检查是否有依赖扫描报告
        scan_report = self.project_root / "security_reports" / "dependencies" / "latest_dependency_scan.json"
        if scan_report.exists():
            try:
                with open(scan_report, 'r') as f:
                    scan_data = json.load(f)
                    
                total_vulns = scan_data.get("summary", {}).get("total_vulnerabilities", 0)
                if total_vulns > 0:
                    result["issues"].append(f"发现{total_vulns}个依赖漏洞")
                    result["recommendations"].append("运行依赖更新脚本修复漏洞")
                    result["status"] = "warning"
            except Exception as e:
                result["issues"].append(f"无法读取依赖扫描报告: {e}")
        else:
            result["recommendations"].append("运行依赖安全扫描检查漏洞")
        
        return result
    
    def _generate_summary(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """生成检查总结"""
        total_issues = 0
        warnings = 0
        errors = 0
        
        for check_name, check_result in checks.items():
            status = check_result.get("status", "success")
            issues_count = len(check_result.get("issues", []))
            
            total_issues += issues_count
            
            if status == "error":
                errors += 1
            elif status == "warning":
                warnings += 1
        
        # 确定总体安全状态
        if errors > 0:
            overall_status = "critical"
        elif warnings > 3:
            overall_status = "high_risk"
        elif warnings > 0:
            overall_status = "medium_risk"
        else:
            overall_status = "secure"
        
        return {
            "overall_status": overall_status,
            "total_issues": total_issues,
            "errors": errors,
            "warnings": warnings,
            "checks_passed": len([c for c in checks.values() if c["status"] == "success"]),
            "checks_total": len(checks)
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """主函数"""
    checker = SecurityConfigChecker()
    results = checker.run_full_check()
    
    # 保存检查报告
    report_dir = Path("security_reports/config")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = results["timestamp"].replace(":", "-").split(".")[0]
    report_file = report_dir / f"config_check_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 打印总结
    summary = results["summary"]
    print(f"\n🔍 安全配置检查完成")
    print(f"总体状态: {summary['overall_status']}")
    print(f"总问题数: {summary['total_issues']}")
    print(f"错误: {summary['errors']}")
    print(f"警告: {summary['warnings']}")
    print(f"通过检查: {summary['checks_passed']}/{summary['checks_total']}")
    print(f"报告已保存: {report_file}")
    
    # 如果有严重问题，返回非零退出码
    if summary['errors'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
