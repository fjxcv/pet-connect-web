"""
审计日志与 IP 工具。
"""


def write_operation_log(operator, module, action, content, target_type=None, target_id=None, ip_address=None):
    """
    功能：写入 OperationLog（后台审计用）。
    参数：operator（admin 用户）, module, action, content, target_*, ip_address
    【权限】仅 admin 操作后调用
    """
    from system.models import OperationLog

    OperationLog.objects.create(
        operator=operator,
        module=module,
        action=action,
        content=content,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip_address,
    )


def get_client_ip(request):
    """
    功能：从 request.META 提取真实客户端 IP（支持 X-Forwarded-For）。
    参数：request
    返回：str IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
