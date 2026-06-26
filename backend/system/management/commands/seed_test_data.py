"""
模块说明：测试数据种子脚本（答辩不重点讲解）。
"""

from decimal import Decimal

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand

from django.utils import timezone

from cms.models import CmsArticle, CmsCategory

from lostfound.models import LostFoundPost

from pets.models import PetProfile

from portal.models import PortalCarousel



class Command(BaseCommand):

    help = '安全添加更多测试数据（科普文章、公告、报失寻主、领养宠物）'

    def handle(self, *args, **options):

        # 获取管理员用户

        admin = User.objects.filter(username='admin').first()

        if not admin:

            self.stdout.write(self.style.ERROR('请先运行 seed_demo 创建管理员用户'))

            return

        # 获取普通用户

        demo = User.objects.filter(username='demo').first()

        if not demo:

            self.stdout.write(self.style.ERROR('请先运行 seed_demo 创建演示用户'))

            return

        # ========== 科普文章 ==========

        science_category, _ = CmsCategory.objects.get_or_create(

            name='科普',

            defaults={'sort_order': 1, 'description': '养宠科普知识'},

        )

        science_articles = [

            {

                'title': '如何正确喂养流浪猫',

                'summary': '了解流浪猫的营养需求和喂养注意事项',

                'content': '流浪猫的喂养需要特别注意营养均衡。建议选择高蛋白猫粮，并确保有充足的清水。同时要注意定时定点喂养，避免食物浪费和环境污染。',

            },

            {

                'title': '狗狗疫苗接种指南',

                'summary': '幼犬疫苗接种时间表和注意事项',

                'content': '幼犬通常在6-8周龄开始接种第一针疫苗，之后每3-4周加强一次，直到16周龄。核心疫苗包括犬瘟热、细小病毒、腺病毒和狂犬病疫苗。',

            },

            {

                'title': '宠物绝育的好处与时机',

                'summary': '宠物绝育的最佳时间和术后护理',

                'content': '宠物绝育不仅可以控制流浪动物数量，还能降低某些疾病风险。猫狗建议在6个月左右进行绝育手术，术后需注意伤口护理和饮食管理。',

            },

            {

                'title': '夏季宠物防暑小贴士',

                'summary': '高温天气如何保护你的宠物',

                'content': '夏季高温容易导致宠物中暑。建议避免在正午时段遛狗，保持室内通风，提供充足饮水。短鼻犬种（如法斗、英斗）尤其需要注意防暑。',

            },

            {

                'title': '宠物常见皮肤病识别与处理',

                'summary': '认识宠物皮肤病的症状和家庭护理方法',

                'content': '宠物常见皮肤病包括真菌感染、细菌感染、寄生虫感染和过敏性皮炎。症状包括瘙痒、脱毛、红斑、皮屑等。发现异常应及时就医。',

            },

            {

                'title': '领养宠物前的准备工作',

                'summary': '领养宠物需要做好的物质和心理准备',

                'content': '领养宠物前需要准备：合适的居住空间、宠物用品（食盆、水盆、猫砂盆/狗垫）、宠物食品、玩具等。同时要做好长期陪伴的心理准备。',

            },

        ]

        added_science = 0

        for article in science_articles:

            _, created = CmsArticle.objects.get_or_create(

                title=article['title'],

                defaults={

                    'category': science_category,

                    'author': admin,

                    'article_type': 'science',

                    'summary': article['summary'],

                    'content': article['content'],

                    'status': 1,

                    'published_at': timezone.now(),

                },

            )

            if created:

                added_science += 1

        self.stdout.write(f'  科普文章: 新增 {added_science} 条')

        # ========== 公告 ==========

        announcement_category, _ = CmsCategory.objects.get_or_create(

            name='公告',

            defaults={'sort_order': 2, 'description': '平台公告'},

        )

        announcements = [

            {

                'title': '平台新版功能上线通知',

                'summary': '新增附近搜索和逆地理编码功能',

                'content': '亲爱的用户，平台已上线新版功能，包括附近走失宠物搜索、逆地理编码自动获取地址等。欢迎体验！',

                'is_pinned': True,

            },

            {

                'title': '2026年夏季领养日活动预告',

                'summary': '本月将举办大型线下领养日活动',

                'content': '平台将于本月20日举办夏季领养日活动，届时将有50+只待领养宠物到场，欢迎爱心人士参与。',

                'is_pinned': True,

            },

            {

                'title': '志愿者招募公告',

                'summary': '诚邀爱心人士加入我们的志愿者团队',

                'content': '我们正在招募流浪动物救助志愿者，工作内容包括日常喂养、医疗协助、领养审核等。有意者请通过平台联系管理员。',

                'is_pinned': False,

            },

            {

                'title': '关于平台维护的通知',

                'summary': '系统将于本周六凌晨进行维护升级',

                'content': '平台将于本周六凌晨2:00-6:00进行系统维护，期间部分功能可能无法使用，敬请谅解。',

                'is_pinned': False,

            },

        ]

        added_announcement = 0

        for article in announcements:

            _, created = CmsArticle.objects.get_or_create(

                title=article['title'],

                defaults={

                    'category': announcement_category,

                    'author': admin,

                    'article_type': 'announcement',

                    'summary': article['summary'],

                    'content': article['content'],

                    'is_pinned': article['is_pinned'],

                    'status': 1,

                    'published_at': timezone.now(),

                },

            )

            if created:

                added_announcement += 1

        self.stdout.write(f'  公告: 新增 {added_announcement} 条')

        # ========== 报失寻主 ==========

        lost_found_posts = [

            {

                'post_type': 'lost',

                'pet_species': '橘猫',

                'features': '橘色短毛、黄色眼睛、约2岁、脖子上有红色项圈',

                'latitude': Decimal('30.639200'),

                'longitude': Decimal('104.043200'),

                'address_text': '成都市武侯区玉林小区',

                'reward_amount': Decimal('300.00'),

                'contact_phone': '13912345678',

            },

            {

                'post_type': 'lost',

                'pet_species': '柯基犬',

                'features': '黄白双色、短腿、尾巴有白色毛尖、佩戴蓝色项圈',

                'latitude': Decimal('30.657800'),

                'longitude': Decimal('104.080800'),

                'address_text': '成都市锦江区春熙路附近',

                'reward_amount': Decimal('1000.00'),

                'contact_phone': '13698765432',

            },

            {

                'post_type': 'found',

                'pet_species': '布偶猫',

                'features': '蓝眼睛、长毛、白色为主带灰色花纹、非常亲人',

                'latitude': Decimal('30.548500'),

                'longitude': Decimal('104.059800'),

                'address_text': '成都市高新区天府三街',

                'reward_amount': Decimal('0'),

                'contact_phone': '15855556666',

            },

            {

                'post_type': 'lost',

                'pet_species': '泰迪犬',

                'features': '棕色卷毛、约5岁、体型偏胖、走失时穿红色衣服',

                'latitude': Decimal('30.670800'),

                'longitude': Decimal('104.055800'),

                'address_text': '成都市青羊区宽窄巷子',

                'reward_amount': Decimal('500.00'),

                'contact_phone': '13777778888',

            },

            {

                'post_type': 'found',

                'pet_species': '狸花猫',

                'features': '灰色条纹、绿色眼睛、约1岁、左耳有缺口（已绝育标记）',

                'latitude': Decimal('30.659800'),

                'longitude': Decimal('104.099800'),

                'address_text': '成都市成华区建设路',

                'reward_amount': Decimal('0'),

                'contact_phone': '15999990000',

            },

            {

                'post_type': 'lost',

                'pet_species': '哈士奇',

                'features': '灰白毛色、蓝色眼睛、体型较大、走失时戴黑色项圈',

                'latitude': Decimal('30.718800'),

                'longitude': Decimal('104.043800'),

                'address_text': '成都市金牛区欢乐谷附近',

                'reward_amount': Decimal('2000.00'),

                'contact_phone': '13344445555',

            },

        ]

        added_lost = 0

        for post in lost_found_posts:

            # 用特征和地址来避免重复创建

            obj, created = LostFoundPost.objects.get_or_create(

                pet_species=post['pet_species'],

                features=post['features'],

                address_text=post['address_text'],

                defaults={

                    'publisher': demo,

                    'post_type': post['post_type'],

                    'latitude': post.get('latitude'),

                    'longitude': post.get('longitude'),

                    'reward_amount': post['reward_amount'],

                    'contact_phone': post['contact_phone'],

                    'status': 'searching',

                },

            )

            # 如果已存在但没有经纬度，补充更新

            if not created and (obj.latitude is None or obj.longitude is None):

                obj.latitude = post.get('latitude')

                obj.longitude = post.get('longitude')

                obj.save(update_fields=['latitude', 'longitude'])

                self.stdout.write(f'    补充坐标: {obj.pet_species} ({obj.latitude}, {obj.longitude})')

            if created:

                added_lost += 1

        self.stdout.write(f'  报失寻主: 新增 {added_lost} 条')

        # ========== 领养宠物 ==========

        adoption_pets = [

            {

                'name': '小花',

                'species': '猫',

                'breed': '橘猫',

                'age_months': 8,

                'gender': '母',

                'health_status': '已驱虫、已接种疫苗',

                'description': '性格温顺亲人，喜欢晒太阳，已绝育。适合有养猫经验的主人。',

                'photo_url': 'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=500&h=400&fit=crop',

            },

            {

                'name': '旺财',

                'species': '狗',

                'breed': '中华田园犬',

                'age_months': 14,

                'gender': '公',

                'health_status': '已驱虫、已接种疫苗、已绝育',

                'description': '活泼好动，聪明机灵，适合有院子的家庭。已学会基本指令。',

                'photo_url': 'https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=500&h=400&fit=crop',

            },

            {

                'name': '咪咪',

                'species': '猫',

                'breed': '狸花猫',

                'age_months': 6,

                'gender': '母',

                'health_status': '已驱虫、已接种第一针疫苗',

                'description': '活泼可爱，好奇心强，喜欢玩逗猫棒。适合新手领养。',

                'photo_url': 'https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=500&h=400&fit=crop',

            },

            {

                'name': '小黑',

                'species': '狗',

                'breed': '拉布拉多',

                'age_months': 24,

                'gender': '公',

                'health_status': '已驱虫、已接种疫苗、已绝育',

                'description': '性格温和，对人友善，适合有小孩的家庭。需要较大的活动空间。',

                'photo_url': 'https://images.unsplash.com/photo-1544568100-847a948585b9?w=500&h=400&fit=crop',

            },

            {

                'name': '雪球',

                'species': '猫',

                'breed': '英短蓝白',

                'age_months': 10,

                'gender': '公',

                'health_status': '已驱虫、已接种疫苗、已绝育',

                'description': '安静优雅，喜欢被抚摸，适合公寓饲养。不挑食，好养活。',

                'photo_url': 'https://images.unsplash.com/photo-1513360371669-4adf3dd7dff8?w=500&h=400&fit=crop',

            },

        ]

        added_pets = 0

        for pet in adoption_pets:

            _, created = PetProfile.objects.get_or_create(

                name=pet['name'],

                species=pet['species'],

                defaults={

                    'breed': pet['breed'],

                    'age_months': pet['age_months'],

                    'gender': pet['gender'],

                    'health_status': pet['health_status'],

                    'description': pet['description'],

                    'photo_url': pet['photo_url'],

                    'adoption_status': 'available',

                    'is_public': True,

                },

            )

            if created:

                added_pets += 1

        self.stdout.write(f'  领养宠物: 新增 {added_pets} 条')

        # ========== 轮播图（图片与领养宠物一一对应） ==========

        carousel_items = [

            {

                'title': '欢迎领养',

                'image_url': 'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=1200&h=400&fit=crop',

                'link_url': '/pets',

                'sort_order': 1,

            },

            {

                'title': '小花 - 橘猫妹妹找家',

                'image_url': 'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=1200&h=400&fit=crop',

                'link_url': '/pets',

                'sort_order': 2,

            },

            {

                'title': '旺财 - 中华田园犬待领养',

                'image_url': 'https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=1200&h=400&fit=crop',

                'link_url': '/pets',

                'sort_order': 3,

            },

            {

                'title': '咪咪 - 狸花猫求带走',

                'image_url': 'https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=1200&h=400&fit=crop',

                'link_url': '/pets',

                'sort_order': 4,

            },

            {

                'title': '小黑 - 拉布拉多寻主人',

                'image_url': 'https://images.unsplash.com/photo-1544568100-847a948585b9?w=1200&h=400&fit=crop',

                'link_url': '/pets',

                'sort_order': 5,

            },

            {

                'title': '雪球 - 英短蓝白求带走',

                'image_url': 'https://images.unsplash.com/photo-1513360371669-4adf3dd7dff8?w=1200&h=400&fit=crop',

                'link_url': '/pets',

                'sort_order': 6,

            },

        ]

        added_carousel = 0

        for item in carousel_items:

            _, created = PortalCarousel.objects.get_or_create(

                title=item['title'],

                defaults={

                    'image_url': item['image_url'],

                    'link_url': item['link_url'],

                    'sort_order': item['sort_order'],

                    'status': 1,

                },

            )

            if created:

                added_carousel += 1

        self.stdout.write(f'  轮播图: 新增 {added_carousel} 条')

        # ========== 总结 ==========

        total_science = CmsArticle.objects.filter(article_type='science', status=1).count()

        total_announcement = CmsArticle.objects.filter(article_type='announcement', status=1).count()

        total_lost = LostFoundPost.objects.filter(status='searching').count()

        total_adoptable = PetProfile.objects.filter(adoption_status='available').count()

        total_carousel = PortalCarousel.objects.filter(status=1).count()

        self.stdout.write(self.style.SUCCESS('=' * 40))

        self.stdout.write(self.style.SUCCESS('测试数据添加完成！'))

        self.stdout.write(f'  科普文章总数: {total_science}')

        self.stdout.write(f'  公告总数: {total_announcement}')

        self.stdout.write(f'  报失寻主总数: {total_lost}')

        self.stdout.write(f'  待领养宠物: {total_adoptable}')

        self.stdout.write(f'  轮播图: {total_carousel}')

        self.stdout.write(self.style.SUCCESS('=' * 40))



