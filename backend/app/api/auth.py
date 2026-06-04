"""
用户认证模块: 注册 / 登录 / 微信登录
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserRegisterReq, UserLoginReq, WechatLoginReq, UserInfoResp, TokenResp, ApiResp
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
            created_at=datetime.now(),
        )
        db.add(user)
        await db.flush()  # 确保生成ID

        return ApiResp(message="注册成功", data={"user_id": user.id})
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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
    通过wx.login()返回的code换取openid，自动创建或绑定用户
    """
    # 调用微信API换取openid (生产环境需要配置appid和secret)
    # 此处为简化实现，直接假设已获取到openid
    # ============ 生产环境替换 start ============
    import httpx

    # 微信官方接口
    wx_url = "https://api.weixin.qq.com/sns/jscode2session"
    # params = {
    #     "appid": settings.WECHAT_APPID,
    #     "secret": settings.WECHAT_SECRET,
    #     "js_code": req.code,
    #     "grant_type": "authorization_code",
    # }
    # async with httpx.AsyncClient() as client:
    #     wx_resp = await client.get(wx_url, params=params)
    #     wx_data = wx_resp.json()
    # openid = wx_data.get("openid")

    # 临时：用code作为openid(生产环境务必替换)
    openid = f"wechat_{req.code}"
    # ============ 生产环境替换 end ============

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
            hashed_password=hash_password(openid),  # 微信用户用openid做密码
            created_at=datetime.now(),
        )
        db.add(user)
    else:
        # 更新头像昵称
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
