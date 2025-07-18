from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")


@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(user_login: UserLogin, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.") 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """사용자 회원가입을 처리하는 API

    Args:
        user (User): 회원가입할 사용자 정보
        service (UserService, optional): 사용자 서비스 객체. Defaults to Depends(get_user_service).

    Raises:
        HTTPException: 중복된 이메일 등으로 회원가입 실패 시 발생

    Returns:
        BaseResponse[User]: 회원가입 성공 여부와 사용자 정보
    """
    try:
        user = service.register_user(user) 
        return BaseResponse(status="success", data=user, message="User registeration success.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """사용자 삭제를 처리하는 API

    Args:
        user_delete_request (UserDeleteRequest): 삭제할 사용자의 이메일 정보
        service (UserService, optional): 사용자 서비스 객체. Defaults to Depends(get_user_service).

    Raises:
        HTTPException: 사용자가 존재하지 않거나 삭제 실패 시 발생

    Returns:
        BaseResponse[User]: 삭제 성공 여부와 삭제된 사용자 정보
    """
    try:
        user = service.delete_user(user_delete_request.email) 
        return BaseResponse(status="success", data=user, message="User Deletion Success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    """사용자 비밀번호 변경을 처리하는 API

    Args:
        user_update (UserUpdate): 비밀번호 변경 요청 정보
        service (UserService, optional): 사용자 서비스 객체. Defaults to Depends(get_user_service).

    Raises:
        HTTPException: 비밀번호 변경 실패 시 발생

    Returns:
        BaseResponse[User]: 비밀번호 변경 성공 여부와 사용자 정보
    """
    try:
        user = service.update_user_pwd(user_update) 
        return BaseResponse(status="success", data=user, message="User password update success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))