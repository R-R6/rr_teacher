"""
腾讯云 COS 对象存储上传服务
本地开发模式下使用本地文件存储
"""
import os
import logging
import shutil
from app.config import settings

logger = logging.getLogger(__name__)

# 本地存储目录
LOCAL_STORAGE_DIR = "./uploads"
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

# 尝试导入COS SDK
try:
    from qcloud_cos import CosConfig, CosS3Client
    HAS_COS_SDK = True
except ImportError:
    HAS_COS_SDK = False
    logger.info("qcloud_cos SDK未安装，使用本地文件存储模式")


def _get_cos_client():
    """获取COS客户端实例"""
    if not HAS_COS_SDK:
        return None
    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
    )
    return CosS3Client(config)


async def upload_to_cos(local_path: str, cos_key: str) -> str:
    """
    上传文件到腾讯云COS
    本地开发模式: 复制到本地uploads目录
    返回可访问的URL或本地路径
    """
    # 本地开发模式: 未配置COS或未安装SDK
    if not settings.COS_SECRET_ID or not HAS_COS_SDK:
        # 复制文件到本地存储
        dest_path = os.path.join(LOCAL_STORAGE_DIR, os.path.basename(cos_key))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(local_path, dest_path)
        logger.info(f"文件已保存到本地: {dest_path}")
        return f"/uploads/{os.path.basename(cos_key)}"

    # 生产模式: 上传到COS
    client = _get_cos_client()
    with open(local_path, "rb") as f:
        client.put_object(
            Bucket=settings.COS_BUCKET,
            Body=f,
            Key=cos_key,
            EnableMD5=False,
        )

    url = f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{cos_key}"
    return url


def get_cos_url(cos_key: str) -> str:
    """根据COS key获取访问URL"""
    if not settings.COS_SECRET_ID or not HAS_COS_SDK:
        return f"/uploads/{os.path.basename(cos_key)}"
    return f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{cos_key}"


async def delete_from_cos(cos_key: str) -> bool:
    """从COS删除文件"""
    if not settings.COS_SECRET_ID or not HAS_COS_SDK:
        # 本地模式: 删除本地文件
        local_path = os.path.join(LOCAL_STORAGE_DIR, os.path.basename(cos_key))
        if os.path.exists(local_path):
            os.remove(local_path)
        return True

    client = _get_cos_client()
    client.delete_object(
        Bucket=settings.COS_BUCKET,
        Key=cos_key,
    )
    return True
