"""
模块说明：演示数据种子脚本（答辩不重点讲解）。
"""

from decimal import Decimal

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand

from django.utils import timezone

from accounts.models import UserProfile

from cms.models import ArticleFavorite, CmsArticle, CmsCategory

from community.models import (

    CommentLike,

    CommunityComment,

    CommunityPost,

    PostFavorite,

    PostLike,

)

from lostfound.models import LostFoundPost

from pets.models import AdoptApplication, PetProfile

from portal.models import PortalCarousel

from rescue.models import RescueCase, RescueStageRecord, RescueStatusLog

from system.models import PlatformConfig



class Command(BaseCommand):

    help = 'Seed demo data for PawRescue platform (Chinese)'

    def handle(self, *args, **options):

        admin, _ = User.objects.update_or_create(

            username='admin',

            defaults={'email': 'admin@petrescue.local', 'is_staff': True, 'is_superuser': True},

        )

        admin.set_password('admin12345')

        admin.save()

        UserProfile.objects.filter(user=admin).update(role='admin')

        user, _ = User.objects.update_or_create(

            username='demo',

            defaults={'email': 'demo@petrescue.local'},

        )

        user.set_password('demo12345')

        user.save()

        UserProfile.objects.filter(user=user).update(has_privacy_consent=True)

        PlatformConfig.objects.get_or_create(

            config_key='max_upload_mb',

            defaults={'config_value': '10', 'description': '\u6700\u5927\u4e0a\u4f20\u6587\u4ef6\u5927\u5c0f\uff08MB\uff09'},

        )

        PlatformConfig.objects.get_or_create(

            config_key='ai_daily_limit',

            defaults={

                'config_value': '200',

                'description': '\u5e73\u53f0\u6bcf\u65e5 AI \u8c03\u7528\u4e0a\u9650\uff0c0 \u8868\u793a\u4e0d\u9650\u5236',

            },

        )

        PlatformConfig.objects.get_or_create(

            config_key='ai_total_limit',

            defaults={

                'config_value': '10000',

                'description': '\u5e73\u53f0 AI \u7d2f\u8ba1\u8c03\u7528\u4e0a\u9650\uff0c0 \u8868\u793a\u4e0d\u9650\u5236',

            },

        )

        PortalCarousel.objects.update_or_create(

            title='\u6b22\u8fce\u9886\u517b',

            defaults={

                'image_url': 'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=800',

                'link_url': '/pets',

                'sort_order': 1,

            },

        )

        category, _ = CmsCategory.objects.get_or_create(

            name='\u79d1\u666e',

            defaults={'sort_order': 1},

        )

        CmsArticle.objects.update_or_create(

            article_type='science',

            title='\u6d41\u6d6a\u732b\u72d7\u79d1\u666e\u77e5\u8bc6',

            defaults={

                'category': category,

                'author': admin,

                'summary': '\u517b\u5ba0\u524d\u5fc5\u770b\u7684\u79d1\u666e\u77e5\u8bc6',

                'content': '\u8bf7\u5728\u9886\u517b\u524d\u505a\u597d\u5fc3\u7406\u51c6\u5907\u4e0e\u8d23\u4efb\u8bc4\u4f30\u3002\u9886\u517b\u4e0d\u4ec5\u4ec5\u662f\u5e26\u56de\u5bb6\u91cc\u4e00\u53ea\u5ba0\u7269\uff0c\u66f4\u662f\u4e00\u4efd\u957f\u8fbe\u5341\u4f59\u5e74\u7684\u627f\u8bfa\u3002',

                'status': 1,

                'published_at': timezone.now(),

            },

        )

        announcement_category, _ = CmsCategory.objects.get_or_create(

            name='\u516c\u544a',

            defaults={'sort_order': 2},

        )

        CmsArticle.objects.update_or_create(

            article_type='announcement',

            title='\u6696\u722a\u6551\u52a9\u5e73\u53f0\u6b63\u5f0f\u4e0a\u7ebf',

            defaults={

                'category': announcement_category,

                'author': admin,

                'summary': '\u6b22\u8fce\u52a0\u5165\u6d41\u6d6a\u5ba0\u7269\u7efc\u5408\u6551\u52a9\u7ba1\u7406\u5e73\u53f0',

                'content': '\u5e73\u53f0\u5df2\u5f00\u653e\u9886\u517b\u3001\u62a5\u5931\u5bfb\u4e3b\u3001\u6551\u52a9\u8ffd\u8e2a\u4e0e\u793e\u533a\u4ea4\u6d41\u7b49\u529f\u80fd\uff0c\u6b22\u8fce\u7231\u5fc3\u4eba\u58eb\u53c2\u4e0e\u3002',

                'is_pinned': True,

                'status': 1,

                'published_at': timezone.now(),

            },

        )

        CmsArticle.objects.update_or_create(

            article_type='announcement',

            title='\u6625\u5b63\u9886\u517b\u65e5\u6d3b\u52a8\u9884\u544a',

            defaults={

                'category': announcement_category,

                'author': admin,

                'summary': '\u672c\u5468\u672b\u5c06\u4e3e\u529e\u7ebf\u4e0b\u9886\u517b\u89c1\u9762\u4f1a',

                'content': '\u5c65\u65f6\u5c06\u6709 20+ \u53ea\u5f85\u9886\u517b\u5ba0\u7269\u5230\u573a\uff0c\u6b22\u8fce\u6709\u610f\u5411\u7684\u9886\u517b\u4eba\u63d0\u524d\u9884\u7ea6\u53c2\u89c2\u3002',

                'is_pinned': False,

                'status': 1,

                'published_at': timezone.now(),

            },

        )

        rescue1, _ = RescueCase.objects.update_or_create(

            rescue_no='RC20260601001',

            defaults={

                'reporter': user,

                'discover_latitude': Decimal('30.572800'),

                'discover_longitude': Decimal('104.066800'),

                'discover_address': '\u6210\u90fd\u5e02\u9526\u6c5f\u533a\u4e1c\u5927\u8857',

                'appearance': '\u6a58\u8272\u77ed\u6bdb\uff0c\u5706\u8138\uff0c\u4f53\u578b\u4e2d\u7b49',

                'health_note': '\u5df2\u505a\u57fa\u7840\u68c0\u67e5\uff0c\u8f7b\u5fae\u8033\u8815',

                'current_status': 'awaiting_adoption',

            },

        )

        rescue2, _ = RescueCase.objects.update_or_create(

            rescue_no='RC20260601002',

            defaults={

                'reporter': user,

                'discover_latitude': Decimal('30.660000'),

                'discover_longitude': Decimal('104.063000'),

                'discover_address': '\u6210\u90fd\u5e02\u6b66\u4faf\u533a\u79d1\u534e\u5317\u8def',

                'appearance': '\u9ed1\u767d\u76f8\u95f4\u957f\u6bdb\uff0c\u84dd\u773c\u775b\uff0c\u4f53\u578b\u8f83\u5927',

                'health_note': '\u5df2\u9a71\u866b\u75ab\u82d7\uff0c\u8eab\u4f53\u5065\u5eb7',

                'current_status': 'rescued',

            },

        )

        rescue3, _ = RescueCase.objects.update_or_create(

            rescue_no='RC20260601003',

            defaults={

                'reporter': user,

                'discover_latitude': Decimal('30.550000'),

                'discover_longitude': Decimal('104.050000'),

                'discover_address': '\u6210\u90fd\u5e02\u6210\u534e\u533a\u5efa\u8bbe\u8def',

                'appearance': '\u7eaf\u767d\u8272\u77ed\u6bdb\uff0c\u4f53\u578b\u5a07\u5c0f',

                'health_note': '\u5df2\u7edd\u80b2\uff0c\u63a5\u79cd\u75ab\u82d7',

                'current_status': 'awaiting_adoption',

            },

        )

        rescue4, _ = RescueCase.objects.update_or_create(

            rescue_no='RC20260601004',

            defaults={

                'reporter': user,

                'discover_latitude': Decimal('30.580000'),

                'discover_longitude': Decimal('104.120000'),

                'discover_address': '\u6210\u90fd\u5e02\u91d1\u725b\u533a\u8336\u5e97\u5b50',

                'appearance': '\u8910\u8272\u77ed\u6bdb\uff0c\u7acb\u8033\uff0c\u4f53\u683c\u5065\u58ee',

                'health_note': '\u5df2\u63a5\u79cd\u72c2\u72ac\u75ab\u82d7\uff0c\u5df2\u9a71\u866b',

                'current_status': 'awaiting_adoption',

            },

        )

        RescueCase.objects.update_or_create(

            rescue_no='RC20260601005',

            defaults={

                'reporter': user,

                'discover_latitude': Decimal('30.620000'),

                'discover_longitude': Decimal('104.080000'),

                'discover_address': '\u6210\u90fd\u5e02\u9526\u6c5f\u533a\u6625\u7199\u8def\u9644\u8fd1',

                'appearance': '\u4e09\u82b1\u957f\u6bdb\u732b\uff0c\u4f53\u578b\u504f\u7626',

                'health_note': '\u5df2\u5eb7\u590d\uff0c\u53ef\u9886\u517b',

                'current_status': 'rescued',

            },

        )

        RescueCase.objects.update_or_create(

            rescue_no='RC20260623001',

            defaults={

                'reporter': user,

                'discover_latitude': Decimal('30.570000'),

                'discover_longitude': Decimal('104.060000'),

                'discover_address': '\u6210\u90fd\u5e02\u6b66\u4faf\u533a\u79d1\u534e\u5317\u8def',

                'appearance': '\u9ed1\u8272\u4e2d\u578b\u72ac\uff0c\u5de6\u8033\u6709\u7f3a\u53e3',

                'health_note': '\u4eca\u65e5\u4e0a\u62a5\uff0c\u5f85\u8fdb\u4e00\u6b65\u68c0\u67e5',

                'current_status': 'rescued',

                'created_at': timezone.now(),

            },

        )

        AdoptApplication.objects.all().delete()

        PetProfile.objects.all().delete()

        PetProfile.objects.create(

            rescue_case=rescue1,

            name='\u5c0f\u6a58',

            species='cat',

            breed='\u4e2d\u534e\u7530\u56ed\u732b',

            age_months=8,

            gender='male',

            size_category='small',

            health_status='\u5df2\u9a71\u866b\u75ab\u82d7\uff0c\u5df2\u7edd\u80b2',

            description='\u6027\u683c\u6e29\u987a\u7c98\u4eba\uff0c\u559c\u6b22\u8e72\u817f\u6c42\u62b1\u62b1\uff0c\u9002\u5408\u6709\u7ecf\u9a8c\u7684\u5bb6\u5ead\u9886\u517b\u3002',

            photo_url='https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600',

            adoption_status='available',

        )

        PetProfile.objects.create(

            rescue_case=rescue2,

            name='\u96ea\u7403',

            species='cat',

            breed='\u5e03\u5076\u732b',

            age_months=24,

            gender='female',

            size_category='small',

            health_status='\u5df2\u63a5\u79cd\u75ab\u82d7\uff0c\u5b9a\u671f\u4f53\u68c0',

            description='\u989c\u503c\u8d85\u9ad8\uff0c\u6027\u683c\u5b89\u9759\u4f18\u96c5\uff0c\u84dd\u773c\u775b\u7279\u522b\u8ff7\u4eba\u3002',

            photo_url='https://images.unsplash.com/photo-1574158622682-e40e69881006?w=600',

            adoption_status='available',

        )

        PetProfile.objects.create(

            rescue_case=rescue3,

            name='\u5c0f\u767d',

            species='dog',

            breed='\u6bd4\u718a\u72d7',

            age_months=12,

            gender='female',

            size_category='small',

            health_status='\u5df2\u7edd\u80b2\uff0c\u5df2\u63a5\u79cd\u75ab\u82d7',

            description='\u6d3b\u6cfc\u597d\u52a8\uff0c\u7279\u522b\u4eb2\u4eba\uff0c\u559c\u6b22\u51fa\u53bb\u901b\u5f2f\u3002',

            photo_url='https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600',

            adoption_status='available',

        )

        PetProfile.objects.create(

            rescue_case=rescue4,

            name='\u65fa\u8d22',

            species='dog',

            breed='\u4e2d\u534e\u7530\u56ed\u72ac',

            age_months=36,

            gender='male',

            size_category='medium',

            health_status='\u5df2\u63a5\u79cd\u72c2\u72ac\u75ab\u82d7\uff0c\u5df2\u9a71\u866b',

            description='\u975e\u5e38\u5fe0\u8bda\uff0c\u770b\u5bb6\u62a4\u9662\u7684\u4e00\u628a\u597d\u624b\uff0c\u5bf9\u4e3b\u4eba\u6781\u4e3a\u4f9d\u604b\u3002',

            photo_url='https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600',

            adoption_status='available',

        )

        PetProfile.objects.create(

            rescue_case=None,

            name='\u8c46\u8c46',

            species='rabbit',

            breed='\u8377\u5170\u5782\u8033\u5154',

            age_months=6,

            gender='female',

            size_category='small',

            health_status='\u5065\u5eb7\u6d3b\u6cfc\uff0c\u5df2\u505a\u4f53\u68c0',

            description='\u8d85\u840c\u5782\u8033\u5154\uff0c\u7231\u5e72\u51c0\uff0c\u4f1a\u7528\u5154\u5395\u6240\u3002',

            photo_url='https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=600',

            adoption_status='available',

        )

        PetProfile.objects.create(

            rescue_case=None,

            name='\u963f\u798f',

            species='dog',

            breed='\u91d1\u6bdb\u5bfb\u56de\u72ac',

            age_months=18,

            gender='male',

            size_category='large',

            health_status='\u5df2\u7edd\u80b2\uff0c\u63a5\u79cd\u5168\u90e8\u75ab\u82d7',

            description='\u6027\u683c\u9633\u5149\u5f00\u6717\uff0c\u975e\u5e38\u806a\u660e\uff0c\u4f1a\u5750\u4e0b\u3001\u63e1\u624b\u7b49\u57fa\u672c\u6307\u4ee4\u3002',

            photo_url='https://images.unsplash.com/photo-1552053831-71594a27632d?w=600',

            adoption_status='available',

        )

        PetProfile.objects.create(

            rescue_case=None,

            name='\u56e2\u56e2',

            species='cat',

            breed='\u6a58\u732b',

            age_months=30,

            gender='female',

            size_category='small',

            health_status='\u5df2\u7edd\u80b2\uff0c\u8eab\u4f53\u5065\u5eb7',

            description='\u5df2\u4e8e\u53bb\u5e74\u88ab\u7231\u5fc3\u5bb6\u5ead\u9886\u517b\uff0c\u76ee\u524d\u751f\u6d3b\u5e78\u798f\u3002',

            photo_url='https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=600',

            adoption_status='adopted',

            is_public=False,

        )

        PetProfile.objects.create(

            rescue_case=None,

            name='\u5927\u9ec4',

            species='dog',

            breed='\u4e2d\u534e\u7530\u56ed\u72ac',

            age_months=48,

            gender='male',

            size_category='medium',

            health_status='\u5df2\u7edd\u80b2\uff0c\u5b9a\u671f\u4f53\u68c0',

            description='\u5fe0\u8bda\u62a4\u4e3b\uff0c\u5df2\u6210\u529f\u9886\u517b\u81f3\u90ca\u533a\u5c0f\u9662\u3002',

            photo_url='https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600',

            adoption_status='adopted',

            is_public=False,

        )

        PetProfile.objects.create(

            rescue_case=None,

            name='\u5495\u5495',

            species='cat',

            breed='\u72f8\u82b1\u732b',

            age_months=20,

            gender='female',

            size_category='small',

            health_status='\u5df2\u63a5\u79cd\u75ab\u82d7',

            description='\u6027\u683c\u72ec\u7acb\uff0c\u5df2\u88ab\u5927\u5b66\u751f\u9886\u517b\u3002',

            photo_url='https://images.unsplash.com/photo-1529773473-3f2e4d392ae8?w=600',

            adoption_status='adopted',

            is_public=False,

        )

        LostFoundPost.objects.update_or_create(

            publisher=user,

            post_type='lost',

            pet_species='\u732b',

            address_text='\u6210\u90fd\u5e02\u9ad8\u65b0\u533a\u5929\u5e9c\u8f6f\u4ef6\u56ed\u9644\u8fd1',

            defaults={

                'features': '\u68a8\u82b1\u8272\u3001\u7eff\u773c\u775b\u3001\u6234\u7ea2\u8272\u9879\u5708',

                'latitude': Decimal('30.600000'),

                'longitude': Decimal('104.100000'),

                'reward_amount': Decimal('500.00'),

                'contact_phone': '13800000000',

                'status': 'searching',

            },

        )

        LostFoundPost.objects.update_or_create(

            publisher=user,

            post_type='found',

            pet_species='\u6cf0\u8fea\u72ac',

            address_text='\u6210\u90fd\u5e02\u6b66\u4faf\u533a\u7389\u6797\u751f\u6d3b\u5e7f\u573a',

            defaults={

                'features': '\u68d5\u8272\u5377\u6bdb\u3001\u4f53\u578b\u8f83\u5c0f\u3001\u6234\u84dd\u8272\u9879\u5708',

                'latitude': Decimal('30.630000'),

                'longitude': Decimal('104.050000'),

                'reward_amount': Decimal('0'),

                'contact_phone': '13800000001',

                'status': 'searching',

            },

        )

        LostFoundPost.objects.update_or_create(

            publisher=user,

            post_type='lost',

            pet_species='\u67ef\u57fa\u72ac',

            address_text='\u6210\u90fd\u5e02\u9752\u7f8a\u533a\u5bbd\u7a84\u5df7\u5b50',

            defaults={

                'features': '\u9ec4\u767d\u53cc\u8272\u3001\u77ed\u817f\u3001\u8d70\u5931\u65f6\u7a7f\u7ea2\u8272\u8863\u670d',

                'latitude': Decimal('30.670000'),

                'longitude': Decimal('104.050000'),

                'reward_amount': Decimal('800.00'),

                'contact_phone': '13800000002',

                'status': 'searching',

            },

        )

        CommunityPost.objects.update_or_create(

            author=user,

            title='\u5206\u4eab\u4e00\u6b21\u6551\u52a9\u7ecf\u5386',

            defaults={

                'category': 'rescue_share',

                'content': '\u611f\u8c22\u6240\u6709\u5fd7\u613f\u8005\u7684\u5e2e\u52a9\uff01\u6628\u5929\u5728\u8def\u8fb9\u53d1\u73b0\u4e00\u53ea\u53d7\u4f24\u7684\u5c0f\u732b\uff0c\u5927\u5bb6\u4e00\u8d77\u628a\u5b83\u9001\u5230\u4e86\u5ba0\u7269\u533b\u9662\uff0c\u73b0\u5728\u5df2\u7ecf\u8131\u79bb\u4e86\u5371\u9669\u3002',

            },

        )

        post = CommunityPost.objects.filter(author=user).first()

        if post:

            PostFavorite.objects.get_or_create(post=post, user=user)

        article = CmsArticle.objects.filter(status=1).first()

        if article:

            ArticleFavorite.objects.get_or_create(article=article, user=user)

        # ====================== \u793e\u533a\u5e16\u5b50\u5b8c\u6574\u6f14\u793a\u6570\u636e ======================

        post1, _ = CommunityPost.objects.update_or_create(

            author=user,

            title='\u96e8\u591c\u62fe\u5230\u53d7\u4f24\u5c0f\u72f8\u82b1\u732b\uff0c\u6551\u52a9\u5168\u8fc7\u7a0b\u5206\u4eab',

            defaults={

                'category': 'rescue_share',

                'content': '\u6628\u665a\u4e0b\u5927\u96e8\u8def\u8fb9\u53d1\u73b0\u4e00\u53ea\u540e\u817f\u53d7\u4f24\u7684\u5c0f\u72f8\u82b1\u732b\uff0c\u6d78\u6e7f\u53d1\u6296\u4e0d\u6562\u9760\u8fd1\u4eba\u3002\u4e70\u4e86\u7f50\u5934\u5f15\u8bf1\u540e\u5e26\u53bb\u5ba0\u7269\u533b\u9662\uff0c\u62cd\u7247\u53d1\u73b0\u8f7b\u5fae\u9aa8\u88c2\uff0c\u76ee\u524d\u4f4f\u9662\u89c2\u5bdf\uff0c\u5e0c\u671b\u5b83\u65e9\u65e5\u5eb7\u590d\uff0c\u627e\u5230\u613f\u610f\u8d1f\u8d23\u7684\u9886\u517b\u4eba\u3002',

                'image_urls': ['/media/gallery/darcat.jpg'],

            },

        )

        PostLike.objects.get_or_create(post=post1, user=admin)

        c1, _ = CommunityComment.objects.get_or_create(

            post=post1,

            author=admin,

            parent=None,

            content='\u592a\u6709\u7231\u5fc3\u4e86\uff01\u5c0f\u732b\u6062\u590d\u540e\u53ef\u4ee5\u53d1\u5e73\u53f0\u9886\u517b\u677f\u5757\uff0c\u6211\u5e2e\u5fd9\u8f6c\u53d1\u3002',

        )

        CommunityComment.objects.get_or_create(

            post=post1,

            author=user,

            parent=c1,

            content='\u611f\u8c22\u7ba1\u7406\u5458\uff0c\u7b49\u5c0f\u732b\u75ca\u6108\u4f1a\u4e0a\u4f20\u5b8c\u6574\u6863\u6848\u7533\u8bf7\u9886\u517b\u3002',

        )

        post2, _ = CommunityPost.objects.update_or_create(

            author=user,

            title='\u79df\u623f\u53ef\u4ee5\u9886\u517b\u732b\u732b\u5417\uff1f\u9700\u8981\u6ce8\u610f\u4ec0\u4e48\uff1f',

            defaults={

                'category': 'help_request',

                'content': '\u76ee\u524d\u72ec\u5c45\u4e00\u5ba4\u4e00\u5385\uff0c\u623f\u4e1c\u5141\u8bb8\u517b\u5c0f\u578b\u5ba0\u7269\uff0c\u60f3\u9886\u517b\u4e00\u53ea\u4e2d\u534e\u7530\u56ed\u72ac\uff0c\u60f3\u95ee\u5e73\u53f0\u9886\u517b\u5ba1\u6838\u4f1a\u770b\u79df\u623f\u5408\u540c\u5417\uff1f\u5e7c\u72ac\u548c\u6210\u72ac\u54ea\u4e2a\u66f4\u9002\u5408\u79df\u623f\u515a\uff1f',

            },

        )

        PostFavorite.objects.get_or_create(post=post2, user=user)

        PostLike.objects.get_or_create(post=post2, user=admin)

        CommunityComment.objects.get_or_create(

            post=post2,

            author=admin,

            parent=None,

            content='\u9886\u517b\u5ba1\u6838\u4f1a\u7b80\u5355\u6838\u5b9e\u5c45\u4f4f\u73af\u5883\uff0c\u5c0f\u578b\u6210\u5e74\u72ac\u66f4\u9002\u5408\u79df\u623f\uff0c\u5e7c\u72ac\u62c6\u5bb6\u5435\u95f9\u4f1a\u5f71\u54cd\u90bb\u5c45\u3002',

        )

        post3, _ = CommunityPost.objects.update_or_create(

            author=user,

            title='\u6210\u534e\u533a\u5efa\u8bbe\u8def\u8d70\u5931\u4e09\u82b1\u6bcd\u732b\uff0c\u91cd\u91d1\u5bfb\u56de',

            defaults={

                'category': 'help_request',

                'content': '6\u670820\u65e5\u4e0b\u5348\u5728\u5efa\u8bbe\u8def\u5c0f\u533a\u8d70\u5931\u4e09\u82b1\u6bcd\u732b\uff0c\u5de6\u8033\u6709\u7f3a\u53e3\uff0c\u8116\u5b50\u6234\u7ea2\u8272\u94c3\u94db\u9879\u5708\uff0c\u60ac\u8d4f\u5fc5\u987b500\u5143\u73b0\u91d1\uff0c\u8054\u7cfb\u65b9\u5f0f13800000002\uff0c\u9ebb\u70e7\u9644\u8fd1\u5c45\u6c11\u5e2e\u5fd9\u7559\u610f\u3002',

            },

        )

        c3, _ = CommunityComment.objects.get_or_create(

            post=post3,

            author=admin,

            parent=None,

            content='\u5df2\u5e2e\u4f60\u8f6c\u53d1\u5e73\u53f0\u5bfb\u5ba0\u677f\u5757\uff0c\u5468\u8fb9\u5fd7\u613f\u8005\u4f1a\u5e2e\u7740\u7559\u610f\u3002',

        )

        CommunityComment.objects.get_or_create(

            post=post3,

            author=user,

            parent=c3,

            content='\u975e\u5e38\u611f\u8c22\u5e73\u53f0\u5e2e\u5fd9\u6269\u6563\uff01',

        )

        post4, _ = CommunityPost.objects.update_or_create(

            author=user,

            title='\u65b0\u624b\u517b\u732b\u5fc5\u770b\uff1a\u75ab\u82d7\u4e0e\u9a71\u866b\u5b8c\u6574\u65f6\u95f4\u8868',

            defaults={

                'category': 'pet_experience',

                'content': '\u5e7c\u732b8\u5468\u9f84\u9996\u6b21\u4f53\u5185\u5916\u9a71\u866b\uff0c9\u5468\u6253\u7b2c\u4e00\u9488\u732b\u4e09\u8054\uff0c\u95f4\u969421\u5929\u7b2c\u4e8c\u9488\uff0c12\u5468\u7b2c\u4e09\u9488+\u72ac\u4f20\u75ab\u82d7\uff1b\u6210\u5e74\u540e\u6bcf\u5e74\u4e00\u9488\u52a0\u5f3a\u75ab\u82d7\uff0c\u6bcf\u4e09\u4e2a\u6708\u4f53\u5185\u9a71\u866b\uff0c\u6bcf\u6708\u4f53\u5916\u9a71\u866b\u3002',

            },

        )

        PostFavorite.objects.get_or_create(post=post4, user=user)

        PostLike.objects.get_or_create(post=post4, user=admin)

        CommunityComment.objects.get_or_create(

            post=post4,

            author=admin,

            parent=None,

            content='\u5e72\u8d27\u6536\u85cf\u4e86\uff0c\u51c6\u5907\u9886\u517b\u5c0f\u732b\u6b63\u597d\u9700\u8981\u8fd9\u4efd\u65f6\u95f4\u8868\u3002',

        )

        post5, _ = CommunityPost.objects.update_or_create(

            author=user,

            title='\u5c0f\u72d7\u81ea\u5236\u9c9c\u98df\u914d\u6bd4\u7701\u4e00\u534a\u4ff1\u4e50\u8d39\uff0c\u6bdb\u53d1\u8089\u773c\u53d1\u4eae',

            defaults={

                'category': 'pet_experience',

                'content': (

                    '\u8e29\u5751\u65e0\u6570\u540e\u6574\u7406\u7684\u6210\u5e74\u72d7\u7c7b\u901a\u7528\u9c9c\u98df\u914d\u6bd4\uff0c\u4eb2\u6d4b\u534a\u5e74\uff0c\u6bcf\u6708\u5582\u517b\u6210\u672c\u76f4\u63a5\u51cf\u534a\uff0c\u72d7\u5b9d\u6bdb\u53d1\u987a\u6ed1\u5206\u6bdb\uff01\n'

                    '\u98df\u6750\u91cd\u91cf\u5360\u6bd4\n'

                    '\u8089\u7c7b 50%\u3001\u78b3\u6c34 30%\u3001\u852c\u83dc 18%\u3001\u6cb9\u8102\u8865\u5145 2%\n'

                    '\u8089\u7c7b\u8f6e\u6362\u9e21\u80f8\u3001\u7626\u725b\u3001\u4e09\u6587\u9c7c\uff08\u6bcf\u5468 2 \u6b21\u6df1\u6d77\u9c7c\u662f\u4eae\u6bdb\u6838\u5fc3\uff09\n'

                    '\u4e3b\u98df\u9009\u7ea2\u85af\u3001\u7c97\u7cae\uff0c\u852c\u83dc\u897f\u5170\u82b1\u80e1\u841d\u535c\uff0c\u65e0\u4efb\u4f55\u8c03\u5473\u54c1\n'

                    '\u5236\u4f5c\uff1a\u5168\u90e8\u716e\u719f\u5207\u788e\u5206\u88c5\u51b7\u51bb\uff0c\u968f\u5403\u968f\u53d6\n'

                    '\u6210\u672c\u5bf9\u6bd4\uff1a\u4e4b\u524d\u72d7\u7cae\u6708\u82b1300+\uff0c\u81ea\u5236\u4ec5 140-160 \u5143\n'

                    '\u6ce8\u610f\uff1a\u5e7c\u72ac\u3001\u80be\u75c5 / \u80f0\u817a\u708e\u72ac\u7c7b\u9700\u8981\u8c03\u6574\u914d\u6bd4\uff0c\u4e0d\u80fd\u76f4\u63a5\u7167\u642c\uff0c\u6709\u54c1\u79cd\u4f53\u91cd\u6211\u53ef\u4ee5\u5e2e\u5fd9\u7b97\u7cbe\u51c6\u7528\u91cf\u3002'

                ),

                'image_urls': ['/media/pets/download_2.webp', '/media/pets/download_2.webp'],

            },

        )

        PostLike.objects.get_or_create(post=post5, user=admin)

        c5, _ = CommunityComment.objects.get_or_create(

            post=post5,

            author=admin,

            parent=None,

            content='\u5e72\u8d27\u4fdd\u5b58\uff01\u5bb6\u91cc\u6bcf\u6708\u72d7\u7cae\u5f00\u9500\u786e\u5b9e\u9ad8\uff0c\u4e0b\u5468\u5c31\u8bd5\u8bd5\u8fd9\u4e2a\u914d\u6bd4\u3002',

        )

        CommunityComment.objects.get_or_create(

            post=post5,

            author=user,

            parent=c5,

            content='\u53ef\u4ee5\u5148\u5c11\u91cf\u8bd5\u5403\u89c2\u5bdf\u4fbf\u4fbf\u72b6\u6001\uff0c\u4eae\u6bdb\u6548\u679c\u5f88\u660e\u663e\u54e6',

        )

        c5_reply2, _ = CommunityComment.objects.get_or_create(

            post=post5,

            author=admin,

            parent=c5,

            root=c5,

            defaults={

                'content': '\u60f3\u95ee\u4e00\u4e0b\u4f53\u578b\u8f83\u5c0f\u8089\u7c7b\u6bd4\u4f8b\u9700\u8981\u4e0b\u8c03\u5417\uff1f\u5b83\u7684\u80a0\u80c3\u6bd4\u8f83\u654f\u611f\u3002',

            },

        )

        CommentLike.objects.get_or_create(comment=c5_reply2, user=user)

        CommunityComment.objects.get_or_create(

            post=post5,

            author=user,

            parent=c5_reply2,

            root=c5,

            defaults={

                'content': '\u8089\u7c7b\u8c03\u523040%\uff0c\u78b3\u6c34\u589e\u52a05%\uff0c\u5c11\u6cb9\uff0c\u9e21\u80f8\u4e3a\u4e3b\u3002',

            },

        )

        PostFavorite.objects.get_or_create(post=post5, user=user)

        post6, _ = CommunityPost.objects.update_or_create(

            author=user,

            title='\u5c0f\u6237\u578b\u4e0a\u73ed\u65cf\u6c42\u72d7\u72d7\u63a8\u8350\uff01\u8981\u6389\u6bdb\u5c11\u3001\u8fd0\u52a8\u91cf\u5c0f\uff0c\u767d\u5929\u72ec\u81ea\u5728\u5bb6\u4e0d\u62c6\u5bb6',

            defaults={

                'category': 'general',

                'content': (

                    '\u5750\u6807\u5c0f\u6237\u578b\u516c\u5bd3\uff0c\u6bcf\u5929\u65e9\u4e5d\u665a\u516d\uff0c\u52a0\u73ed\u8fd8\u4f1a\u665a\u5f52\uff0c\u60f3\u517b\u4e00\u53ea\u5c0f\u578b\u966a\u4f34\u72ac\uff0c\u786c\u6027\u9700\u6c42\uff1a\n'

                    '\u6389\u6bdb\u6781\u5c11 / \u51e0\u4e4e\u4e0d\u6389\uff0c\u6d01\u9759\u515c\uff0c\u4e0d\u60f3\u5929\u5929\u5438\u6bdb\u7c98\u8863\u670d\uff1b\n'

                    '\u8fd0\u52a8\u91cf\u5f88\u4f4e\uff0c\u4e0d\u7528\u957f\u65f6\u95f4\u901b\u5f2f\uff0c\u9634\u96e8\u5929\u5728\u5bb6\u73a9\u5c31\u80fd\u6d88\u8017\u7cbe\u529b\uff1b\n'

                    '\u72ec\u5904\u7a33\u5b9a\uff0c\u767d\u5929\u72ec\u81ea\u5728\u5bb6\u4e0d\u4e71\u53eb\u3001\u4e0d\u62c6\u5bb6\uff0c\u4e0d\u6293\u4eba\uff1b\n'

                    '\u4f53\u578b\u5c0f\u5de7\uff0c\u4e0d\u5360\u7a7a\u95f4\uff0c\u516c\u5bd3\u597d\u5b89\u7f6e\u3002\n'

                    '\u76ee\u524d\u7ea0\u7ed3\u6cd5\u6597\u3001\u6bd4\u718a\u3001\u5df4\u54e5\u3001\u8ff7\u4f60\u96ea\u7eb3\u745e\uff0c\u60f3\u95ee\u95ee\u517b\u8fc7\u7684\u9886\u517b\u5b98\u771f\u5b9e\u4f53\u9a8c'

                ),

            },

        )

        c6, _ = CommunityComment.objects.get_or_create(

            post=post6,

            author=admin,

            parent=None,

            content='\u8ff7\u4f60\u96ea\u7eb3\u745e\u6700\u8d34\u5408\u4f60\u7684\u9700\u6c42\uff0c\u5355\u5c42\u88ab\u6bdb\u51e0\u4e4e\u4e0d\u6389\u6bdb\uff0c\u6027\u683c\u5b89\u9759\u8010\u72ec\u5904\uff1b\u5df4\u54e5\u547c\u5438\u9053\u5f31\u8fd0\u52a8\u91cf\u4e0d\u80fd\u591a\uff0c\u6cf0\u8fea\u5bb9\u6613\u7126\u8651\u62c6\u5bb6\uff0c\u53ef\u4ee5\u4f18\u5148\u8003\u8651\u96ea\u7eb3\u745e\u3002',

        )

        CommunityComment.objects.get_or_create(

            post=post6,

            author=user,

            parent=c6,

            content='\u611f\u8c22\u5efa\u8bae\uff01\u4e4b\u524d\u62c5\u5fc3\u96ea\u7eb3\u745e\u8138\u6c14\u503c\uff0c\u8fd9\u4e0b\u6709\u53c2\u8003\u65b9\u5411\u4e86\uff0c\u6253\u7b97\u5e73\u53f0\u9886\u517b\u4e00\u53ea\u6210\u5e74\u96ea\u7eb3\u745e\u3002',

        )

        # ====================== 扩展全国演示数据（多用户/多地区/多模块） ======================

        user_specs = [

            ('alice_demo', 'alice_demo@petrescue.local', '\u5317\u4eac\u5e02'),

            ('bob_demo', 'bob_demo@petrescue.local', '\u4e0a\u6d77\u5e02'),

            ('charlie_demo', 'charlie_demo@petrescue.local', '\u5e7f\u4e1c\u7701'),

            ('diana_demo', 'diana_demo@petrescue.local', '\u6d59\u6c5f\u7701'),

            ('eva_demo', 'eva_demo@petrescue.local', '\u6e56\u5317\u7701'),

            ('frank_demo', 'frank_demo@petrescue.local', '\u9655\u897f\u7701'),

            ('grace_demo', 'grace_demo@petrescue.local', '\u5c71\u4e1c\u7701'),

            ('henry_demo', 'henry_demo@petrescue.local', '\u6cb3\u5357\u7701'),

            ('ivy_demo', 'ivy_demo@petrescue.local', '\u4e91\u5357\u7701'),

            ('jack_demo', 'jack_demo@petrescue.local', '\u798f\u5efa\u7701'),

        ]

        demo_users = []

        for username, email, province in user_specs:

            demo_u, _ = User.objects.update_or_create(username=username, defaults={'email': email})

            demo_u.set_password('demo12345')

            demo_u.save()

            UserProfile.objects.filter(user=demo_u).update(

                has_privacy_consent=True,

                nickname=f'{username}_\u7231\u5fc3\u5fd7\u613f\u8005',

                address=f'\u4e2d\u56fd{province}',

            )

            demo_users.append(demo_u)

        rescue_specs = [

            (

                'RC20260625011',

                demo_users[0],

                Decimal('39.904200'),

                Decimal('116.407400'),

                '\u5317\u4eac\u5e02\u671d\u9633\u533a\u4e09\u91cc\u5c6f\u8857\u9053',

                '\u68d5\u8272\u7530\u56ed\u72ac\uff0c\u53f3\u540e\u817f\u8f7b\u5fae\u53d7\u4f24',

                '\u5df2\u6e05\u521b\u6d88\u6bd2\uff0c\u5f85\u590d\u67e5',

                ['https://images.unsplash.com/photo-1517849845537-4d257902454a?w=800'],

                'in_medical',

            ),

            (

                'RC20260625012',

                demo_users[1],

                Decimal('31.230400'),

                Decimal('121.473700'),

                '\u4e0a\u6d77\u5e02\u9ec4\u6d66\u533a\u5357\u4eac\u4e1c\u8def',

                '\u94f6\u6e10\u5c42\u82f1\u77ed\u732b\uff0c\u6027\u683c\u80c6\u5c0f',

                '\u98df\u6b32\u6b63\u5e38\uff0c\u5df2\u5b8c\u6210\u4f53\u5185\u9a71\u866b',

                ['https://images.unsplash.com/photo-1511044568932-338cba0ad803?w=800'],

                'recovering',

            ),

            (

                'RC20260625013',

                demo_users[2],

                Decimal('23.129100'),

                Decimal('113.264400'),

                '\u5e7f\u5dde\u5e02\u5929\u6cb3\u533a\u4f53\u80b2\u4e1c\u8def',

                '\u9ed1\u767d\u5957\u88c5\u72ac\uff0c\u8033\u6735\u6709\u65e7\u4f24',

                '\u7cbe\u795e\u72b6\u6001\u826f\u597d\uff0c\u5df2\u9884\u7ea6\u7edd\u80b2',

                ['https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800'],

                'awaiting_adoption',

            ),

            (

                'RC20260625014',

                demo_users[3],

                Decimal('30.274100'),

                Decimal('120.155100'),

                '\u676d\u5dde\u5e02\u897f\u6e56\u533a\u6587\u4e09\u8def',

                '\u4e09\u82b1\u6bcd\u732b\uff0c\u4f53\u578b\u5a07\u5c0f',

                '\u672f\u540e\u6062\u590d\u826f\u597d\uff0c\u53ef\u8fdb\u5165\u9886\u517b\u6d41\u7a0b',

                ['https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=800'],

                'awaiting_adoption',

            ),

            (

                'RC20260625015',

                demo_users[4],

                Decimal('30.592800'),

                Decimal('114.305500'),

                '\u6b66\u6c49\u5e02\u6b66\u660c\u533a\u4e2d\u5317\u8def',

                '\u9ec4\u767d\u67ef\u57fa\uff0c\u816e\u90e8\u624b\u672f\u540e\u5eb7\u590d',

                '\u5df2\u63a5\u79cd\u5168\u5957\u75ab\u82d7',

                ['https://images.unsplash.com/photo-1561037404-61cd46aa615b?w=800'],

                'rescued',

            ),

        ]

        rescue_cases = []

        for rescue_no, reporter, lat, lon, address, appearance, health_note, photo_urls, status in rescue_specs:

            case, _ = RescueCase.objects.update_or_create(

                rescue_no=rescue_no,

                defaults={

                    'reporter': reporter,

                    'discover_latitude': lat,

                    'discover_longitude': lon,

                    'discover_address': address,

                    'appearance': appearance,

                    'health_note': health_note,

                    'photo_urls': photo_urls,

                    'current_status': status,

                },

            )

            rescue_cases.append(case)

        for case in rescue_cases:

            RescueStatusLog.objects.get_or_create(

                rescue_case=case,

                from_status='pending_rescue',

                to_status='in_medical',

                operator=case.reporter,

                remark='\u7b2c\u4e00\u6b65\uff1a\u5df2\u5b89\u5168\u8f6c\u8fd0\u81f3\u5408\u4f5c\u5ba0\u7269\u533b\u9662',

            )

            RescueStatusLog.objects.get_or_create(

                rescue_case=case,

                from_status='in_medical',

                to_status=case.current_status,

                operator=admin,

                remark='\u7b2c\u4e8c\u6b65\uff1a\u7efc\u5408\u8bc4\u4f30\u540e\u66f4\u65b0\u6551\u52a9\u9636\u6bb5',

            )

            RescueStageRecord.objects.get_or_create(

                rescue_case=case,

                operator=case.reporter,

                content='\u7ebf\u4e0a\u5efa\u6863\u5e76\u4e0a\u4f20\u73b0\u573a\u7167\u7247\uff0c\u786e\u8ba4\u6551\u52a9\u4efb\u52a1\u3002',

            )

            RescueStageRecord.objects.get_or_create(

                rescue_case=case,

                operator=admin,

                content='\u5b8c\u6210\u5065\u5eb7\u68c0\u67e5\uff0c\u8ffd\u52a0\u5fc3\u7406\u72b6\u6001\u8bc4\u4f30\u4e0e\u540e\u7eed\u8ffd\u8e2a\u8ba1\u5212\u3002',

            )

        pet_specs = [

            ('\u5317\u5317', 'dog', '\u67ef\u57fa', 14, 'female', 'small', rescue_cases[0], '\u4e2d\u56fd', '\u5317\u4eac\u5e02', '\u5317\u4eac\u5e02', '\u671d\u9633\u533a', Decimal('39.904200'), Decimal('116.407400'), 'https://images.unsplash.com/photo-1525253086316-d0c936c814f8?w=800'),

            ('\u6c64\u5706', 'cat', '\u82f1\u77ed', 10, 'male', 'small', rescue_cases[1], '\u4e2d\u56fd', '\u4e0a\u6d77\u5e02', '\u4e0a\u6d77\u5e02', '\u9ec4\u6d66\u533a', Decimal('31.230400'), Decimal('121.473700'), 'https://images.unsplash.com/photo-1472491235688-bdc81a63246e?w=800'),

            ('\u53ef\u4e50', 'dog', '\u67f4\u72ac', 20, 'male', 'medium', rescue_cases[2], '\u4e2d\u56fd', '\u5e7f\u4e1c\u7701', '\u5e7f\u5dde\u5e02', '\u5929\u6cb3\u533a', Decimal('23.129100'), Decimal('113.264400'), 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800'),

            ('\u7cd6\u7cd6', 'cat', '\u4e2d\u534e\u7530\u56ed\u732b', 6, 'female', 'small', rescue_cases[3], '\u4e2d\u56fd', '\u6d59\u6c5f\u7701', '\u676d\u5dde\u5e02', '\u897f\u6e56\u533a', Decimal('30.274100'), Decimal('120.155100'), 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800'),

            ('\u5c0f\u4e03', 'dog', '\u91d1\u6bdb', 26, 'male', 'large', rescue_cases[4], '\u4e2d\u56fd', '\u6e56\u5317\u7701', '\u6b66\u6c49\u5e02', '\u6b66\u660c\u533a', Decimal('30.592800'), Decimal('114.305500'), 'https://images.unsplash.com/photo-1552053831-71594a27632d?w=800'),

            ('\u7cd6\u8c46', 'cat', '\u5e03\u5076\u732b', 18, 'female', 'small', None, '\u4e2d\u56fd', '\u5c71\u4e1c\u7701', '\u9752\u5c9b\u5e02', '\u5d02\u5c71\u533a', Decimal('36.067100'), Decimal('120.382600'), 'https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=800'),

            ('\u5c0f\u8c46', 'dog', '\u6bd4\u718a', 9, 'male', 'small', None, '\u4e2d\u56fd', '\u798f\u5efa\u7701', '\u53a6\u95e8\u5e02', '\u601d\u660e\u533a', Decimal('24.479800'), Decimal('118.089400'), 'https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=800'),

            ('\u556a\u55d2', 'rabbit', '\u57cb\u7f57\u5154', 11, 'female', 'small', None, '\u4e2d\u56fd', '\u9655\u897f\u7701', '\u897f\u5b89\u5e02', '\u96c1\u5854\u533a', Decimal('34.341600'), Decimal('108.939800'), 'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=800'),

            ('\u660e\u660e', 'bird', '\u7384\u51e4', 16, 'unknown', 'small', None, '\u4e2d\u56fd', '\u6cb3\u5357\u7701', '\u90d1\u5dde\u5e02', '\u4e2d\u539f\u533a', Decimal('34.746600'), Decimal('113.625400'), 'https://images.unsplash.com/photo-1444464666168-49d633b86797?w=800'),

            ('\u9ed1\u59ae', 'cat', '\u66fc\u57fa\u5eb7', 15, 'female', 'small', None, '\u4e2d\u56fd', '\u4e91\u5357\u7701', '\u6606\u660e\u5e02', '\u4e94\u534e\u533a', Decimal('25.038900'), Decimal('102.718300'), 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=800'),

            ('\u5c0f\u72fc', 'dog', '\u4e2d\u534e\u7530\u56ed\u72ac', 30, 'male', 'medium', None, '\u4e2d\u56fd', '\u7518\u8083\u7701', '\u5170\u5dde\u5e02', '\u57ce\u5173\u533a', Decimal('36.061100'), Decimal('103.834300'), 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800'),

        ]

        extra_pets = []

        for (

            name, species, breed, age_months, gender, size_category, rescue_case,

            country, province, city, district, lat, lon, photo_url

        ) in pet_specs:

            pet, _ = PetProfile.objects.update_or_create(

                name=name,

                defaults={

                    'rescue_case': rescue_case,

                    'species': species,

                    'breed': breed,

                    'age_months': age_months,

                    'gender': gender,

                    'size_category': size_category,

                    'health_status': '\u5065\u5eb7\uff0c\u5df2\u5b8c\u6210\u57fa\u7840\u75ab\u82d7',

                    'description': f'{name}\u6027\u683c\u53cb\u597d\uff0c\u9002\u5408\u5bb6\u5ead\u7ec8\u8eab\u9886\u517b\u3002',

                    'photo_url': photo_url,

                    'country': country,

                    'province': province,

                    'city': city,

                    'district': district,

                    'location_text': f'{province}{city}{district}',

                    'latitude': lat,

                    'longitude': lon,

                    'adoption_status': 'available',

                    'is_public': True,

                },

            )

            extra_pets.append(pet)

        if extra_pets:

            for idx, applicant in enumerate(demo_users[:6]):

                pet = extra_pets[idx % len(extra_pets)]

                AdoptApplication.objects.update_or_create(

                    applicant=applicant,

                    pet=pet,

                    defaults={

                        'message': '\u8ba4\u540c\u79d1\u5b66\u5582\u517b\uff0c\u6709\u957f\u671f\u966a\u4f34\u80fd\u529b\uff0c\u613f\u610f\u914d\u5408\u56de\u8bbf\u3002',

                        'online_status': 'pending' if idx % 2 == 0 else 'approved',

                        'auditor': admin if idx % 2 == 1 else None,

                        'audited_at': timezone.now() if idx % 2 == 1 else None,

                    },

                )

        lf_specs = [

            (demo_users[5], 'lost', '\u72d7', '\u897f\u5b89\u5e02\u96c1\u5854\u533a\u5c0f\u5be8\u4e1c\u8def', '\u9ec4\u767d\u67ef\u57fa\uff0c\u7ea2\u8272\u9879\u5708', Decimal('34.223500'), Decimal('108.953100'), Decimal('600.00'), '13900000011', ['https://images.unsplash.com/photo-1561037404-61cd46aa615b?w=800']),

            (demo_users[6], 'found', '\u732b', '\u6d4e\u5357\u5e02\u5386\u4e0b\u533a\u6cc9\u57ce\u8def', '\u7070\u767d\u82f1\u77ed\uff0c\u80c6\u5c0f\u4eb2\u4eba', Decimal('36.651200'), Decimal('117.120100'), Decimal('0'), '13900000012', ['https://images.unsplash.com/photo-1511044568932-338cba0ad803?w=800']),

            (demo_users[7], 'lost', '\u72d7', '\u90d1\u5dde\u5e02\u4e8c\u4e03\u533a\u5927\u5b66\u8def', '\u9ed1\u8272\u7530\u56ed\u72ac\uff0c\u53f3\u8033\u5c16\u7f3a', Decimal('34.720300'), Decimal('113.650000'), Decimal('300.00'), '13900000013', ['https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800']),

            (demo_users[8], 'found', '\u732b', '\u6606\u660e\u5e02\u4e94\u534e\u533a\u5357\u5c4f\u8857', '\u4e09\u82b1\u6bcd\u732b\uff0c\u9879\u5708\u4e0a\u6709\u94c3\u94db', Decimal('25.038900'), Decimal('102.718300'), Decimal('0'), '13900000014', ['https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=800']),

            (demo_users[9], 'lost', '\u72d7', '\u53a6\u95e8\u5e02\u601d\u660e\u533a\u4e2d\u5c71\u8def', '\u767d\u8272\u6bd4\u718a\uff0c\u84dd\u8272\u80f8\u80cc', Decimal('24.479800'), Decimal('118.089400'), Decimal('1000.00'), '13900000015', ['https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=800']),

        ]

        for publisher, post_type, pet_species, address_text, features, lat, lon, reward, phone, photo_urls in lf_specs:

            LostFoundPost.objects.update_or_create(

                publisher=publisher,

                post_type=post_type,

                pet_species=pet_species,

                address_text=address_text,

                defaults={

                    'features': features,

                    'photo_urls': photo_urls,

                    'latitude': lat,

                    'longitude': lon,

                    'reward_amount': reward,

                    'contact_phone': phone,

                    'status': 'searching',

                },

            )

        post_specs = [

            (demo_users[0], '\u5317\u4eac\u987a\u4e49\u6551\u52a9\u72ac\u4e34\u65f6\u4e2d\u8f6c\u6c42\u52a9', 'rescue_share', '\u4eca\u5929\u63a5\u5230\u4e24\u53ea\u7530\u56ed\u72ac\uff0c\u4e34\u65f6\u4e2d\u8f6c\u538b\u529b\u8f83\u5927\uff0c\u6c42\u5927\u5bb6\u63a8\u8350\u5bc4\u517b\u8d44\u6e90\u3002', ['https://images.unsplash.com/photo-1517849845537-4d257902454a?w=800']),

            (demo_users[1], '\u4e0a\u6d77\u5e02\u533a\u627e\u5230\u53d7\u60ca\u82f1\u77ed\u732b\uff0c\u5df2\u9001\u533b', 'help_request', '\u5728\u9646\u5bb6\u5634\u5730\u94c1\u7ad9\u9644\u8fd1\u627e\u5230\u4e00\u53ea\u82f1\u77ed\u732b\uff0c\u5df2\u4e0a\u4f20\u56fe\u7247\uff0c\u82e5\u6709\u4e3b\u8bf7\u5c3d\u5feb\u8054\u7cfb\u3002', ['https://images.unsplash.com/photo-1511044568932-338cba0ad803?w=800']),

            (demo_users[2], '\u5e7f\u5dde\u9886\u517b\u7ecf\u9a8c\uff1a\u6210\u5e74\u72ac\u6bd4\u5e7c\u72ac\u66f4\u9002\u5408\u4e0a\u73ed\u65cf', 'pet_experience', '\u6211\u5bb6\u9886\u517b\u6210\u5e74\u67f4\u72ac 3 \u4e2a\u6708\uff0c\u6027\u683c\u7a33\u5b9a\uff0c\u8f83\u5c11\u62c6\u5bb6\uff0c\u63a8\u8350\u7ed9\u4e0a\u73ed\u65cf\u3002', ['https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800']),

            (demo_users[3], '\u676d\u5dde\u7edd\u80b2\u8855\u533a\u9879\u76ee\u5fd7\u613f\u8005\u62db\u52df', 'general', '\u5468\u672b\u5c06\u8fdb\u884c\u8857\u533a TNR \u9879\u76ee\uff0c\u9700\u8981\u6293\u6355\u3001\u966a\u62a4\u3001\u5ba3\u4f20\u5fd7\u613f\u8005\uff0c\u6b22\u8fce\u62a5\u540d\u3002', ['https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=800']),

            (demo_users[4], '\u6b66\u6c49\u6551\u52a9\u7ad9\u7269\u8d44\u6e05\u5355\u66f4\u65b0', 'rescue_share', '\u76ee\u524d\u7f3a\u5c11\u5e7c\u72ac\u5976\u7c89\uff0c\u732b\u7802\uff0c\u4e00\u6b21\u6027\u5c3f\u57ab\u4e0e\u5916\u7528\u6d88\u6bd2\u55b7\u96fe\uff0c\u611f\u8c22\u5927\u5bb6\u652f\u6301\u3002', ['https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=800']),

        ]

        for author, title, category, content, image_urls in post_specs:

            post, _ = CommunityPost.objects.update_or_create(

                author=author,

                title=title,

                defaults={

                    'category': category,

                    'content': content,

                    'image_urls': image_urls,

                },

            )

            PostLike.objects.get_or_create(post=post, user=admin)

            CommunityComment.objects.get_or_create(

                post=post,

                author=user,

                parent=None,

                content='\u5df2\u7ecf\u5e2e\u4f60\u8f6c\u53d1\uff0c\u5e0c\u671b\u66f4\u591a\u4eba\u770b\u5230\u8fd9\u6761\u4fe1\u606f\u3002',

            )

        for post in CommunityPost.objects.all():

            like_ct = PostLike.objects.filter(post=post).count()

            comment_ct = CommunityComment.objects.filter(post=post, is_deleted=False).count()

            CommunityPost.objects.filter(pk=post.pk).update(like_count=like_ct, comment_count=comment_ct)

        self.stdout.write(self.style.SUCCESS('[OK] \u6f14\u793a\u6570\u636e\u5df2\u5c31\u7eea\uff08\u5168\u90e8\u4e3a\u4e2d\u6587\u5185\u5bb9\uff09'))

        self.stdout.write('  \u7ba1\u7406\u5458\u8d26\u53f7: admin / admin12345')

        self.stdout.write('  \u666e\u901a\u7528\u6237:   demo / demo12345')

        self.stdout.write(f'  \u53ef\u9886\u517b\u5ba0\u7269: {PetProfile.objects.filter(adoption_status="available").count()} \u53ea')

        self.stdout.write(f'  \u5df2\u9886\u517b\u5ba0\u7269: {PetProfile.objects.filter(adoption_status="adopted").count()} \u53ea')

        self.stdout.write('  \u5efa\u8bae\u7ee7\u7eed\u8fd0\u884c: python manage.py seed_test_data')



