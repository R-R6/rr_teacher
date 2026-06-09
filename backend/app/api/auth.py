"""
用户认证模块: 注册 / 登录 / 微信登录
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
import httpx

from app.database import get_db
from app.models import User
from app.config import settings
from app.schemas import UserRegisterReq, UserLoginReq, WechatLoginReq, UpdateProfileReq, UserInfoResp, TokenResp, ApiResp
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=ApiResp)
async def register(req: UserRegisterReq, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        result = await db.execute(select(User).where(User.username == req.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户名已被注册")

        # 检查手机号是否已存在
        if req.phone:
            result = await db.execute(select(User).where(User.phone == req.phone))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="手机号已被绑定")

        user = User(
            username=req.username,
            hashed_password=hash_password(req.password),
            role=req.role,
            nickname=req.nickname or req.username,
            school=req.school,
            phone=req.phone,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.flush()  # 确保生成ID

        return ApiResp(message="注册成功", data={"user_id": user.id})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")


@router.post("/login", response_model=ApiResp)
async def login(req: UserLoginReq, db: AsyncSession = Depends(get_db)):
    """用户名+密码登录"""
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    access_token, access_expire = create_access_token(user.id, user.role)
    refresh_token, _ = create_refresh_token(user.id)

    user_info = UserInfoResp.model_validate(user)
    token_data = TokenResp(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int((access_expire - datetime.now(timezone.utc)).total_seconds()),
        user=user_info,
    )
    return ApiResp(data=token_data.model_dump())


@router.post("/wechat-login", response_model=ApiResp)
async def wechat_login(req: WechatLoginReq, db: AsyncSession = Depends(get_db)):
    """
    微信小程序登录
    通过wx.login()返回的code调用jscode2session换取openid
    """
    # 检查微信配置
    if not settings.WECHAT_APPID or not settings.WECHAT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="微信登录未配置，请设置 WECHAT_APPID 和 WECHAT_SECRET 环境变量"
        )

    # 调用微信官方接口换取 openid + session_key
    wx_url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APPID,
        "secret": settings.WECHAT_SECRET,
        "js_code": req.code,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            wx_resp = await client.get(wx_url, params=params)
            wx_data = wx_resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="微信服务暂时不可用，请稍后重试")

    # 检查微信返回是否成功
    openid = wx_data.get("openid")
    if not openid:
        errcode = wx_data.get("errcode", "unknown")
        errmsg = wx_data.get("errmsg", "未知错误")
        raise HTTPException(
            status_code=401,
            detail=f"微信登录失败: [{errcode}] {errmsg}"
        )

    # session_key 可用于后续解密（如获取手机号）
    # session_key = wx_data.get("session_key")

    # 查找或创建用户
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=f"wx_{openid[-8:]}",
            openid=openid,
            nickname=req.nickname or f"微信用户{openid[-4:]}",
            avatar_url=req.avatar_url,
            role="teacher",  # 默认老师，后续可在小程序内选择
            hashed_password=hash_password(secrets.token_hex(32)),  # 微信用户用随机密码（不可通过密码登录）
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.flush()  # 确保生成ID
    else:
        # 更新头像昵称（如果本次登录有提供）
        if req.nickname:
            user.nickname = req.nickname
        if req.avatar_url:
            user.avatar_url = req.avatar_url

    access_token, access_expire = create_access_token(user.id, user.role)
    refresh_token, _ = create_refresh_token(user.id)

    user_info = UserInfoResp.model_validate(user)
    token_data = TokenResp(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int((access_expire - datetime.now(timezone.utc)).total_seconds()),
        user=user_info,
    )
    return ApiResp(data=token_data.model_dump())




@router.get("/me", response_model=ApiResp)
async def get_my_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return ApiResp(data=UserInfoResp.model_validate(current_user).model_dump())


@router.put("/me", response_model=ApiResp)
async def update_my_info(
    req: UpdateProfileReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息（昵称、头像、学校）"""
    if req.nickname is not None:
        current_user.nickname = req.nickname
    if req.avatar_url is not None:
        current_user.avatar_url = req.avatar_url
    if req.school is not None:
        current_user.school = req.school

    await db.flush()  # 持久化到数据库

    # 返回更新后的用户信息
    user_info = UserInfoResp.model_validate(current_user)
    return ApiResp(message="更新成功", data=user_info.model_dump())


@router.post("/refresh", response_model=ApiResp)
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """刷新访问令牌"""
    from app.auth import decode_token
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的刷新令牌")
    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    access_token, _ = create_access_token(user.id, user.role)
    return ApiResp(data={"access_token": access_token})


@router.post("/bind-phone", response_model=ApiResp)
async def bind_phone(
    phone: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    绑定手机号（预留接口）
    前端通过 <button open-type="getPhoneNumber"> 获取 encryptedData + iv
    后端用 session_key 解密得到手机号
    """
    # TODO: 实现阶段需要传入 encryptedData 和 iv，用 session_key 解密
    # 目前简化为直接传手机号

    # 检查手机号是否已被其他用户绑定
    result = await db.execute(
        select(User).where(User.phone == phone, User.id != current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该手机号已被其他账号绑定")

    current_user.phone = phone
    return ApiResp(message="手机号绑定成功")
