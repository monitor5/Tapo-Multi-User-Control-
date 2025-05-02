# app/routers/plugs.py

from typing       import List
from fastapi      import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
import logging

from app.db       import get_session
from app.models   import PlugSession, User
from app.routers.auth import get_current_user
from app.services.pyp100 import pyp100_service
from app.schemas  import PlugInfo, PlugStatus
from app.dependencies import oauth2_scheme
from app.exceptions import (
    PlugNotFoundException,
    PlugAlreadyInUseException,
    PlugNotInUseException,
    TapoConnectionException
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/plugs", tags=["plugs"])


def get_user_model(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> User:
    """
    auth.get_current_user가 반환한 username(str)으로
    DB에서 User 모델을 꺼내 돌려줍니다.
    """
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found"
        )
    return user


def get_plug_or_404(name: str):
    if name not in pyp100_service.plugs:
        raise PlugNotFoundException(name)


def count_active(db: Session, name: str) -> int:
    return db.query(PlugSession).filter_by(plug_name=name).count()


def create_session(db: Session, name: str, user_id: int) -> bool:
    # 해당 사용자가 이미 해당 플러그를 사용 중인지 확인
    exists = db.query(PlugSession).filter_by(plug_name=name, user_id=user_id).first()
    
    # 이미 사용 중이면 새로 추가하지 않고 성공으로 반환
    if exists:
        logger.info(f"사용자(ID: {user_id})가 이미 플러그 '{name}'을 사용 중입니다.")
        return True
    
    # 신규 세션 추가
    logger.info(f"사용자(ID: {user_id})가 새로 플러그 '{name}'을 사용합니다.")
    sess = PlugSession(plug_name=name, user_id=user_id)
    db.add(sess)
    db.commit()
    return True


def delete_session(db: Session, name: str, user_id: int) -> bool:
    sess = db.query(PlugSession).filter_by(plug_name=name, user_id=user_id).first()
    if not sess:
        raise PlugNotInUseException(name)
    
    db.delete(sess)
    db.commit()
    return True


@router.get("/", response_model=List[PlugInfo], summary="플러그 목록 조회", 
            dependencies=[Security(oauth2_scheme)])
async def list_plugs(
    db: Session = Depends(get_session),
    user: User = Depends(get_user_model),
):
    result: List[PlugInfo] = []
    try:
        logger.info(f"플러그 목록 조회: 사용자 '{user.username}' (ID: {user.id})")
        
        for name, ip in pyp100_service.plugs.items():
            # 1) 상태 조회
            try:
                status_on = await pyp100_service.get_status(name)
            except Exception as e:
                logger.error(f"Failed to get status for plug {name}: {str(e)}")
                status_on = None

            # 2) 참여자 목록
            try:
                rows = (
                    db.query(PlugSession, User.username)
                    .join(User, PlugSession.user_id == User.id)
                    .filter(PlugSession.plug_name == name)
                    .all()
                )
                # 모든 사용자 이름을 문자열로 변환하여 저장
                users = [str(uname).strip() for _, uname in rows]
                logger.info(f"플러그 {name} 사용자 목록: {users}")
                
                # 현재 사용자가 플러그를 사용 중인지 확인 - 문자열 타입으로 비교
                current_username = str(user.username).strip()
                is_using = current_username in users
                logger.info(f"사용자 '{current_username}'가 '{name}' 플러그 사용 중: {is_using}")
                logger.debug(f"사용자 비교 상세: 현재={current_username}, 목록={users}, 타입={type(current_username)}")
                
            except Exception as e:
                logger.error(f"Failed to get users for plug {name}: {str(e)}")
                users = []

            result.append(PlugInfo(
                name=name,
                ip=ip,
                status=status_on,
                active_users=len(users),
                users=users,
            ))
        
        if not result:
            logger.warning("No plugs found in the service")
        return result
    except Exception as e:
        logger.error(f"Failed to list plugs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="플러그 목록을 불러오는데 실패했습니다"
        )


@router.post("/{name}/on", response_model=PlugStatus, status_code=201, 
             summary="플러그 사용 예약 및 ON", 
             dependencies=[Security(oauth2_scheme)])
async def reserve_on(
    name: str,
    db: Session = Depends(get_session),
    user: User    = Depends(get_user_model),
):
    get_plug_or_404(name)
    try:
        logger.info(f"플러그 {name} 사용 예약 요청: 사용자 '{user.username}' (ID: {user.id})")
        created = create_session(db, name, user.id)
        
        # 현재 active 세션 수 계산
        active = count_active(db, name)
        
        # 방금 추가된 사용자를 포함한 모든 사용자 목록 가져오기
        rows = (
            db.query(PlugSession, User.username)
            .join(User, PlugSession.user_id == User.id)
            .filter(PlugSession.plug_name == name)
            .all()
        )
        users_list = [str(uname).strip() for _, uname in rows]
        logger.info(f"플러그 {name}의 현재 사용자 목록: {users_list}")
        
        # 첫 번째 사용자인 경우 플러그 켜기
        if created and active == 1:
            logger.info(f"플러그 {name}를 ON으로 전환 (첫 번째 사용자)")
            await pyp100_service.turn_on(name)
        else:
            logger.info(f"플러그 {name}는 이미 사용 중 (총 {active}명)")
            
        return PlugStatus(name=name, status=True, active_users=active, users=users_list)
    except Exception as e:
        if isinstance(e, (PlugAlreadyInUseException, PlugNotFoundException)):
            raise
        logger.error(f"플러그 {name} 사용 예약 실패: {str(e)}")
        raise TapoConnectionException(name, str(e))


@router.post("/{name}/off", response_model=PlugStatus, status_code=200, 
            summary="플러그 예약 해제 및 OFF", 
            dependencies=[Security(oauth2_scheme)])
async def release_off(
    name: str,
    db: Session = Depends(get_session),
    user: User    = Depends(get_user_model),
):
    get_plug_or_404(name)
    try:
        logger.info(f"플러그 {name} 사용 해제 요청: 사용자 '{user.username}' (ID: {user.id})")
        delete_session(db, name, user.id)
        active = count_active(db, name)
        status_on = True
        
        # 남은 사용자 목록 가져오기
        rows = (
            db.query(PlugSession, User.username)
            .join(User, PlugSession.user_id == User.id)
            .filter(PlugSession.plug_name == name)
            .all()
        )
        users_list = [str(uname).strip() for _, uname in rows]
        logger.info(f"플러그 {name}의 남은 사용자 목록: {users_list}")
        
        if active == 0:
            logger.info(f"플러그 {name}를 OFF로 전환 (마지막 사용자 해제)")
            await pyp100_service.turn_off(name)
            status_on = False
        else:
            logger.info(f"플러그 {name}는 여전히 사용 중 (남은 사용자 {active}명)")
            
        return PlugStatus(name=name, status=status_on, active_users=active, users=users_list)
    except Exception as e:
        if isinstance(e, (PlugNotInUseException, PlugNotFoundException)):
            raise
        logger.error(f"플러그 {name} 사용 해제 실패: {str(e)}")
        raise TapoConnectionException(name, str(e))


@router.get("/{name}/status", response_model=PlugStatus, status_code=200, 
           summary="플러그 상태 조회", 
           dependencies=[Security(oauth2_scheme)])
async def plug_status(
    name: str,
    db: Session = Depends(get_session),
    user: User    = Depends(get_user_model),
):
    get_plug_or_404(name)
    try:
        status_on = await pyp100_service.get_status(name)
        active = count_active(db, name)
        
        # 사용자 목록 가져오기
        rows = (
            db.query(PlugSession, User.username)
            .join(User, PlugSession.user_id == User.id)
            .filter(PlugSession.plug_name == name)
            .all()
        )
        users_list = [str(uname).strip() for _, uname in rows]
        
        return PlugStatus(name=name, status=status_on, active_users=active, users=users_list)
    except Exception as e:
        raise TapoConnectionException(name, str(e))


@router.delete("/{name}/sessions", status_code=204, 
              summary="[Admin] 모든 세션 초기화", 
              dependencies=[Security(oauth2_scheme)])
async def force_clear(
    name: str,
    db: Session = Depends(get_session),
    user: User    = Depends(get_user_model),
):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )
    try:
        db.query(PlugSession).filter_by(plug_name=name).delete()
        db.commit()
        await pyp100_service.turn_off(name)
    except Exception as e:
        raise TapoConnectionException(name, str(e))
