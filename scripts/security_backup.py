#!/usr/bin/env python3
"""
安全备份脚本
自动化数据库备份、加密和异地存储
"""
import os
import sys
import gzip
import shutil
import sqlite3
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from backend_fastapi.app.config import settings
from backend_fastapi.app.core.encryption import get_encryption


class SecurityBackup:
    """安全备份管理器"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.db_path = Path("backend-fastapi/data/admin.db")
        self.encryption = get_encryption()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backups/backup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self) -> Optional[str]:
        """
        创建数据库备份
        
        Returns:
            Optional[str]: 备份文件路径，失败返回None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"admin_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            self.logger.info(f"开始创建数据库备份: {backup_filename}")
            
            # 检查数据库文件是否存在
            if not self.db_path.exists():
                self.logger.error(f"数据库文件不存在: {self.db_path}")
                return None
            
            # 使用SQLite的备份API创建一致性备份
            with sqlite3.connect(str(self.db_path)) as source_conn:
                with sqlite3.connect(str(backup_path)) as backup_conn:
                    source_conn.backup(backup_conn)
            
            self.logger.info(f"数据库备份创建成功: {backup_path}")
            
            # 压缩备份文件
            compressed_path = self._compress_backup(backup_path)
            if compressed_path:
                backup_path.unlink()  # 删除未压缩的文件
                backup_path = compressed_path
            
            # 加密备份文件
            encrypted_path = self._encrypt_backup(backup_path)
            if encrypted_path:
                backup_path.unlink()  # 删除未加密的文件
                backup_path = encrypted_path
            
            # 生成校验和
            checksum = self._generate_checksum(backup_path)
            checksum_file = backup_path.with_suffix(backup_path.suffix + '.sha256')
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {backup_path.name}\n")
            
            self.logger.info(f"备份完成: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"备份创建失败: {e}")
            return None
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """压缩备份文件"""
        try:
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            self.logger.info(f"备份文件压缩完成: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"备份文件压缩失败: {e}")
            return None
    
    def _encrypt_backup(self, backup_path: Path) -> Optional[Path]:
        """加密备份文件"""
        try:
            encrypted_path = backup_path.with_suffix(backup_path.suffix + '.enc')
            
            with open(backup_path, 'rb') as f_in:
                data = f_in.read()
                encrypted_data = self.encryption.encrypt(data)
            
            with open(encrypted_path, 'w') as f_out:
                f_out.write(encrypted_data)
            
            self.logger.info(f"备份文件加密完成: {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            self.logger.error(f"备份文件加密失败: {e}")
            return None
    
    def _generate_checksum(self, file_path: Path) -> str:
        """生成文件校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def verify_backup(self, backup_path: str) -> bool:
        """
        验证备份文件完整性
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 验证是否成功
        """
        try:
            backup_file = Path(backup_path)
            checksum_file = backup_file.with_suffix(backup_file.suffix + '.sha256')
            
            if not checksum_file.exists():
                self.logger.error(f"校验和文件不存在: {checksum_file}")
                return False
            
            # 读取存储的校验和
            with open(checksum_file, 'r') as f:
                stored_checksum = f.read().split()[0]
            
            # 计算当前文件的校验和
            current_checksum = self._generate_checksum(backup_file)
            
            if stored_checksum == current_checksum:
                self.logger.info(f"备份文件验证成功: {backup_path}")
                return True
            else:
                self.logger.error(f"备份文件验证失败: 校验和不匹配")
                return False
                
        except Exception as e:
            self.logger.error(f"备份文件验证失败: {e}")
            return False
    
    def restore_backup(self, backup_path: str, target_path: Optional[str] = None) -> bool:
        """
        恢复备份
        
        Args:
            backup_path: 备份文件路径
            target_path: 目标路径，默认为原数据库路径
            
        Returns:
            bool: 恢复是否成功
        """
        try:
            if not self.verify_backup(backup_path):
                self.logger.error("备份文件验证失败，无法恢复")
                return False
            
            backup_file = Path(backup_path)
            target = Path(target_path) if target_path else self.db_path
            
            self.logger.info(f"开始恢复备份: {backup_path} -> {target}")
            
            # 解密备份文件
            if backup_file.suffix == '.enc':
                decrypted_path = self._decrypt_backup(backup_file)
                if not decrypted_path:
                    return False
                backup_file = decrypted_path
            
            # 解压备份文件
            if backup_file.suffix == '.gz':
                decompressed_path = self._decompress_backup(backup_file)
                if not decompressed_path:
                    return False
                backup_file = decompressed_path
            
            # 备份当前数据库
            if target.exists():
                backup_current = target.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(target, backup_current)
                self.logger.info(f"当前数据库已备份到: {backup_current}")
            
            # 恢复数据库
            shutil.copy2(backup_file, target)
            
            self.logger.info(f"数据库恢复完成: {target}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库恢复失败: {e}")
            return False
    
    def _decrypt_backup(self, encrypted_path: Path) -> Optional[Path]:
        """解密备份文件"""
        try:
            decrypted_path = encrypted_path.with_suffix('')
            
            with open(encrypted_path, 'r') as f_in:
                encrypted_data = f_in.read()
                decrypted_data = self.encryption.decrypt(encrypted_data)
            
            with open(decrypted_path, 'wb') as f_out:
                f_out.write(decrypted_data)
            
            return decrypted_path
            
        except Exception as e:
            self.logger.error(f"备份文件解密失败: {e}")
            return None
    
    def _decompress_backup(self, compressed_path: Path) -> Optional[Path]:
        """解压备份文件"""
        try:
            decompressed_path = compressed_path.with_suffix('')
            
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return decompressed_path
            
        except Exception as e:
            self.logger.error(f"备份文件解压失败: {e}")
            return None
    
    def cleanup_old_backups(self, retention_days: int = 30):
        """
        清理旧备份文件
        
        Args:
            retention_days: 保留天数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("admin_backup_*.db.*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    # 同时删除校验和文件
                    checksum_file = backup_file.with_suffix(backup_file.suffix + '.sha256')
                    if checksum_file.exists():
                        checksum_file.unlink()
                    deleted_count += 1
                    self.logger.info(f"删除旧备份文件: {backup_file}")
            
            self.logger.info(f"清理完成，删除了 {deleted_count} 个旧备份文件")
            
        except Exception as e:
            self.logger.error(f"清理旧备份文件失败: {e}")
    
    def list_backups(self) -> List[dict]:
        """
        列出所有备份文件
        
        Returns:
            List[dict]: 备份文件信息列表
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("admin_backup_*.db.*")):
            if backup_file.suffix == '.sha256':
                continue
                
            stat = backup_file.stat()
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'verified': self.verify_backup(str(backup_file))
            })
        
        return backups


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IP查询系统安全备份工具')
    parser.add_argument('action', choices=['backup', 'restore', 'verify', 'list', 'cleanup'],
                       help='执行的操作')
    parser.add_argument('--file', help='备份文件路径（用于restore和verify）')
    parser.add_argument('--target', help='恢复目标路径（用于restore）')
    parser.add_argument('--retention-days', type=int, default=30,
                       help='备份保留天数（用于cleanup）')
    
    args = parser.parse_args()
    
    backup_manager = SecurityBackup()
    
    if args.action == 'backup':
        backup_path = backup_manager.create_backup()
        if backup_path:
            print(f"备份创建成功: {backup_path}")
        else:
            print("备份创建失败")
            sys.exit(1)
    
    elif args.action == 'restore':
        if not args.file:
            print("错误: 需要指定备份文件路径")
            sys.exit(1)
        
        success = backup_manager.restore_backup(args.file, args.target)
        if success:
            print("备份恢复成功")
        else:
            print("备份恢复失败")
            sys.exit(1)
    
    elif args.action == 'verify':
        if not args.file:
            print("错误: 需要指定备份文件路径")
            sys.exit(1)
        
        success = backup_manager.verify_backup(args.file)
        if success:
            print("备份文件验证成功")
        else:
            print("备份文件验证失败")
            sys.exit(1)
    
    elif args.action == 'list':
        backups = backup_manager.list_backups()
        if backups:
            print("备份文件列表:")
            for backup in backups:
                status = "✓" if backup['verified'] else "✗"
                print(f"{status} {backup['filename']} ({backup['size']} bytes, {backup['created']})")
        else:
            print("没有找到备份文件")
    
    elif args.action == 'cleanup':
        backup_manager.cleanup_old_backups(args.retention_days)
        print(f"清理完成，保留最近 {args.retention_days} 天的备份")


if __name__ == '__main__':
    main()
