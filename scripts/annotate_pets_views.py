# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "backend" / "pets" / "views.py"
text = p.read_text(encoding="utf-8")

header = (
    '"""\n'
    "\u6a21\u5757\u8bf4\u660e\uff1a\u5ba0\u7269\u6863\u6848\u4e0e\u9886\u517b\u7533\u8bf7 API \u89c6\u56fe\u3002\n\n"
    "\u5305\u542b\uff1a\u5ba0\u7269 CRUD\u3001\u9644\u8fd1\u67e5\u8be2\u3001\u9886\u517b\u7533\u8bf7\u3001\u7ba1\u7406\u5458\u5ba1\u6838\u4e0e\u7ebf\u4e0b\u6838\u9a8c\u3002\n"
    '"""\n\n'
)
if not text.lstrip().startswith('"""'):
    text = header + text.lstrip()

pairs = [
    (
        "class PetProfileViewSet(viewsets.ModelViewSet):\n    queryset",
        "class PetProfileViewSet(viewsets.ModelViewSet):\n"
        '    """\n'
        "\u529f\u80fd\uff1a\u5ba0\u7269\u6863\u6848 CRUD\u3001\u9644\u8fd1\u67e5\u8be2\u4e0e\u6211\u7684\u5ba0\u7269\u3002\n"
        "\u3010\u6743\u9650\u3011visitor/user\uff1alist/retrieve/nearby \u4ec5\u516c\u5f00\u6863\u6848\uff1badmin\uff1a\u53ef\u589e\u5220\u6539\u3002\n"
        '    """\n    queryset',
    ),
    (
        "    def get_serializer_class(self):\n        if self.action",
        "    def get_serializer_class(self):\n"
        '        """\u529f\u80fd\uff1a\u66f4\u65b0\u64cd\u4f5c\u4f7f\u7528 PetProfileUpdateSerializer\u3002\u8fd4\u56de\uff1aSerializer \u7c7b\u3002"""\n'
        "        if self.action",
    ),
    (
        "    def get_permissions(self):\n        if self.action in ['list', 'retrieve', 'nearby']:",
        "    def get_permissions(self):\n"
        '        """\n'
        "\u529f\u80fd\uff1a\u6309\u52a8\u4f5c\u5206\u914d\u6743\u9650\u3002\n"
        "\u3010\u6743\u9650\u3011list/retrieve/nearby\uff1avisitor \u53ef\u8bbf\u95ee\uff1bmy_pets\uff1a\u9700\u767b\u5f55\uff1b\u5176\u4f59\uff1aadmin\u3002\n"
        '        """\n'
        "        if self.action in ['list', 'retrieve', 'nearby']:",
    ),
    (
        "    def get_queryset(self):\n        qs = super().get_queryset()",
        "    def get_queryset(self):\n"
        '        """\n'
        "\u529f\u80fd\uff1a\u6309\u67e5\u8be2\u53c2\u6570\u7b5b\u9009\uff0c\u975e admin \u9ed8\u8ba4\u53ea\u770b is_public=True\u3002\n"
        "\u3010\u6743\u9650\u3011visitor/user \u4ec5\u516c\u5f00\u6863\u6848\uff1badmin \u53ef\u770b\u5168\u90e8\u3002\n"
        '        """\n        qs = super().get_queryset()',
    ),
    (
        "        if is_public is not None and self.action in ['list', 'retrieve']:\n            if not (self.request.user.is_authenticated",
        "        # \u3010\u6743\u9650\u3011\u975e admin \u5728\u5217\u8868/\u8be6\u60c5\u53ea\u80fd\u770b is_public=True\n"
        "        if is_public is not None and self.action in ['list', 'retrieve']:\n            if not (self.request.user.is_authenticated",
    ),
    (
        "    def _haversine_distance(lat1, lon1, lat2, lon2):\n        radius_km = 6371",
        "    def _haversine_distance(lat1, lon1, lat2, lon2):\n"
        '        """\u529f\u80fd\uff1a\u8ba1\u7b97\u4e24\u70b9\u7403\u9762\u8ddd\u79bb\uff08\u5343\u7c73\uff09\u3002\u8fd4\u56de\uff1afloat\u3002"""\n        radius_km = 6371',
    ),
    (
        "    def nearby(self, request):\n        try:",
        "    def nearby(self, request):\n"
        '        """\n'
        "\u529f\u80fd\uff1a\u6309\u7ecf\u7eac\u5ea6\u4e0e\u534a\u5f84\u67e5\u8be2\u9644\u8fd1\u5ba0\u7269\u3002\n"
        "\u3010\u6743\u9650\u3011visitor/user/admin \u5747\u53ef\uff08\u4ec5\u516c\u5f00\u6863\u6848\uff09\u3002\n"
        '        """\n        try:',
    ),
    (
        "    def my_pets(self, request):\n        qs = PetProfile.objects.filter(",
        "    def my_pets(self, request):\n"
        '        """\n'
        "\u529f\u80fd\uff1a\u83b7\u53d6\u5f53\u524d\u7528\u6237\u53d1\u5e03\u7684\u5ba0\u7269\u5217\u8868\u3002\n"
        "\u3010\u6743\u9650\u3011\u9700\u767b\u5f55 user/admin\u3002\n"
        '        """\n        qs = PetProfile.objects.filter(',
    ),
    (
        "class AdoptApplicationViewSet(viewsets.ModelViewSet):\n    queryset = AdoptApplication",
        "class AdoptApplicationViewSet(viewsets.ModelViewSet):\n"
        '    """\n'
        "\u529f\u80fd\uff1a\u9886\u517b\u7533\u8bf7\u63d0\u4ea4\u3001\u95ee\u5377\u4e0e\u9644\u4ef6\u3002\n"
        "\u3010\u6743\u9650\u3011user \u53ef\u521b\u5efa/\u67e5\u672c\u4eba\uff1badmin \u53ef\u5ba1\u6838\u3002\n"
        '    """\n    queryset = AdoptApplication',
    ),
    (
        "class AdoptApplicationViewSet(viewsets.ModelViewSet):\n    queryset = AdoptApplication.objects.select_related('applicant', 'pet', 'auditor', 'offline_verify').all()\n    serializer_class = AdoptApplicationSerializer\n    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']\n\n    def get_permissions(self):\n        if self.action in ['create', 'my', 'questionnaire', 'attachments']:",
        "class AdoptApplicationViewSet(viewsets.ModelViewSet):\n    queryset = AdoptApplication.objects.select_related('applicant', 'pet', 'auditor', 'offline_verify').all()\n    serializer_class = AdoptApplicationSerializer\n    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']\n\n    def get_permissions(self):\n"
        '        """\n'
        "\u3010\u6743\u9650\u3011create/my/questionnaire/attachments/retrieve\uff1a\u9700\u767b\u5f55\uff1b\u5176\u4f59\uff1aadmin\u3002\n"
        '        """\n        if self.action in [\'create\', \'my\', \'questionnaire\', \'attachments\']:',
    ),
    (
        "        if self.action == 'retrieve':\n            if user_is_admin(self.request.user):",
        "        if self.action == 'retrieve':\n"
        "            # \u3010\u6743\u9650\u3011admin \u53ef\u770b\u4efb\u610f\u7533\u8bf7\uff1buser \u4ec5\u770b\u81ea\u5df1\u7684\n"
        "            if user_is_admin(self.request.user):",
    ),
    (
        "    def perform_create(self, serializer):\n        pet = serializer.validated_data['pet']",
        "    def perform_create(self, serializer):\n"
        '        """\u529f\u80fd\uff1a\u521b\u5efa\u9886\u517b\u7533\u8bf7\u5e76\u5c06\u5ba0\u7269\u72b6\u6001\u6539\u4e3a pending\u3002\u3010\u6743\u9650\u3011\u9700\u767b\u5f55 user\u3002"""\n'
        "        pet = serializer.validated_data['pet']",
    ),
    (
        "        if pet.adoption_status != 'available':\n            raise ValidationError({'pet_id':",
        "        # \u5206\u652f\uff1a\u5ba0\u7269\u5f53\u524d\u4e0d\u53ef\u9886\u517b\n        if pet.adoption_status != 'available':\n            raise ValidationError({'pet_id':",
    ),
    (
        "            raise ValidationError({'pet_id': '\\u8be5\\u5ba0\\u7269\\u5f53\\u524d\\u4e0d\\u53ef\\u7533\\u8bf7\\u9886\\u517b'})\n        if AdoptApplication.objects.filter(",
        "            raise ValidationError({'pet_id': '\\u8be5\\u5ba0\\u7269\\u5f53\\u524d\\u4e0d\\u53ef\\u7533\\u8bf7\\u9886\\u517b'})\n"
        "        # \u5206\u652f\uff1a\u5df2\u6709\u8fdb\u884c\u4e2d\u7684\u7533\u8bf7\n        if AdoptApplication.objects.filter(",
    ),
    (
        "    def my(self, request):\n        qs = self.get_queryset()",
        "    def my(self, request):\n"
        '        """\u529f\u80fd\uff1a\u8fd4\u56de\u5f53\u524d\u7528\u6237\u7684\u9886\u517b\u7533\u8bf7\u5217\u8868\u3002\u3010\u6743\u9650\u3011\u9700\u767b\u5f55 user\u3002"""\n'
        "        qs = self.get_queryset()",
    ),
    (
        "    def questionnaire(self, request, pk=None):\n        app = self.get_object()\n        if app.applicant != request.user:",
        "    def questionnaire(self, request, pk=None):\n"
        '        """\u529f\u80fd\uff1a\u63d0\u4ea4\u9886\u517b\u95ee\u5377\u3002\u3010\u6743\u9650\u3011\u4ec5\u7533\u8bf7\u4eba\u672c\u4eba user\u3002"""\n'
        "        app = self.get_object()\n        # \u3010\u6743\u9650\u3011\u975e\u672c\u4eba\u7981\u6b62\n        if app.applicant != request.user:",
    ),
    (
        "    def attachments(self, request, pk=None):\n        app = self.get_object()\n        if app.applicant != request.user:",
        "    def attachments(self, request, pk=None):\n"
        '        """\u529f\u80fd\uff1a\u4e0a\u4f20\u9886\u517b\u7533\u8bf7\u9644\u4ef6\u3002\u3010\u6743\u9650\u3011\u4ec5\u7533\u8bf7\u4eba\u672c\u4eba user\u3002"""\n'
        "        app = self.get_object()\n        # \u3010\u6743\u9650\u3011\u975e\u672c\u4eba\u7981\u6b62\n        if app.applicant != request.user:",
    ),
    (
        "class AdminAdoptApplicationViewSet(viewsets.GenericViewSet):\n    queryset = AdoptApplication.objects.select_related(",
        "class AdminAdoptApplicationViewSet(viewsets.GenericViewSet):\n"
        '    """\u529f\u80fd\uff1a\u7ba1\u7406\u5458\u9886\u517b\u5ba1\u6838\u4e0e\u8be6\u60c5\u67e5\u8be2\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "    queryset = AdoptApplication.objects.select_related(",
    ),
    (
        "    def list(self, request):\n        qs = self.get_queryset()\n        serializer = AdminAdoptApplicationListSerializer",
        "    def list(self, request):\n"
        '        """\u529f\u80fd\uff1a\u9886\u517b\u7533\u8bf7\u5217\u8868\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "        qs = self.get_queryset()\n        serializer = AdminAdoptApplicationListSerializer",
    ),
    (
        "    def review_detail(self, request, pk=None):\n        app = self.get_object()",
        "    def review_detail(self, request, pk=None):\n"
        '        """\u529f\u80fd\uff1a\u67e5\u770b\u7533\u8bf7\u5ba1\u6838\u8be6\u60c5\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "        app = self.get_object()",
    ),
    (
        "class AdminAdoptApplicationViewSet(viewsets.GenericViewSet):\n    \"\"\"\u529f\u80fd\uff1a\u7ba1\u7406\u5458\u9886\u517b\u5ba1\u6838\u4e0e\u8be6\u60c5\u67e5\u8be2\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n    queryset = AdoptApplication.objects.select_related(\n        'applicant', 'applicant__profile', 'pet', 'pet__rescue_case', 'auditor',\n    ).prefetch_related('attachments', 'questionnaire').all()\n    serializer_class = AdoptApplicationAuditSerializer\n    permission_classes = [IsAdminRole]\n\n    def list(self, request):\n        \"\"\"\u529f\u80fd\uff1a\u9886\u517b\u7533\u8bf7\u5217\u8868\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n        qs = self.get_queryset()\n        serializer = AdminAdoptApplicationListSerializer(qs, many=True, context={'request': request})\n        return Response(serializer.data)\n\n    def review_detail(self, request, pk=None):\n        \"\"\"\u529f\u80fd\uff1a\u67e5\u770b\u7533\u8bf7\u5ba1\u6838\u8be6\u60c5\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n        app = self.get_object()\n        return Response(AdoptApplicationReviewDetailSerializer(app).data)\n\n    def update(self, request, pk=None):\n        app = self.get_object()",
        "class AdminAdoptApplicationViewSet(viewsets.GenericViewSet):\n    \"\"\"\u529f\u80fd\uff1a\u7ba1\u7406\u5458\u9886\u517b\u5ba1\u6838\u4e0e\u8be6\u60c5\u67e5\u8be2\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n    queryset = AdoptApplication.objects.select_related(\n        'applicant', 'applicant__profile', 'pet', 'pet__rescue_case', 'auditor',\n    ).prefetch_related('attachments', 'questionnaire').all()\n    serializer_class = AdoptApplicationAuditSerializer\n    permission_classes = [IsAdminRole]\n\n    def list(self, request):\n        \"\"\"\u529f\u80fd\uff1a\u9886\u517b\u7533\u8bf7\u5217\u8868\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n        qs = self.get_queryset()\n        serializer = AdminAdoptApplicationListSerializer(qs, many=True, context={'request': request})\n        return Response(serializer.data)\n\n    def review_detail(self, request, pk=None):\n        \"\"\"\u529f\u80fd\uff1a\u67e5\u770b\u7533\u8bf7\u5ba1\u6838\u8be6\u60c5\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n        app = self.get_object()\n        return Response(AdoptApplicationReviewDetailSerializer(app).data)\n\n    def update(self, request, pk=None):\n"
        '        """\u529f\u80fd\uff1a\u5ba1\u6838\u9886\u517b\u7533\u8bf7\u5e76\u8bb0\u5ba1\u8ba1\u65e5\u5fd7\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "        app = self.get_object()",
    ),
    (
        "class AdminOfflineVerifyViewSet(viewsets.GenericViewSet):\n    queryset = AdoptOfflineVerify",
        "class AdminOfflineVerifyViewSet(viewsets.GenericViewSet):\n"
        '    """\u529f\u80fd\uff1a\u7ebf\u4e0b\u6838\u9a8c\u7ed3\u679c\u5f55\u5165\u4e0e\u8054\u52a8\u5ba0\u7269\u72b6\u6001\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "    queryset = AdoptOfflineVerify",
    ),
    (
        "class AdminOfflineVerifyViewSet(viewsets.GenericViewSet):\n    \"\"\"\u529f\u80fd\uff1a\u7ebf\u4e0b\u6838\u9a8c\u7ed3\u679c\u5f55\u5165\u4e0e\u8054\u52a8\u5ba0\u7269\u72b6\u6001\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n    queryset = AdoptOfflineVerify.objects.select_related('application').all()\n    serializer_class = AdoptOfflineVerifySerializer\n    permission_classes = [IsAdminRole]\n\n    def update(self, request, pk=None):\n        verify = self.get_object()",
        "class AdminOfflineVerifyViewSet(viewsets.GenericViewSet):\n    \"\"\"\u529f\u80fd\uff1a\u7ebf\u4e0b\u6838\u9a8c\u7ed3\u679c\u5f55\u5165\u4e0e\u8054\u52a8\u5ba0\u7269\u72b6\u6001\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\"\"\"\n    queryset = AdoptOfflineVerify.objects.select_related('application').all()\n    serializer_class = AdoptOfflineVerifySerializer\n    permission_classes = [IsAdminRole]\n\n    def update(self, request, pk=None):\n"
        '        """\u529f\u80fd\uff1a\u66f4\u65b0\u7ebf\u4e0b\u6838\u9a8c\u7ed3\u679c\u5e76\u8054\u52a8\u7533\u8bf7\u4e0e\u5ba0\u7269\u72b6\u6001\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "        verify = self.get_object()",
    ),
    (
        "        if new_status == 'failed' and not (verify_note or '').strip():",
        "        # \u5206\u652f\uff1a\u6838\u9a8c\u5931\u8d25\u5fc5\u987b\u586b\u5199\u539f\u56e0\n        if new_status == 'failed' and not (verify_note or '').strip():",
    ),
    (
        "        verify.save()\n        if verify.verify_status == 'passed':",
        "        verify.save()\n        # \u5206\u652f\uff1a\u7ebf\u4e0b\u6838\u9a8c\u901a\u8fc7\n        if verify.verify_status == 'passed':",
    ),
    (
        "        elif verify.verify_status == 'failed':\n            verify.application.online_status = 'rejected'",
        "        # \u5206\u652f\uff1a\u7ebf\u4e0b\u6838\u9a8c\u5931\u8d25\uff0c\u6062\u590d\u53ef\u9886\u517b\n        elif verify.verify_status == 'failed':\n            verify.application.online_status = 'rejected'",
    ),
    (
        "    def create_for_application(self, request, application_id=None):\n        app = AdoptApplication.objects.get(pk=application_id)",
        "    def create_for_application(self, request, application_id=None):\n"
        '        """\u529f\u80fd\uff1a\u4e3a\u7533\u8bf7\u5355\u521b\u5efa\u6216\u83b7\u53d6\u7ebf\u4e0b\u6838\u9a8c\u8bb0\u5f55\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002"""\n'
        "        app = AdoptApplication.objects.get(pk=application_id)",
    ),
]

for old, new in pairs:
    if old in text:
        text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("annotated pets/views.py")
