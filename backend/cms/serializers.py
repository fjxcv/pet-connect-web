"""
cms 序列化器：分类、文章、收藏序列化（含作者、分类名、是否收藏）。
"""

from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import ArticleFavorite, CmsArticle, CmsCategory


class CmsCategorySerializer(serializers.ModelSerializer):
    """分类序列化器。【权限】admin 写，visitor 读"""
    class Meta:
        model = CmsCategory
        fields = '__all__'


class CmsArticleSerializer(serializers.ModelSerializer):
    """
    文章序列化器。
    字段：author（只读）、category_name（只读）、is_favorited（当前用户是否收藏）。
    【权限】visitor 读公开；user 可收藏
    """
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = CmsArticle
        fields = '__all__'

    def get_is_favorited(self, obj):
        """
        功能：判断当前登录用户是否已收藏该文章。
        返回：bool
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ArticleFavorite.objects.filter(article=obj, user=request.user).exists()
        return False


class ArticleFavoriteItemSerializer(serializers.ModelSerializer):
    """我的收藏列表项（嵌套文章详情）。【权限】user 本人"""
    article = CmsArticleSerializer(read_only=True)

    class Meta:
        model = ArticleFavorite
        fields = ['id', 'created_at', 'article']
