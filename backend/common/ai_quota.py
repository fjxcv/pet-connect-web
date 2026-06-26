"""
AI 配额检查。
"""

from django.utils import timezone

from system.models import AiInvocationLog, PlatformConfig


class AiQuotaExceededError(Exception):
    """超配额异常"""
    def __init__(self, message, quota_type='daily'):
        super().__init__(message)
        self.quota_type = quota_type


def _get_config_int(key, default=0):
    """
    功能：从 PlatformConfig 读取整数配置值（ai_daily_limit 等）。
    参数：key — 配置键；default — 默认值
    返回：int
    """
    try:
        row = PlatformConfig.objects.get(config_key=key)
        return max(0, int(str(row.config_value).strip() or '0'))
    except (PlatformConfig.DoesNotExist, ValueError, TypeError):
        return default


def get_ai_usage_stats():
    """
    功能：统计今日与累计 AI 调用次数 + 平台配额配置。
    返回：dict（today_count, total_count, daily_limit, total_limit）
    【权限】内部调用，user/admin 配额检查前置
    """
    today = timezone.now().date()
    return {
        'today_count': AiInvocationLog.objects.filter(created_at__date=today).count(),
        'total_count': AiInvocationLog.objects.count(),
        'daily_limit': _get_config_int('ai_daily_limit', 0),
        'total_limit': _get_config_int('ai_total_limit', 0),
    }


def check_ai_quota(user):
    """
    功能：检查 user/admin 的 AI 配额（daily/total），超限抛异常。
    参数：user — 已登录用户
    返回：None（正常）或抛 AiQuotaExceededError
    【权限】仅 user/admin 可调用；visitor 由上层 IsAuthenticated 拦截
    """
    stats = get_ai_usage_stats()
    daily_limit = stats['daily_limit']
    total_limit = stats['total_limit']

    # 分支：今日超限 → 抛 daily 异常
    if daily_limit > 0 and stats['today_count'] >= daily_limit:
        raise AiQuotaExceededError(
            f'\u4eca\u65e5 AI \u8c03\u7528\u5df2\u8fbe\u4e0a\u9650\uff08{stats["today_count"]}/{daily_limit}\uff09\uff0c\u8bf7\u660e\u5929\u518d\u8bd5\u6216\u8054\u7cfb\u7ba1\u7406\u5458\u3002',
            quota_type='daily',
        )
    # 分支：累计超限 → 抛 total 异常
    if total_limit > 0 and stats['total_count'] >= total_limit:
        raise AiQuotaExceededError(
            f'AI \u7d2f\u8ba1\u8c03\u7528\u5df2\u8fbe\u4e0a\u9650\uff08{stats["total_count"]}/{total_limit}\uff09\uff0c\u8bf7\u8054\u7cfb\u7ba1\u7406\u5458\u3002',
            quota_type='total',
        )


def log_quota_exceeded(user, feature_type, request_meta=''):
    """
    功能：配额超限时写入 AiInvocationLog（success=False）。
    参数：user, feature_type, request_meta
    """
    AiInvocationLog.objects.create(
        user=user,
        feature_type=feature_type,
        request_meta=request_meta or '',
        result_meta='quota_exceeded',
        success=False,
    )
