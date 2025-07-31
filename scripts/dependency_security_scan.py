#!/usr/bin/env python3
"""
依赖安全扫描脚本
自动化检测Python和Node.js依赖的安全漏洞
"""
import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DependencySecurityScanner:
    """依赖安全扫描器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.report_dir = self.project_root / "security_reports" / "dependencies"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.vulnerabilities = []
        self.scan_results = {
            "scan_time": datetime.now().isoformat(),
            "python_scan": {},
            "nodejs_scan": {},
            "summary": {}
        }
    
    def run_full_dependency_scan(self) -> Dict[str, Any]:
        """运行完整的依赖安全扫描"""
        logger.info("🔍 开始依赖安全扫描...")
        
        # 1. Python依赖扫描
        self.scan_results["python_scan"] = self._scan_python_dependencies()
        
        # 2. Node.js依赖扫描
        self.scan_results["nodejs_scan"] = self._scan_nodejs_dependencies()
        
        # 3. 生成总结报告
        self.scan_results["summary"] = self._generate_summary()
        
        # 4. 保存扫描报告
        self._save_scan_report()
        
        logger.info("✅ 依赖安全扫描完成")
        return self.scan_results
    
    def _scan_python_dependencies(self) -> Dict[str, Any]:
        """扫描Python依赖安全漏洞"""
        logger.info("🐍 扫描Python依赖...")
        
        result = {
            "status": "success",
            "vulnerabilities": [],
            "tools_used": [],
            "recommendations": []
        }
        
        # 检查后端项目
        backend_dir = self.project_root / "backend-fastapi"
        if not backend_dir.exists():
            result["status"] = "skipped"
            result["error"] = "后端目录不存在"
            return result
        
        # 1. 使用pip-audit扫描
        pip_audit_result = self._run_pip_audit(backend_dir)
        if pip_audit_result:
            result["tools_used"].append("pip-audit")
            result["vulnerabilities"].extend(pip_audit_result.get("vulnerabilities", []))
        
        # 2. 使用safety扫描
        safety_result = self._run_safety_scan(backend_dir)
        if safety_result:
            result["tools_used"].append("safety")
            result["vulnerabilities"].extend(safety_result.get("vulnerabilities", []))
        
        # 3. 使用bandit扫描代码安全问题
        bandit_result = self._run_bandit_scan(backend_dir)
        if bandit_result:
            result["tools_used"].append("bandit")
            result["vulnerabilities"].extend(bandit_result.get("issues", []))
        
        # 生成修复建议
        if result["vulnerabilities"]:
            result["recommendations"] = self._generate_python_recommendations(result["vulnerabilities"])
        
        return result
    
    def _run_pip_audit(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """运行pip-audit扫描"""
        try:
            cmd = ["pip-audit", "--format=json", "--desc"]
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.returncode == 0 and process.stdout.strip():
                return json.loads(process.stdout)
            elif process.stderr:
                logger.warning(f"pip-audit警告: {process.stderr}")
            
        except subprocess.TimeoutExpired:
            logger.error("pip-audit执行超时")
        except FileNotFoundError:
            logger.warning("pip-audit未安装，跳过扫描")
        except Exception as e:
            logger.error(f"pip-audit执行失败: {e}")
        
        return None
    
    def _run_safety_scan(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """运行safety扫描"""
        try:
            cmd = ["safety", "check", "--json"]
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.stdout.strip():
                safety_data = json.loads(process.stdout)
                return {
                    "vulnerabilities": [
                        {
                            "package": vuln.get("package"),
                            "version": vuln.get("installed_version"),
                            "vulnerability": vuln.get("vulnerability"),
                            "severity": "high",
                            "source": "safety"
                        }
                        for vuln in safety_data
                    ]
                }
                
        except subprocess.TimeoutExpired:
            logger.error("safety执行超时")
        except FileNotFoundError:
            logger.warning("safety未安装，跳过扫描")
        except Exception as e:
            logger.error(f"safety执行失败: {e}")
        
        return None
    
    def _run_bandit_scan(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """运行bandit代码安全扫描"""
        try:
            cmd = ["bandit", "-r", ".", "-f", "json"]
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.stdout.strip():
                bandit_data = json.loads(process.stdout)
                return {
                    "issues": [
                        {
                            "file": issue.get("filename"),
                            "line": issue.get("line_number"),
                            "issue": issue.get("issue_text"),
                            "severity": issue.get("issue_severity"),
                            "confidence": issue.get("issue_confidence"),
                            "source": "bandit"
                        }
                        for issue in bandit_data.get("results", [])
                    ]
                }
                
        except subprocess.TimeoutExpired:
            logger.error("bandit执行超时")
        except FileNotFoundError:
            logger.warning("bandit未安装，跳过扫描")
        except Exception as e:
            logger.error(f"bandit执行失败: {e}")
        
        return None
    
    def _scan_nodejs_dependencies(self) -> Dict[str, Any]:
        """扫描Node.js依赖安全漏洞"""
        logger.info("📦 扫描Node.js依赖...")
        
        result = {
            "status": "success",
            "projects": {},
            "total_vulnerabilities": 0,
            "recommendations": []
        }
        
        # 扫描前端项目
        frontend_projects = ["frontend-vue3", "frontend-admin"]
        
        for project in frontend_projects:
            project_dir = self.project_root / project
            if project_dir.exists() and (project_dir / "package.json").exists():
                project_result = self._scan_nodejs_project(project_dir)
                result["projects"][project] = project_result
                result["total_vulnerabilities"] += len(project_result.get("vulnerabilities", []))
        
        # 生成修复建议
        if result["total_vulnerabilities"] > 0:
            result["recommendations"] = self._generate_nodejs_recommendations(result["projects"])
        
        return result
    
    def _scan_nodejs_project(self, project_dir: Path) -> Dict[str, Any]:
        """扫描单个Node.js项目"""
        result = {
            "vulnerabilities": [],
            "tools_used": [],
            "package_count": 0
        }
        
        try:
            # 1. npm audit扫描
            cmd = ["npm", "audit", "--json"]
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.stdout.strip():
                audit_data = json.loads(process.stdout)
                result["tools_used"].append("npm audit")
                
                # 解析漏洞信息
                vulnerabilities = audit_data.get("vulnerabilities", {})
                for pkg_name, vuln_info in vulnerabilities.items():
                    result["vulnerabilities"].append({
                        "package": pkg_name,
                        "severity": vuln_info.get("severity"),
                        "title": vuln_info.get("via", [{}])[0].get("title", ""),
                        "range": vuln_info.get("range"),
                        "source": "npm audit"
                    })
            
            # 2. 检查package.json中的包数量
            package_json = project_dir / "package.json"
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    pkg_data = json.load(f)
                    deps = pkg_data.get("dependencies", {})
                    dev_deps = pkg_data.get("devDependencies", {})
                    result["package_count"] = len(deps) + len(dev_deps)
                    
        except subprocess.TimeoutExpired:
            logger.error(f"npm audit超时: {project_dir}")
        except Exception as e:
            logger.error(f"Node.js扫描失败 {project_dir}: {e}")
        
        return result
    
    def _generate_python_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """生成Python依赖修复建议"""
        recommendations = []
        
        if vulnerabilities:
            recommendations.append("运行 'pip-audit --fix' 自动修复已知漏洞")
            recommendations.append("更新requirements.txt中的包版本")
            recommendations.append("定期运行安全扫描检查新漏洞")
            
            # 按包名分组建议
            packages = set(v.get("package") for v in vulnerabilities if v.get("package"))
            if packages:
                recommendations.append(f"重点关注以下包的安全更新: {', '.join(packages)}")
        
        return recommendations
    
    def _generate_nodejs_recommendations(self, projects: Dict) -> List[str]:
        """生成Node.js依赖修复建议"""
        recommendations = []
        
        for project_name, project_data in projects.items():
            if project_data.get("vulnerabilities"):
                recommendations.append(f"在{project_name}目录运行 'npm audit fix' 修复漏洞")
                recommendations.append(f"考虑更新{project_name}的package.json依赖版本")
        
        recommendations.append("定期运行 'npm audit' 检查新漏洞")
        recommendations.append("使用 'npm update' 更新到最新的安全版本")
        
        return recommendations
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成扫描总结"""
        python_vulns = len(self.scan_results["python_scan"].get("vulnerabilities", []))
        nodejs_vulns = self.scan_results["nodejs_scan"].get("total_vulnerabilities", 0)
        
        total_vulns = python_vulns + nodejs_vulns
        
        # 确定风险等级
        if total_vulns == 0:
            risk_level = "low"
        elif total_vulns <= 5:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "total_vulnerabilities": total_vulns,
            "python_vulnerabilities": python_vulns,
            "nodejs_vulnerabilities": nodejs_vulns,
            "risk_level": risk_level,
            "scan_tools": list(set(
                self.scan_results["python_scan"].get("tools_used", []) +
                [tool for project in self.scan_results["nodejs_scan"].get("projects", {}).values()
                 for tool in project.get("tools_used", [])]
            )),
            "next_scan_recommended": (datetime.now().replace(day=datetime.now().day + 7)).isoformat()
        }
    
    def _save_scan_report(self):
        """保存扫描报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"dependency_scan_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
        
        # 保存最新报告
        latest_report = self.report_dir / "latest_dependency_scan.json"
        with open(latest_report, 'w', encoding='utf-8') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 扫描报告已保存: {report_file}")


def install_scan_tools():
    """安装扫描工具"""
    logger.info("🔧 安装依赖扫描工具...")
    
    tools = [
        ("pip-audit", "pip install pip-audit"),
        ("safety", "pip install safety"),
        ("bandit", "pip install bandit")
    ]
    
    for tool_name, install_cmd in tools:
        try:
            subprocess.run([tool_name, "--version"], capture_output=True, check=True)
            logger.info(f"✅ {tool_name} 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info(f"📦 安装 {tool_name}...")
            subprocess.run(install_cmd.split(), check=True)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='依赖安全扫描工具')
    parser.add_argument('--install-tools', action='store_true', help='安装扫描工具')
    parser.add_argument('--python-only', action='store_true', help='仅扫描Python依赖')
    parser.add_argument('--nodejs-only', action='store_true', help='仅扫描Node.js依赖')
    
    args = parser.parse_args()
    
    if args.install_tools:
        install_scan_tools()
        return
    
    scanner = DependencySecurityScanner()
    
    if args.python_only:
        result = {"python_scan": scanner._scan_python_dependencies()}
    elif args.nodejs_only:
        result = {"nodejs_scan": scanner._scan_nodejs_dependencies()}
    else:
        result = scanner.run_full_dependency_scan()
    
    # 打印总结
    summary = result.get("summary", {})
    total_vulns = summary.get("total_vulnerabilities", 0)
    risk_level = summary.get("risk_level", "unknown")
    
    print(f"\n🔍 依赖安全扫描完成")
    print(f"发现漏洞: {total_vulns}")
    print(f"风险等级: {risk_level}")
    
    if total_vulns > 0:
        print("\n⚠️  建议立即修复发现的安全漏洞")
        sys.exit(1)
    else:
        print("\n✅ 未发现安全漏洞")


if __name__ == '__main__':
    main()
