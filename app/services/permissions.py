from typing import List
from sqlalchemy.orm import Session
from app.models import User, UserPlugPermission
from app.services.pyp100 import pyp100_service
import logging

logger = logging.getLogger(__name__)


def get_user_allowed_plugs(user: User, db: Session) -> List[str]:
    """사용자가 접근 가능한 플러그 목록을 반환"""
    
    # 관리자는 모든 플러그에 접근 가능
    if user.role == "admin":
        return list(pyp100_service.plugs.keys())
    
    # 일반 사용자는 권한이 부여된 플러그만 접근 가능
    permissions = db.query(UserPlugPermission).filter_by(user_id=user.id).all()
    allowed_plugs = [perm.plug_name for perm in permissions]
    
    # 권한이 있는 플러그 중에서 실제로 존재하는 플러그만 반환
    existing_plugs = pyp100_service.plugs.keys()
    return [plug for plug in allowed_plugs if plug in existing_plugs]


def can_user_access_plug(user: User, plug_name: str, db: Session) -> bool:
    """사용자가 특정 플러그에 접근할 수 있는지 확인"""
    
    # 관리자는 모든 플러그에 접근 가능
    if user.role == "admin":
        return True
    
    # 플러그가 존재하는지 확인
    if plug_name not in pyp100_service.plugs:
        return False
    
    # 사용자에게 해당 플러그 권한이 있는지 확인
    permission = db.query(UserPlugPermission).filter_by(
        user_id=user.id, 
        plug_name=plug_name
    ).first()
    
    return permission is not None


def grant_plug_permission(user_id: int, plug_name: str, db: Session) -> bool:
    """사용자에게 플러그 권한을 부여"""
    
    # 플러그가 존재하는지 확인
    if plug_name not in pyp100_service.plugs:
        logger.warning(f"존재하지 않는 플러그에 권한 부여 시도: {plug_name}")
        return False
    
    # 이미 권한이 있는지 확인
    existing = db.query(UserPlugPermission).filter_by(
        user_id=user_id, 
        plug_name=plug_name
    ).first()
    
    if existing:
        logger.info(f"사용자 {user_id}는 이미 플러그 {plug_name}에 대한 권한이 있습니다")
        return True
    
    # 새 권한 생성
    permission = UserPlugPermission(user_id=user_id, plug_name=plug_name)
    db.add(permission)
    
    try:
        db.commit()
        logger.info(f"사용자 {user_id}에게 플러그 {plug_name} 권한 부여 성공")
        return True
    except Exception as e:
        logger.error(f"플러그 권한 부여 실패: {e}")
        db.rollback()
        return False


def revoke_plug_permission(user_id: int, plug_name: str, db: Session) -> bool:
    """사용자의 플러그 권한을 회수"""
    
    permission = db.query(UserPlugPermission).filter_by(
        user_id=user_id, 
        plug_name=plug_name
    ).first()
    
    if not permission:
        logger.warning(f"권한이 없는 플러그에서 권한 회수 시도: 사용자 {user_id}, 플러그 {plug_name}")
        return True  # 이미 권한이 없으므로 성공으로 처리
    
    try:
        db.delete(permission)
        db.commit()
        logger.info(f"사용자 {user_id}의 플러그 {plug_name} 권한 회수 성공")
        return True
    except Exception as e:
        logger.error(f"플러그 권한 회수 실패: {e}")
        db.rollback()
        return False


def get_all_users_with_permissions(db: Session) -> List[dict]:
    """모든 사용자와 그들의 플러그 권한을 반환"""
    
    users = db.query(User).all()
    result = []
    
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "allowed_plugs": get_user_allowed_plugs(user, db)
        }
        result.append(user_data)
    
    return result 