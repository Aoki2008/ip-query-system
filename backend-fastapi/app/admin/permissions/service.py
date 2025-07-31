"""
权限管理服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import (
    Permission, Role, SystemPermissions, SystemRoles,
    PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate,
    user_roles, role_permissions
)
from ..models import AdminUser
from ...database import SessionLocal


class PermissionService:
    """权限管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """创建权限"""
        permission = Permission(
            name=permission_data.name,
            code=permission_data.code,
            description=permission_data.description,
            resource=permission_data.resource.value,
            action=permission_data.action.value,
            is_active=permission_data.is_active
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission
    
    def get_permission(self, permission_id: int) -> Optional[Permission]:
        """获取权限"""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """根据代码获取权限"""
        return self.db.query(Permission).filter(Permission.code == code).first()
    
    def list_permissions(self, skip: int = 0, limit: int = 100, 
                        resource: Optional[str] = None,
                        action: Optional[str] = None,
                        is_active: Optional[bool] = None) -> List[Permission]:
        """获取权限列表"""
        query = self.db.query(Permission)
        
        if resource:
            query = query.filter(Permission.resource == resource)
        if action:
            query = query.filter(Permission.action == action)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def update_permission(self, permission_id: int, 
                         permission_data: PermissionUpdate) -> Optional[Permission]:
        """更新权限"""
        permission = self.get_permission(permission_id)
        if not permission:
            return None
        
        update_data = permission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        
        self.db.commit()
        self.db.refresh(permission)
        return permission
    
    def delete_permission(self, permission_id: int) -> bool:
        """删除权限"""
        permission = self.get_permission(permission_id)
        if not permission:
            return False
        
        self.db.delete(permission)
        self.db.commit()
        return True


class RoleService:
    """角色管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_role(self, role_data: RoleCreate, created_by: int) -> Role:
        """创建角色"""
        role = Role(
            name=role_data.name,
            code=role_data.code,
            description=role_data.description,
            is_active=role_data.is_active,
            created_by=created_by
        )
        self.db.add(role)
        self.db.flush()  # 获取ID但不提交
        
        # 分配权限
        if role_data.permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def get_role(self, role_id: int) -> Optional[Role]:
        """获取角色"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_role_by_code(self, code: str) -> Optional[Role]:
        """根据代码获取角色"""
        return self.db.query(Role).filter(Role.code == code).first()
    
    def list_roles(self, skip: int = 0, limit: int = 100,
                   is_system: Optional[bool] = None,
                   is_active: Optional[bool] = None) -> List[Role]:
        """获取角色列表"""
        from sqlalchemy.orm import joinedload

        query = self.db.query(Role).options(joinedload(Role.permissions))

        if is_system is not None:
            query = query.filter(Role.is_system == is_system)
        if is_active is not None:
            query = query.filter(Role.is_active == is_active)

        return query.offset(skip).limit(limit).all()
    
    def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        role = self.get_role(role_id)
        if not role:
            return None
        
        # 系统角色不允许修改某些字段
        if role.is_system:
            # 系统角色只允许修改描述和状态
            if role_data.name is not None or role_data.permission_ids is not None:
                return None
        
        update_data = role_data.dict(exclude_unset=True, exclude={'permission_ids'})
        for field, value in update_data.items():
            setattr(role, field, value)
        
        # 更新权限
        if role_data.permission_ids is not None and not role.is_system:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        role = self.get_role(role_id)
        if not role or role.is_system:
            return False
        
        self.db.delete(role)
        self.db.commit()
        return True
    
    def assign_permissions(self, role_id: int, permission_ids: List[int]) -> bool:
        """为角色分配权限"""
        role = self.get_role(role_id)
        if not role or role.is_system:
            return False
        
        permissions = self.db.query(Permission).filter(
            Permission.id.in_(permission_ids)
        ).all()
        role.permissions = permissions
        
        self.db.commit()
        return True


class UserRoleService:
    """用户角色管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assign_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """为用户分配角色"""
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            return False
        
        roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()
        
        # 清除现有角色关联
        self.db.execute(
            user_roles.delete().where(user_roles.c.user_id == user_id)
        )
        
        # 添加新的角色关联
        for role in roles:
            self.db.execute(
                user_roles.insert().values(user_id=user_id, role_id=role.id)
            )
        
        self.db.commit()
        return True
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """获取用户角色"""
        return self.db.query(Role).join(user_roles).filter(
            user_roles.c.user_id == user_id
        ).all()
    
    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """获取用户权限"""
        return self.db.query(Permission).join(role_permissions).join(
            user_roles, role_permissions.c.role_id == user_roles.c.role_id
        ).filter(user_roles.c.user_id == user_id).distinct().all()
    
    def check_permission(self, user_id: int, permission_code: str) -> bool:
        """检查用户权限"""
        permission_count = self.db.query(Permission).join(role_permissions).join(
            user_roles, role_permissions.c.role_id == user_roles.c.role_id
        ).filter(
            and_(
                user_roles.c.user_id == user_id,
                Permission.code == permission_code,
                Permission.is_active == True
            )
        ).count()
        
        return permission_count > 0
    
    def check_resource_action(self, user_id: int, resource: str, action: str) -> bool:
        """检查用户对资源的操作权限"""
        permission_count = self.db.query(Permission).join(role_permissions).join(
            user_roles, role_permissions.c.role_id == user_roles.c.role_id
        ).filter(
            and_(
                user_roles.c.user_id == user_id,
                Permission.resource == resource,
                Permission.action == action,
                Permission.is_active == True
            )
        ).count()
        
        return permission_count > 0


class PermissionInitService:
    """权限初始化服务"""
    
    @staticmethod
    def init_default_permissions():
        """初始化默认权限"""
        db = SessionLocal()
        try:
            # 检查是否已初始化
            if db.query(Permission).count() > 0:
                return
            
            # 创建默认权限
            for perm_data in SystemPermissions.get_all_permissions():
                permission = Permission(
                    name=perm_data["name"],
                    code=perm_data["code"],
                    description=perm_data["description"],
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    is_active=True
                )
                db.add(permission)
            
            db.commit()
            print("✅ 默认权限初始化完成")
            
        except Exception as e:
            print(f"❌ 权限初始化失败: {e}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def init_default_roles():
        """初始化默认角色"""
        db = SessionLocal()
        try:
            # 检查是否已初始化
            if db.query(Role).count() > 0:
                return
            
            # 创建默认角色
            for role_data in SystemRoles.get_default_roles():
                role = Role(
                    name=role_data["name"],
                    code=role_data["code"],
                    description=role_data["description"],
                    is_system=role_data["is_system"],
                    is_active=True
                )
                db.add(role)
                db.flush()
                
                # 分配权限
                permission_codes = [p["code"] for p in role_data["permissions"]]
                permissions = db.query(Permission).filter(
                    Permission.code.in_(permission_codes)
                ).all()
                role.permissions = permissions
            
            db.commit()
            print("✅ 默认角色初始化完成")
            
        except Exception as e:
            print(f"❌ 角色初始化失败: {e}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def assign_admin_role():
        """为默认管理员分配超级管理员角色"""
        db = SessionLocal()
        try:
            # 查找默认管理员
            admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
            if not admin_user:
                return
            
            # 查找超级管理员角色
            super_admin_role = db.query(Role).filter(Role.code == SystemRoles.SUPER_ADMIN).first()
            if not super_admin_role:
                return
            
            # 检查是否已分配
            existing = db.execute(
                user_roles.select().where(
                    and_(
                        user_roles.c.user_id == admin_user.id,
                        user_roles.c.role_id == super_admin_role.id
                    )
                )
            ).first()
            
            if not existing:
                db.execute(
                    user_roles.insert().values(
                        user_id=admin_user.id,
                        role_id=super_admin_role.id
                    )
                )
                db.commit()
                print("✅ 默认管理员角色分配完成")
            
        except Exception as e:
            print(f"❌ 管理员角色分配失败: {e}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def init_all():
        """初始化所有权限数据"""
        print("🔧 初始化权限系统...")
        PermissionInitService.init_default_permissions()
        PermissionInitService.init_default_roles()
        PermissionInitService.assign_admin_role()
        print("✅ 权限系统初始化完成")
