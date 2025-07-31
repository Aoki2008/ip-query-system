"""
权限管理路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .models import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    UserRoleAssignment, RolePermissionAssignment,
    PermissionCheck, UserPermissions, PermissionMatrix,
    ResourceType, ActionType
)
from .service import PermissionService, RoleService, UserRoleService
from ..models import AdminUser
from ..auth.dependencies import get_current_active_user, require_super_admin
from ...database import get_db

router = APIRouter(prefix="/api/admin/permissions", tags=["权限管理"])


# 权限管理路由

@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建权限（仅超级管理员）"""
    service = PermissionService(db)
    
    # 检查权限代码是否已存在
    existing = service.get_permission_by_code(permission_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限代码已存在"
        )
    
    permission = service.create_permission(permission_data)
    return PermissionResponse.from_orm(permission)


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource: Optional[ResourceType] = None,
    action: Optional[ActionType] = None,
    is_active: Optional[bool] = None,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取权限列表"""
    service = PermissionService(db)
    
    permissions = service.list_permissions(
        skip=skip,
        limit=limit,
        resource=resource.value if resource else None,
        action=action.value if action else None,
        is_active=is_active
    )
    
    return [PermissionResponse.from_orm(p) for p in permissions]


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取权限详情"""
    service = PermissionService(db)
    permission = service.get_permission(permission_id)
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    return PermissionResponse.from_orm(permission)


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """更新权限（仅超级管理员）"""
    service = PermissionService(db)
    permission = service.update_permission(permission_id, permission_data)
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    return PermissionResponse.from_orm(permission)


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """删除权限（仅超级管理员）"""
    service = PermissionService(db)
    
    if not service.delete_permission(permission_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    return {"message": "权限已删除"}


# 角色管理路由

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建角色（仅超级管理员）"""
    service = RoleService(db)
    
    # 检查角色代码是否已存在
    existing = service.get_role_by_code(role_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色代码已存在"
        )
    
    role = service.create_role(role_data, current_user.id)
    return RoleResponse.from_orm(role)


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_system: Optional[bool] = None,
    is_active: Optional[bool] = None,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    service = RoleService(db)
    
    roles = service.list_roles(
        skip=skip,
        limit=limit,
        is_system=is_system,
        is_active=is_active
    )
    
    return [RoleResponse.from_orm(r) for r in roles]


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取角色详情"""
    service = RoleService(db)
    role = service.get_role(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return RoleResponse.from_orm(role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """更新角色（仅超级管理员）"""
    service = RoleService(db)
    role = service.update_role(role_id, role_data)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在或为系统角色"
        )
    
    return RoleResponse.from_orm(role)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """删除角色（仅超级管理员）"""
    service = RoleService(db)
    
    if not service.delete_role(role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在或为系统角色"
        )
    
    return {"message": "角色已删除"}


@router.post("/roles/{role_id}/permissions")
async def assign_role_permissions(
    role_id: int,
    assignment: RolePermissionAssignment,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """为角色分配权限（仅超级管理员）"""
    service = RoleService(db)
    
    if not service.assign_permissions(role_id, assignment.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在或为系统角色"
        )
    
    return {"message": "权限分配成功"}


# 用户角色管理路由

@router.post("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: int,
    assignment: UserRoleAssignment,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """为用户分配角色（仅超级管理员）"""
    service = UserRoleService(db)
    
    if not service.assign_roles(user_id, assignment.role_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {"message": "角色分配成功"}


@router.get("/users/{user_id}/permissions", response_model=UserPermissions)
async def get_user_permissions(
    user_id: int,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户权限"""
    # 只能查看自己的权限，或者超级管理员可以查看所有用户权限
    if user_id != current_user.id and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看其他用户权限"
        )
    
    service = UserRoleService(db)
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    roles = service.get_user_roles(user_id)
    permissions = service.get_user_permissions(user_id)
    
    return UserPermissions(
        user_id=user.id,
        username=user.username,
        roles=[RoleResponse.from_orm(r) for r in roles],
        permissions=[PermissionResponse.from_orm(p) for p in permissions]
    )


@router.post("/check")
async def check_permission(
    permission_check: PermissionCheck,
    current_user: AdminUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """检查当前用户权限"""
    service = UserRoleService(db)
    
    has_permission = service.check_resource_action(
        current_user.id,
        permission_check.resource.value,
        permission_check.action.value
    )
    
    return {
        "user_id": current_user.id,
        "resource": permission_check.resource.value,
        "action": permission_check.action.value,
        "has_permission": has_permission
    }


@router.get("/matrix", response_model=PermissionMatrix)
async def get_permission_matrix(
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """获取权限矩阵（仅超级管理员）"""
    permission_service = PermissionService(db)
    role_service = RoleService(db)
    
    # 获取所有资源和操作
    permissions = permission_service.list_permissions(limit=1000)
    resources = list(set(p.resource for p in permissions))
    actions = list(set(p.action for p in permissions))
    
    # 获取所有角色及其权限
    roles = role_service.list_roles(limit=1000)
    role_matrix = []
    
    for role in roles:
        role_permissions = {f"{p.resource}:{p.action}": True for p in role.permissions}
        role_data = {
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "is_system": role.is_system,
            "permissions": role_permissions
        }
        role_matrix.append(role_data)
    
    return PermissionMatrix(
        resources=resources,
        actions=actions,
        roles=role_matrix
    )
