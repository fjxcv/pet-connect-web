# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "frontend" / "src"

modules = ROOT / "api" / "modules.js"
text = modules.read_text(encoding="utf-8")
start = text.index("export const adminAPI")
end = text.index("};", text.index("export const aiAPI")) + 2
new_block = (
    "/** \u540e\u53f0\u7ba1\u7406\uff1a\u770b\u677f\u3001\u5ba1\u6838\u3001\u914d\u7f6e\u4e0e AI \u65e5\u5fd7\u3002\u3010\u6743\u9650\u3011\u4ec5 admin */\n"
    "export const adminAPI = {\n"
    "  getDashboard: () => api.get('/admin/dashboard/'),\n"
    "  getUsers: (params) => api.get('/admin/users/', { params }),\n"
    "  updateUser: (id, data) => api.patch(`/admin/users/${id}/`, data),\n"
    "  getModeration: () => api.get('/admin/moderation/'),\n"
    "  createModeration: (data) => api.post('/admin/moderation/', data),\n"
    "  getConfig: () => api.get('/admin/config/'),\n"
    "  updateConfig: (key, data) => api.patch(`/admin/config/${key}/`, data),\n"
    "  getAiLogs: (params) => api.get('/admin/ai-logs/', { params }),\n"
    "  getAiLogStats: () => api.get('/admin/ai-logs/stats/'),\n"
    "};\n"
    "const AI_TIMEOUT_MS = 90000;\n\n\n"
    "/** AI \u8f85\u52a9\u3002\u3010\u6743\u9650\u3011user/admin \u9700\u767b\u5f55 */\n"
    "export const aiAPI = {\n"
    "  breedDetect: (data) => api.post('/ai/breed-detect/', data, { timeout: AI_TIMEOUT_MS }),\n"
    "  adoptCopy: (data) => api.post('/ai/adopt-copy/', data, { timeout: AI_TIMEOUT_MS }),\n"
    "  qa: (data) => api.post('/ai/qa/', data, { timeout: AI_TIMEOUT_MS }),\n"
    "};"
)
text = text[:start] + new_block + text[end:]
modules.write_text(text, encoding="utf-8")

aiw = ROOT / "components" / "AiAssistantWidget.js"
t = aiw.read_text(encoding="utf-8")
repls = [
    (
        "const AiAssistantWidget = () => {",
        "/**\n * \u529f\u80fd\uff1a\u667a\u80fd\u517b\u5ba0\u52a9\u624b\u6d6e\u7a97\uff0c\u8c03\u7528 aiAPI.qa\u3002\n * \u3010\u6743\u9650\u3011visitor \u9700\u767b\u5f55\uff1buser/admin \u53ef\u7528\u3002\n */\nconst AiAssistantWidget = () => {",
    ),
    (
        "  const formatAiError = (err) => {",
        "  /** \u529f\u80fd\uff1a\u5c06 API \u9519\u8bef\u8f6c\u4e3a\u53cb\u597d\u63d0\u793a\u3002 */\n  const formatAiError = (err) => {",
    ),
    (
        "  const send = async () => {",
        "  /** \u529f\u80fd\uff1a\u53d1\u9001\u95ee\u9898\u8c03\u7528 AI\u3002\u3010\u6743\u9650\u3011\u9700 token\u3002 */\n  const send = async () => {",
    ),
    (
        "    if (!localStorage.getItem('token')) {",
        "    // \u3010\u6743\u9650\u3011\u6e38\u5ba2\u672a\u767b\u5f55\n    if (!localStorage.getItem('token')) {",
    ),
]
for old, new in repls:
    if old in t:
        t = t.replace(old, new, 1)
aiw.write_text(t, encoding="utf-8")

bdr = ROOT / "components" / "BreedDetectResult.js"
t = bdr.read_text(encoding="utf-8")
old = "const BreedDetectResult = ({ data, className = '' }) => {"
new = (
    "/**\n * \u529f\u80fd\uff1a\u5c55\u793a AI \u54c1\u79cd\u8bc6\u522b\u7ed3\u679c\u3002\n"
    " * \u3010\u6743\u9650\u3011\u7531 AddPet \u7b49\u9875\u9762\u5728\u767b\u5f55\u540e\u8c03\u7528\u3002\n */\n"
    + old
)
if old in t:
    t = t.replace(old, new, 1)
bdr.write_text(t, encoding="utf-8")

add = ROOT / "pages" / "AddPet.js"
t = add.read_text(encoding="utf-8")
if "const AddPet = () => {" in t:
    t = t.replace(
        "const AddPet = () => {",
        "/**\n * \u529f\u80fd\uff1a\u6dfb\u52a0\u5ba0\u7269\u6863\u6848\uff0c\u652f\u6301 AI \u54c1\u79cd\u8bc6\u522b\u4e0e\u6587\u6848\u751f\u6210\u3002\n"
        " * \u3010\u6743\u9650\u3011\u521b\u5efa\u9700 admin\u3002\n */\nconst AddPet = () => {",
        1,
    )
for old, new in [
    (
        "  const handlePhotoChange = async (e) => {",
        "  /** \u529f\u80fd\uff1a\u4e0a\u4f20\u7167\u7247\u5e76\u8c03\u7528\u54c1\u79cd\u8bc6\u522b\u3002 */\n  const handlePhotoChange = async (e) => {",
    ),
    (
        "  const handleSubmit = async (e) => {",
        "  /** \u529f\u80fd\uff1a\u63d0\u4ea4\u521b\u5efa\u5ba0\u7269\u6863\u6848\u3002\u3010\u6743\u9650\u3011admin */\n  const handleSubmit = async (e) => {",
    ),
]:
    if old in t:
        t = t.replace(old, new, 1)
add.write_text(t, encoding="utf-8")

adm = ROOT / "pages" / "AdminDashboard.js"
t = adm.read_text(encoding="utf-8")
t = t.replace(
    "const AdminDashboard = () => {",
    "/**\n * \u529f\u80fd\uff1a\u7ba1\u7406\u540e\u53f0\u4e3b\u9875\u3002\u3010\u6743\u9650\u3011\u4ec5 admin\u3002\n */\nconst AdminDashboard = () => {",
    1,
)
for old, new in [
    (
        "  const loadAiLogsData = useCallback(async (page) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1aAI \u65e5\u5fd7 */\n  const loadAiLogsData = useCallback(async (page) => {",
    ),
    (
        "  const loadTabData = useCallback(async (tab) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1a\u5404 Tab \u6570\u636e */\n  const loadTabData = useCallback(async (tab) => {",
    ),
    (
        "  const handleUserUpdate = async (userId, data) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1a\u5c01\u7981/\u6539\u89d2\u8272 */\n  const handleUserUpdate = async (userId, data) => {",
    ),
    (
        "  const handleAudit = async (appId) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1a\u9886\u517b\u5ba1\u6838 */\n  const handleAudit = async (appId) => {",
    ),
    (
        "  const handleConfigSave = async (key) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1a\u5e73\u53f0\u914d\u7f6e\u542b AI \u914d\u989d */\n  const handleConfigSave = async (key) => {",
    ),
    (
        "  const handlePetPatch = async (petId, data) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1a\u4fee\u6539\u5ba0\u7269 */\n  const handlePetPatch = async (petId, data) => {",
    ),
    (
        "  const handlePetDelete = async (petId) => {",
        "  /** \u3010\u6743\u9650\u3011admin\uff1a\u5220\u9664\u5ba0\u7269 */\n  const handlePetDelete = async (petId) => {",
    ),
]:
    if old in t:
        t = t.replace(old, new, 1)
adm.write_text(t, encoding="utf-8")
print("ok")
