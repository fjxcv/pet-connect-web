# -*- coding: utf-8 -*-
"""Patch portal/cms/lostfound 9 files with Chinese comments (comments only)."""
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"


def patch(rel, pairs):
    path = BACKEND / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            print(f"WARNING missing in {rel}: {old[:60]!r}")
            continue
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("patched", rel)


# ========== portal ==========
patch("portal/models.py", [
    ('"""\n妯″潡璇存槑锛歱ortal 妯″潡鏁版嵁妯″瀷锛圤RM锛夈?銊1?7\n"""',
     '"""\nportal 模块：首页轮播图数据模型。\n【权限】visitor/user 仅读公开；admin 可增删改。\n"""\n'),
    ('class PortalCarousel(models.Model):\n    """棣栭〉杞?鎾?鍥?1?7"""',
     'class PortalCarousel(models.Model):\n    """\n    功能：首页轮播图（图片+链接+排序+上下线）。\n    【权限】visitor/user：list/retrieve 仅 status=1；admin：全部 CRUD\n    """'),
    ('    STATUS_CHOICES = [(0, \'Offline\'), (1, \'Online\')]', '    # 字段说明：0 下线，1 上线（默认上线）'),
    ('    title = models.CharField(max_length=100, blank=True, null=True)', '    # 字段说明：轮播标题（可选）'),
    ('    image_url = models.CharField(max_length=500)', '    # 字段说明：图片 URL（必填）'),
    ('    link_url = models.CharField(max_length=500, blank=True, null=True)', '    # 字段说明：点击跳转链接（可选）'),
    ('    sort_order = models.IntegerField(default=0)', '    # 字段说明：排序权重，数字越小越靠前'),
    ('    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)', '    # 字段说明：上下线状态'),
    ('    created_at = models.DateTimeField(auto_now_add=True)', '    # 字段说明：创建时间'),
    ('    updated_at = models.DateTimeField(auto_now=True)', '    # 字段说明：最后更新时间'),
])

patch("portal/serializers.py", [
    ('"""\n妯″潡璇存槑锛歱ortal 妯″潡搴忓垪鍖栧櫒銆?1?7\n"""',
     '"""\nportal 序列化器：轮播图序列化。\n"""\n'),
    ('class PortalCarouselSerializer(serializers.ModelSerializer):\n\n    class Meta:',
     'class PortalCarouselSerializer(serializers.ModelSerializer):\n    """轮播图序列化器（字段全暴露）。【权限】admin 写，visitor 读公开"""\n\n    class Meta:'),
])

patch("portal/views.py", [
    ('"""\n妯″潡璇存槑锛歱ortal 妯″潡 API 瑙嗗浘銆?1?7\n"""',
     '"""\nportal 视图：轮播图管理 + 首页统计 + 首页聚合数据。\n"""\n'),
    ('class PortalCarouselViewSet(viewsets.ModelViewSet):\n    """\u9996\u9875\u8f6e\u64ad\u56fe\u7ba1\u7406"""',
     'class PortalCarouselViewSet(viewsets.ModelViewSet):\n    """\n    功能：轮播图 CRUD。\n    【权限】list/retrieve：visitor 公开；其余：admin\n    """'),
    ("        if self.action in ['list', 'retrieve']:\n            return [permissions.AllowAny()]\n        return [IsAdminRole()]",
     "        # 分支：list/retrieve 游客可看；create/update/delete 仅 admin\n        if self.action in ['list', 'retrieve']:\n            return [permissions.AllowAny()]\n        return [IsAdminRole()]"),
    ("        if self.action == 'list' and not (\n            self.request.user.is_authenticated\n            and getattr(getattr(self.request.user, 'profile', None), 'role', None) == 'admin'\n        ):\n            qs = qs.filter(status=1)",
     "        # 分支：非 admin 的 list 只返回 status=1（已上线）的轮播\n        if self.action == 'list' and not (\n            self.request.user.is_authenticated\n            and getattr(getattr(self.request.user, 'profile', None), 'role', None) == 'admin'\n        ):\n            qs = qs.filter(status=1)"),
    ('class PortalStatsView(APIView):\n    """\u9996\u9875\u6838\u5fc3\u6570\u636e\u7edf\u8ba1"""',
     'class PortalStatsView(APIView):\n    """\n    功能：首页核心统计数字（救助数、领养数、寻主中、今日上报）。\n    【权限】visitor/user/admin 均可匿名访问\n    """'),
    ('class PortalDashboardView(APIView):\n    """\u9996\u9875\u6700\u65b0\u52a8\u6001\u805a\u5408"""',
     'class PortalDashboardView(APIView):\n    """\n    功能：首页聚合数据（公告 3 条 + 科普 3 条 + 紧急寻主 3 条 + 可领养宠物 4 条）。\n    【权限】visitor/user/admin 均可匿名访问\n    """'),
])

# ========== cms ==========
patch("cms/models.py", [
    ('"""\n妯″潡璇存槑锛歝ms 妯″潡鏁版嵁妯″瀷锛圤RM锛夈?銊1?7\n"""',
     '"""\ncms 模块：文章分类、文章（科普/公告/法规/救助案例）、收藏模型。\n【权限】visitor 读公开；user 可收藏；admin 增删改。\n"""\n'),
    ('class CmsCategory(models.Model):\n    """鏂囩珷鍒嗙被"""',
     'class CmsCategory(models.Model):\n    """\n    功能：文章分类（名称、描述、排序、启用/禁用）。\n    【权限】visitor/user 读启用；admin 增删改\n    """'),
    ('    STATUS_CHOICES = [(0, \'Disabled\'), (1, \'Enabled\')]', '    # 字段说明：0 禁用，1 启用'),
    ('    name = models.CharField(max_length=50)', '    # 字段说明：分类名称'),
    ('    description = models.CharField(max_length=200, blank=True, null=True)', '    # 字段说明：分类描述'),
    ('    sort_order = models.IntegerField(default=0)', '    # 字段说明：排序'),
    ('    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)', '    # 字段说明：启用状态'),
    ('class CmsArticle(models.Model):\n    """鏂囩珷/鍏?鍛?/娉曡??/鏁戝姪妗堜緥"""',
     'class CmsArticle(models.Model):\n    """\n    功能：文章/公告/法规/救助案例（支持置顶、分类、作者、发布时间）。\n    【权限】visitor/user 读 status=1；admin 全部\n    """'),
    ('    ARTICLE_TYPE_CHOICES = [', '    # 字段说明：文章类型（science 科普、announcement 公告、law 法规、rescue_case 救助案例）'),
    ('    STATUS_CHOICES = [(0, \'Draft\'), (1, \'Published\'), (2, \'Offline\')]', '    # 字段说明：0 草稿，1 已发布，2 下线'),
    ('    category = models.ForeignKey(', '    # 字段说明：所属分类（可空）'),
    ('    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name=\'cms_articles\')', '    # 字段说明：作者（管理员）'),
    ('    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPE_CHOICES)', '    # 字段说明：类型'),
    ('    title = models.CharField(max_length=200)', '    # 字段说明：标题'),
    ('    summary = models.CharField(max_length=500, blank=True, null=True)', '    # 字段说明：摘要'),
    ('    content = models.TextField()', '    # 字段说明：正文（Markdown）'),
    ('    cover_url = models.CharField(max_length=500, blank=True, null=True)', '    # 字段说明：封面图'),
    ('    view_count = models.IntegerField(default=0)', '    # 字段说明：阅读量'),
    ('    is_pinned = models.BooleanField(default=False)', '    # 字段说明：是否置顶'),
    ('    sort_weight = models.IntegerField(default=0)', '    # 字段说明：排序权重'),
    ('    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)', '    # 字段说明：发布状态'),
    ('    published_at = models.DateTimeField(blank=True, null=True)', '    # 字段说明：发布时间'),
    ('class ArticleFavorite(models.Model):\n    """鏂囩珷鏀惰棌"""',
     'class ArticleFavorite(models.Model):\n    """\n    功能：用户收藏文章（唯一约束 article+user）。\n    【权限】user：本人收藏；admin：可看全部\n    """'),
])

patch("cms/serializers.py", [
    ('"""\n妯″潡璇存槑锛歝ms 妯″潡搴忓垪鍖栧櫒銆?1?7\n"""',
     '"""\ncms 序列化器：分类、文章、收藏序列化（含作者、分类名、是否收藏）。\n"""\n'),
    ('class CmsCategorySerializer(serializers.ModelSerializer):\n    class Meta:',
     'class CmsCategorySerializer(serializers.ModelSerializer):\n    """分类序列化器。【权限】admin 写，visitor 读"""\n    class Meta:'),
    ('class CmsArticleSerializer(serializers.ModelSerializer):\n    author = UserSerializer(read_only=True)\n    category_name = serializers.CharField(source=\'category.name\', read_only=True)\n    is_favorited = serializers.SerializerMethodField()',
     'class CmsArticleSerializer(serializers.ModelSerializer):\n    """\n    文章序列化器。\n    字段：author（只读）、category_name（只读）、is_favorited（当前用户是否收藏）。\n    【权限】visitor 读公开；user 可收藏\n    """\n    author = UserSerializer(read_only=True)\n    category_name = serializers.CharField(source=\'category.name\', read_only=True)\n    is_favorited = serializers.SerializerMethodField()'),
    ('    def get_is_favorited(self, obj):\n        request = self.context.get(\'request\')\n        if request and request.user.is_authenticated:\n            return ArticleFavorite.objects.filter(article=obj, user=request.user).exists()\n        return False',
     '    def get_is_favorited(self, obj):\n        """\n        功能：判断当前登录用户是否已收藏该文章。\n        返回：bool\n        """'),
    ('class ArticleFavoriteItemSerializer(serializers.ModelSerializer):\n    article = CmsArticleSerializer(read_only=True)\n    class Meta:',
     'class ArticleFavoriteItemSerializer(serializers.ModelSerializer):\n    """我的收藏列表项（嵌套文章详情）。【权限】user 本人"""\n    article = CmsArticleSerializer(read_only=True)\n    class Meta:'),
])

patch("cms/views.py", [
    ('"""\n妯″潡璇存槑锛歝ms 妯″潡 API 瑙嗗浘銆?1?7\n"""',
     '"""\ncms 视图：分类管理、文章 CRUD + 收藏、我的收藏、公告专区。\n"""\n'),
    ('class CmsCategoryViewSet(viewsets.ModelViewSet):\n    """鏂囩珷鍒嗙被绠＄悊"""',
     'class CmsCategoryViewSet(viewsets.ModelViewSet):\n    """\n    功能：文章分类管理。\n    【权限】list/retrieve：visitor；其余：admin\n    """'),
    ("        if self.action in ['list', 'retrieve']:\n            return [permissions.AllowAny()]\n        return [IsAdminRole()]",
     "        # 分支：游客可读分类；写操作仅 admin\n        if self.action in ['list', 'retrieve']:\n            return [permissions.AllowAny()]\n        return [IsAdminRole()]"),
    ('class CmsArticleViewSet(viewsets.ModelViewSet):\n    """鏂囩珷/鍏?鍛?/娉曡??/鏁戝姪妗堜緥 CRUD"""',
     'class CmsArticleViewSet(viewsets.ModelViewSet):\n    """\n    功能：文章 CRUD + 收藏动作。\n    【权限】list/retrieve：visitor；favorite：user；其余：admin\n    """'),
    ("        if self.action in ['list', 'retrieve']:\n            return [permissions.AllowAny()]\n        if self.action == 'favorite':\n            return [permissions.IsAuthenticated(), IsActiveUser()]\n        return [IsAdminRole()]",
     "        # 分支：list/retrieve 公开；favorite 需要登录+未封禁；其余 admin\n        if self.action in ['list', 'retrieve']:\n            return [permissions.AllowAny()]\n        if self.action == 'favorite':\n            return [permissions.IsAuthenticated(), IsActiveUser()]\n        return [IsAdminRole()]"),
    ("        if self.action in ['list', 'retrieve'] and not (self.request.user.is_authenticated and getattr(self.request.user.profile, 'role', None) == 'admin'):\n            qs = qs.filter(status=1)",
     "        # 分支：非 admin 的 list/retrieve 只返回已发布（status=1）的文章\n        if self.action in ['list', 'retrieve'] and not (self.request.user.is_authenticated and getattr(self.request.user.profile, 'role', None) == 'admin'):\n            qs = qs.filter(status=1)"),
    ('    def perform_create(self, serializer):\n        serializer.save(author=self.request.user)',
     '    def perform_create(self, serializer):\n        """\n        功能：创建文章时自动设置 author 为当前用户。\n        【权限】admin\n        """\n        serializer.save(author=self.request.user)'),
    ('    def retrieve(self, request, *args, **kwargs):\n        instance = self.get_object()\n        if instance.status == 1:\n            CmsArticle.objects.filter(pk=instance.pk).update(view_count=F(\'view_count\') + 1)\n            instance.refresh_from_db()\n        return super().retrieve(request, *args, **kwargs)',
     '    def retrieve(self, request, *args, **kwargs):\n        """\n        功能：详情接口，status=1 时阅读量 +1。\n        """\n        instance = self.get_object()\n        if instance.status == 1:\n            CmsArticle.objects.filter(pk=instance.pk).update(view_count=F(\'view_count\') + 1)\n            instance.refresh_from_db()\n        return super().retrieve(request, *args, **kwargs)'),
    ('    def perform_update(self, serializer):\n        article = serializer.save()\n        if article.status == 1 and not article.published_at:\n            article.published_at = timezone.now()\n            article.save(update_fields=[\'published_at\'])',
     '    def perform_update(self, serializer):\n        """\n        功能：更新时若首次发布则自动填充 published_at。\n        """\n        article = serializer.save()\n        if article.status == 1 and not article.published_at:\n            article.published_at = timezone.now()\n            article.save(update_fields=[\'published_at\'])'),
    ('    @action(detail=True, methods=[\'post\', \'delete\'], url_path=\'favorite\')\n    def favorite(self, request, pk=None):\n        article = self.get_object()\n        if article.status != 1:\n            return Response(\n                {\'detail\': \'浠呭彲鏀惰棌宸插彂甯冪殑鏂囩珷\'},\n                status=status.HTTP_400_BAD_REQUEST,\n            )\n        if request.method == \'POST\':\n            ArticleFavorite.objects.get_or_create(article=article, user=request.user)\n            return Response({\'detail\': \'Favorited\'})\n        ArticleFavorite.objects.filter(article=article, user=request.user).delete()\n        return Response({\'detail\': \'Favorite removed\'})',
     '    @action(detail=True, methods=[\'post\', \'delete\'], url_path=\'favorite\')\n    def favorite(self, request, pk=None):\n        """\n        功能：收藏/取消收藏（仅 status=1 的文章可收藏）。\n        【权限】user\n        """\n        article = self.get_object()\n        if article.status != 1:\n            return Response(\n                {\'detail\': \'浠呭彲鏀惰棌宸插彂甯冪殑鏂囩珷\'},\n                status=status.HTTP_400_BAD_REQUEST,\n            )\n        if request.method == \'POST\':\n            ArticleFavorite.objects.get_or_create(article=article, user=request.user)\n            return Response({\'detail\': \'Favorited\'})\n        ArticleFavorite.objects.filter(article=article, user=request.user).delete()\n        return Response({\'detail\': \'Favorite removed\'})'),
    ('class MyArticleFavoritesView(APIView):\n    """鎴戠殑鏂囩珷鏀惰棌鍒楄〃"""',
     'class MyArticleFavoritesView(APIView):\n    """\n    功能：我的收藏列表（仅 status=1 的文章）。\n    【权限】user（需登录未封禁）\n    """'),
    ('class CmsAnnouncementView(APIView):\n    """鍏?鍛婁笓鍖?"""',
     'class CmsAnnouncementView(APIView):\n    """\n    功能：公告专区（type=announcement, status=1）。\n    【权限】visitor/user/admin 均可访问\n    """'),
])

# ========== lostfound ==========
patch("lostfound/models.py", [
    ('"""\n妯″潡璇存槑锛歭ostfound 妯″潡鏁版嵁妯″瀷锛圤RM锛夈?銊1?7\n"""',
     '"""\nlostfound 模块：报失/寻主帖子模型（支持坐标、报酬、状态流转）。\n【权限】visitor 读公开；user 可发布/修改本人；admin 全部\n"""\n'),
    ('class LostFoundPost(models.Model):\n    """鎶ュけ/瀵讳富璁板綍"""',
     'class LostFoundPost(models.Model):\n    """\n    功能：报失（lost）/寻主（found）帖子。\n    状态流转：searching → found / cancelled。\n    【权限】visitor 读；user 发布/修改本人；admin 全部\n    """'),
    ('    POST_TYPE_CHOICES = [(\'lost\', \'Lost\'), (\'found\', \'Found\')]', '    # 字段说明：帖子类型（lost 报失 / found 寻主）'),
    ('    STATUS_CHOICES = [', '    # 字段说明：searching 寻找中、found 已找到、cancelled 已取消'),
    ('    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name=\'lost_found_posts\')', '    # 字段说明：发布者（登录用户）'),
    ('    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)', '    # 字段说明：类型'),
    ('    pet_species = models.CharField(max_length=50)', '    # 字段说明：宠物种类（猫/狗/...）'),
    ('    features = models.TextField()', '    # 字段说明：特征描述'),
    ('    photo_urls = models.JSONField(default=list, blank=True)', '    # 字段说明：照片 URL 列表（至少 1 张）'),
    ('    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)', '    # 字段说明：纬度（6 位小数）'),
    ('    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)', '    # 字段说明：经度（6 位小数）'),
    ('    address_text = models.CharField(max_length=255)', '    # 字段说明：地址文本（必填）'),
    ('    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)', '    # 字段说明：悬赏金额（默认 0）'),
    ('    contact_phone = models.CharField(max_length=20, blank=True, null=True)', '    # 字段说明：联系电话（本人/ admin 可见，其余脱敏）'),
    ('    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=\'searching\')', '    # 字段说明：状态'),
])

patch("lostfound/serializers.py", [
    ('"""\n妯″潡璇存槑锛歭ostfound 妯″潡搴忓垪鍖栧櫒銆?1?7\n"""',
     '"""\nlostfound 序列化器：坐标精度处理 + 电话脱敏（本人/admin 可见）。\n"""\n'),
    ('def _round_coordinate(value):\n    if value is None or value == \'\':\n        return None\n    return Decimal(str(value)).quantize(Decimal(\'0.000001\'), rounding=ROUND_HALF_UP)',
     'def _round_coordinate(value):\n    """\n    功能：坐标保留 6 位小数（Haversine 需要）。\n    """\n    if value is None or value == \'\':\n        return None\n    return Decimal(str(value)).quantize(Decimal(\'0.000001\'), rounding=ROUND_HALF_UP)'),
    ('class CoordinateField(serializers.DecimalField):\n    def __init__(self, **kwargs):\n        kwargs.setdefault(\'max_digits\', 9)\n        kwargs.setdefault(\'decimal_places\', 6)\n        kwargs.setdefault(\'required\', False)\n        kwargs.setdefault(\'allow_null\', True)\n        super().__init__(**kwargs)\n    def to_internal_value(self, data):\n        if data in (None, \'\'):\n            return None\n        return super().to_internal_value(_round_coordinate(data))',
     'class CoordinateField(serializers.DecimalField):\n    """\n    功能：自定义坐标字段，自动 6 位小数 + 可空。\n    """\n    def __init__(self, **kwargs):\n        kwargs.setdefault(\'max_digits\', 9)\n        kwargs.setdefault(\'decimal_places\', 6)\n        kwargs.setdefault(\'required\', False)\n        kwargs.setdefault(\'allow_null\', True)\n        super().__init__(**kwargs)\n    def to_internal_value(self, data):\n        if data in (None, \'\'):\n            return None\n        return super().to_internal_value(_round_coordinate(data))'),
    ('class LostFoundPostSerializer(serializers.ModelSerializer):\n    publisher = UserSerializer(read_only=True)\n    latitude = CoordinateField()\n    longitude = CoordinateField()\n    contact_phone_display = serializers.SerializerMethodField()',
     'class LostFoundPostSerializer(serializers.ModelSerializer):\n    """\n    功能：报失寻主序列化器。\n    字段：publisher 只读；latitude/longitude 自动精度；contact_phone_display 脱敏。\n    【权限】visitor 读脱敏；user 读本人/发布者；admin 读完整\n    """\n    publisher = UserSerializer(read_only=True)\n    latitude = CoordinateField()\n    longitude = CoordinateField()\n    contact_phone_display = serializers.SerializerMethodField()'),
    ('    def get_contact_phone_display(self, obj):\n        request = self.context.get(\'request\')\n        phone = obj.contact_phone\n        if not phone:\n            return None\n        if request and request.user.is_authenticated:\n            if request.user == obj.publisher:\n                return phone\n            if getattr(request.user.profile, \'role\', None) == \'admin\':\n                return phone\n        phone_str = str(phone).strip()\n        if len(phone_str) >= 7:\n            return phone_str[:3] + \'****\' + phone_str[-4:]\n        return phone_str[:3] + \'****\'',
     '    def get_contact_phone_display(self, obj):\n        """\n        功能：电话脱敏逻辑（本人或 admin 可见完整，其余 138****1234）。\n        【权限】publisher/admin 完整；visitor/user 脱敏\n        """\n        request = self.context.get(\'request\')\n        phone = obj.contact_phone\n        if not phone:\n            return None\n        if request and request.user.is_authenticated:\n            if request.user == obj.publisher:\n                return phone\n            if getattr(request.user.profile, \'role\', None) == \'admin\':\n                return phone\n        phone_str = str(phone).strip()\n        if len(phone_str) >= 7:\n            return phone_str[:3] + \'****\' + phone_str[-4:]\n        return phone_str[:3] + \'****\''),
    ('    def validate_photo_urls(self, value):\n        if not value or not isinstance(value, list) or len(value) < 1:\n            raise serializers.ValidationError(\'\u8bf7\u81f3\u5c11\u4e0a\u4f20 1 \u5f20\u5ba0\u7269\u7167\u7247\')\n        return value',
     '    def validate_photo_urls(self, value):\n        """\n        功能：至少上传 1 张照片。\n        """\n        if not value or not isinstance(value, list) or len(value) < 1:\n            raise serializers.ValidationError(\'\u8bf7\u81f3\u5c11\u4e0a\u4f20 1 \u5f20\u5ba0\u7269\u7167\u7247\')\n        return value'),
])

patch("lostfound/views.py", [
    ('"""\n妯″潡璇存槑锛歭ostfound 妯″潡 API 瑙嗗浘銆?1?7\n"""',
     '"""\nlostfound 视图：报失寻主 CRUD + 附近搜索（Haversine 算法）。\n"""\n'),
    ('def _haversine_distance(lat1, lon1, lat2, lon2):\n    """Haversine 閸忣剙绱＄拋锛勭暬娑撱倗鍋ｉ梻纾嬬獩缁備紮绱欓崗顒勫櫡閿涳拷"""\n    R = 6371',
     'def _haversine_distance(lat1, lon1, lat2, lon2):\n    """\n    功能：Haversine 公式计算两点球面距离（单位 km）。\n    用于附近搜索。\n    """\n    R = 6371'),
    ('class LostFoundPostViewSet(viewsets.ModelViewSet):\n    """閹躲儱銇?1?7/鐎佃?冲瘎1?7 CRUD"""',
     'class LostFoundPostViewSet(viewsets.ModelViewSet):\n    """\n    功能：报失寻主 CRUD + my_posts + nearby。\n    【权限】list/retrieve/nearby：visitor；其余：user（未封禁）；更新本人或 admin\n    """'),
    ("        if self.action in ['list', 'retrieve', 'nearby']:\n            return [permissions.AllowAny()]\n        return [permissions.IsAuthenticated(), IsActiveUser()]",
     "        # 分支：list/retrieve/nearby 公开；create/update/delete 需要登录+未封禁\n        if self.action in ['list', 'retrieve', 'nearby']:\n            return [permissions.AllowAny()]\n        return [permissions.IsAuthenticated(), IsActiveUser()]"),
    ('    def perform_create(self, serializer):\n        lat = serializer.validated_data.get(\'latitude\')\n        lon = serializer.validated_data.get(\'longitude\')\n        address_text = serializer.validated_data.get(\'address_text\', \'\')\n        # 閺堝?婃綏閺嶅洣绲鹃弮鐘叉勾閸р偓閺冭?圭礉閼奉亜濮╅柅鍡楁勾閻炲棛绱?閻?锟?1?7\n        if lat is not None and lon is not None and not address_text:\n            try:\n                import requests\n                headers = {\'User-Agent\': \'PetConnectWeb/1.0 (pet-connect-app)\'}\n                url = f\'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=zh\'\n                resp = requests.get(url, headers=headers, timeout=5)\n                if resp.status_code == 200:\n                    data = resp.json()\n                    display_name = data.get(\'display_name\', \'\')\n                    if display_name:\n                        serializer.validated_data[\'address_text\'] = display_name\n            except Exception:\n                pass\n        serializer.save(publisher=self.request.user)',
     '    def perform_create(self, serializer):\n        """\n        功能：创建时若有坐标无地址，调用 Nominatim 反向地理编码自动填充 address_text。\n        【权限】user\n        """\n        lat = serializer.validated_data.get(\'latitude\')\n        lon = serializer.validated_data.get(\'longitude\')\n        address_text = serializer.validated_data.get(\'address_text\', \'\')\n        # 若有经纬度但无地址文本，尝试反向地理编码\n        if lat is not None and lon is not None and not address_text:\n            try:\n                import requests\n                headers = {\'User-Agent\': \'PetConnectWeb/1.0 (pet-connect-app)\'}\n                url = f\'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=zh\'\n                resp = requests.get(url, headers=headers, timeout=5)\n                if resp.status_code == 200:\n                    data = resp.json()\n                    display_name = data.get(\'display_name\', \'\')\n                    if display_name:\n                        serializer.validated_data[\'address_text\'] = display_name\n            except Exception:\n                pass\n        serializer.save(publisher=self.request.user)'),
    ('    def perform_update(self, serializer):\n        instance = self.get_object()\n        if instance.publisher != self.request.user and getattr(self.request.user.profile, \'role\', None) != \'admin\':\n            raise PermissionDenied(\'Not allowed to update this post\')\n        serializer.save()',
     '    def perform_update(self, serializer):\n        """\n        功能：更新权限校验（仅发布者或 admin）。\n        【权限】publisher 或 admin\n        """\n        instance = self.get_object()\n        if instance.publisher != self.request.user and getattr(self.request.user.profile, \'role\', None) != \'admin\':\n            raise PermissionDenied(\'Not allowed to update this post\')\n        serializer.save()'),
    ('    @action(detail=False, methods=[\'get\'])\n    def my_posts(self, request):\n        """瑜版挸澧犻悽銊﹀煕閻ㄥ嫬褰傜敮鍐?顔囪ぐ锟?"""\n        qs = self.get_queryset().filter(publisher=request.user)\n        serializer = self.get_serializer(qs, many=True)\n        return Response(serializer.data)',
     '    @action(detail=False, methods=[\'get\'])\n    def my_posts(self, request):\n        """\n        功能：我的发布列表。\n        【权限】user（本人）\n        """\n        qs = self.get_queryset().filter(publisher=request.user)\n        serializer = self.get_serializer(qs, many=True)\n        return Response(serializer.data)'),
    ('    @action(detail=False, methods=[\'get\'], url_path=\'nearby\')\n    def nearby(self, request):\n        """闂勫嫯绻庨幖婊呭偍閿涙碍鐗撮幑顔剧病缁绢剙瀹抽弻銉﹀?橀幐鍥х暰閼煎啫娲块崘鍛?娈戠拋鏉跨秿"""\n        try:\n            lat = float(request.query_params.get(\'lat\', 0))\n            lon = float(request.query_params.get(\'lon\', 0))\n            radius_km = float(request.query_params.get(\'radius\', 5))\n        except (TypeError, ValueError):\n            return Response(\n                {\'detail\': \'鐠囬攱褰佹笟娑欐箒閺佸牏娈戠紒蹇曞惈鎼达箑寮?閺佸府绱檒at, lon閿涳拷\'},\n                status=status.HTTP_400_BAD_REQUEST,\n            )\n        if not lat or not lon:\n            return Response(\n                {\'detail\': \'鐠囬攱褰佹笟娑氱病缁绢剙瀹抽崣鍌涙殶\'},\n                status=status.HTTP_400_BAD_REQUEST,\n            )',
     '    @action(detail=False, methods=[\'get\'], url_path=\'nearby\')\n    def nearby(self, request):\n        """\n        功能：附近搜索（Haversine 半径过滤 + 距离排序）。\n        参数：lat, lon, radius（默认 5km），post_type, status\n        【权限】visitor\n        """\n        try:\n            lat = float(request.query_params.get(\'lat\', 0))\n            lon = float(request.query_params.get(\'lon\', 0))\n            radius_km = float(request.query_params.get(\'radius\', 5))\n        except (TypeError, ValueError):\n            return Response(\n                {\'detail\': \'鐠囬攱褰佹笟娑欐箒閺佸牏娈戠紒蹇曞惈鎼达箑寮?閺佸府绱檒at, lon閿涳拷\'},\n                status=status.HTTP_400_BAD_REQUEST,\n            )\n        if not lat or not lon:\n            return Response(\n                {\'detail\': \'鐠囬攱褰佹笟娑氱病缁绢剙瀹抽崣鍌涙殶\'},\n                status=status.HTTP_400_BAD_REQUEST,\n            )'),
])

print("done")