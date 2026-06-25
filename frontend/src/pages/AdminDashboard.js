import React, { useCallback, useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { adoptAPI, adminAPI, cmsAPI, petsAPI } from '../api/api';
import CarouselAdminPanel from '../components/CarouselAdminPanel';
import CmsMarkdownEditor from '../components/CmsMarkdownEditor';
import { SITE_NAME, ADOPTION_STATUS, ONLINE_STATUS, ARTICLE_TYPES } from '../constants/site';
import getQuestionnaireEntries, { formatAttachmentType } from '../utils/adoptQuestionnaireDisplay';

const SPECIES_LABELS = {
  dog: '狗',
  cat: '猫',
  bird: '鸟',
  rabbit: '兔',
  fish: '鱼',
  other: '其他',
};

const ROLE_LABELS = {
  admin: '管理员',
  user: '普通用户',
  visitor: '访客',
};

const MODERATION_ACTION_LABELS = {
  approve: '通过',
  hide: '隐藏',
  delete: '删除',
  ban: '封禁',
};

const CONTENT_TYPE_OPTIONS = [
  { value: 'community_post', label: '社区帖子' },
  { value: 'cms_article', label: '资讯文章' },
  { value: 'lost_found_post', label: '报失寻主' },
  { value: 'user', label: '用户' },
];

const CONFIG_LABELS = {
  max_upload_mb: '最大上传文件大小（MB）',
  ai_daily_limit: '每日最大 AI 调用次数',
  ai_total_limit: 'AI 总调用次数上限',
};

const FEATURE_TYPE_LABELS = {
  breed_detect: '品种识别',
  adopt_copy: '领养文案',
  qa_assistant: '智能问答',
};

const AI_LOG_PAGE_SIZE = 20;

const toList = (data) => (Array.isArray(data) ? data : data?.results ?? []);

const getApiError = (err) => {
  const d = err.response?.data;
  if (typeof d === 'string') return d;
  if (d?.detail) return String(d.detail);
  return err.message || '请求失败';
};

const TABS = [
  { key: 'dashboard', label: '数据概览', icon: 'fa-chart-line' },
  { key: 'users', label: '用户管理', icon: 'fa-users' },
  { key: 'adopt', label: '领养审核', icon: 'fa-clipboard-check' },
  { key: 'pets', label: '宠物管理', icon: 'fa-paw' },
  { key: 'cms', label: '资讯管理', icon: 'fa-newspaper' },
  { key: 'moderation', label: '处置记录', icon: 'fa-shield-alt' },
  { key: 'carousel', label: '首页轮播', icon: 'fa-images' },
  { key: 'config', label: '系统配置', icon: 'fa-cog' },
  { key: 'ai-logs', label: 'AI 日志', icon: 'fa-robot' },
];

const KPI_CARDS = [
  { key: 'users', label: '用户', icon: 'fa-users', color: 'primary' },
  { key: 'pets', label: '宠物', icon: 'fa-paw', color: 'success' },
  { key: 'adopt_applications', label: '领养申请', icon: 'fa-heart', color: 'danger' },
  { key: 'rescue_cases', label: '救助案例', icon: 'fa-hand-holding-heart', color: 'warning' },
  { key: 'community_posts', label: '社区帖子', icon: 'fa-comments', color: 'info' },
  { key: 'cms_articles', label: '资讯文章', icon: 'fa-newspaper', color: 'secondary' },
  { key: 'lost_found_posts', label: '寻宠招领', icon: 'fa-search-location', color: 'dark' },
];

const emptyArticleForm = () => ({
  title: '', summary: '', content: '', article_type: 'science', status: 1, is_pinned: false,
});

const AdminDashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [applications, setApplications] = useState([]);
  const [pets, setPets] = useState([]);
  const [articles, setArticles] = useState([]);
  const [moderation, setModeration] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [aiLogs, setAiLogs] = useState([]);
  const [aiLogPage, setAiLogPage] = useState(1);
  const [aiLogTotal, setAiLogTotal] = useState(0);
  const [aiLogStats, setAiLogStats] = useState(null);

  const [auditForm, setAuditForm] = useState({});
  const [modFilter, setModFilter] = useState({ content_type: '', action: '' });
  const [configEdits, setConfigEdits] = useState({});
  const [articleForm, setArticleForm] = useState(emptyArticleForm());
  const [editingArticleId, setEditingArticleId] = useState(null);
  const [showArticleForm, setShowArticleForm] = useState(false);
  const [reviewDetail, setReviewDetail] = useState(null);
  const [reviewLoadingId, setReviewLoadingId] = useState(null);

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && TABS.some((t) => t.key === tab)) setActiveTab(tab);
  }, [searchParams]);

  const loadAiLogsData = useCallback(async (page) => {
    const res = await adminAPI.getAiLogs({ page, page_size: AI_LOG_PAGE_SIZE });
    setAiLogs(toList(res.data));
    setAiLogTotal(res.data?.count ?? 0);
    const statsRes = await adminAPI.getAiLogStats();
    setAiLogStats(statsRes.data);
  }, []);

  const loadTabData = useCallback(async (tab) => {
    setLoading(true);
    setError(null);
    try {
      switch (tab) {
        case 'dashboard': {
          const res = await adminAPI.getDashboard();
          setDashboard(res.data);
          break;
        }
        case 'users': {
          const res = await adminAPI.getUsers();
          setUsers(toList(res.data));
          break;
        }
        case 'adopt': {
          const res = await adoptAPI.getAll();
          setApplications(toList(res.data));
          break;
        }
        case 'pets': {
          const res = await petsAPI.getAll();
          setPets(toList(res.data));
          break;
        }
        case 'cms': {
          const res = await cmsAPI.getArticles();
          setArticles(toList(res.data));
          break;
        }
        case 'moderation': {
          const res = await adminAPI.getModeration();
          setModeration(toList(res.data));
          break;
        }
        case 'config': {
          const res = await adminAPI.getConfig();
          const list = toList(res.data);
          setConfigs(list);
          const edits = {};
          list.forEach((c) => { edits[c.config_key] = c.config_value; });
          setConfigEdits(edits);
          try {
            const statsRes = await adminAPI.getAiLogStats();
            setAiLogStats(statsRes.data);
          } catch {
            /* optional stats */
          }
          break;
        }
        default:
          break;
      }
    } catch (err) {
      const msg = getApiError(err);
      setError(err.response?.status === 403
        ? `权限不足：${msg}（请确认账号为管理员或运行 fix_admin_roles）`
        : `加载失败：${msg}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'ai-logs') {
      setLoading(true);
      setError(null);
      loadAiLogsData(aiLogPage)
        .catch((err) => {
          const msg = getApiError(err);
          setError(`加载失败：${msg}`);
          console.error(err);
        })
        .finally(() => setLoading(false));
      return;
    }
    loadTabData(activeTab);
  }, [activeTab, aiLogPage, loadTabData, loadAiLogsData]);

  const handleUserUpdate = async (userId, data) => {
    try {
      const res = await adminAPI.updateUser(userId, data);
      setUsers((prev) => prev.map((u) => (u.id === userId ? res.data : u)));
    } catch (err) {
      alert(getApiError(err) || '更新失败');
      console.error(err);
    }
  };

  const loadReviewDetail = async (appId) => {
    if (reviewDetail?.id === appId) {
      setReviewDetail(null);
      return;
    }
    setReviewLoadingId(appId);
    try {
      const res = await adoptAPI.getReviewDetail(appId);
      setReviewDetail(res.data);
    } catch (err) {
      alert(getApiError(err) || '加载申请详情失败');
      console.error(err);
    } finally {
      setReviewLoadingId(null);
    }
  };

  const getAuditFormForApp = (appId) => ({
    online_status: 'approved',
    audit_opinion: '',
    ...(auditForm[appId] || {}),
  });

  const handleAudit = async (appId) => {
    const form = getAuditFormForApp(appId);
    if (!form.online_status) {
      alert('请选择审核结果');
      return;
    }
    try {
      await adoptAPI.audit(appId, form);
      setReviewDetail(null);
      loadTabData('adopt');
    } catch (err) {
      alert(getApiError(err) || '审核失败');
      console.error(err);
    }
  };

  const handleConfigSave = async (key) => {
    try {
      await adminAPI.updateConfig(key, { config_value: configEdits[key] });
      alert('配置已保存');
      loadTabData('config');
    } catch (err) {
      alert('保存失败');
      console.error(err);
    }
  };

  const handlePetPatch = async (petId, data) => {
    try {
      await petsAPI.update(petId, data);
      loadTabData('pets');
    } catch (err) {
      alert(getApiError(err));
    }
  };

  const handlePetDelete = async (petId) => {
    if (!window.confirm('确定删除该宠物档案？')) return;
    try {
      await petsAPI.delete(petId);
      loadTabData('pets');
    } catch (err) {
      alert(getApiError(err));
    }
  };

  const openArticleEditor = (article) => {
    if (article) {
      setEditingArticleId(article.id);
      setArticleForm({
        title: article.title || '',
        summary: article.summary || '',
        content: article.content || '',
        article_type: article.article_type || 'science',
        status: article.status ?? 1,
        is_pinned: !!article.is_pinned,
      });
    } else {
      setEditingArticleId(null);
      setArticleForm(emptyArticleForm());
    }
    setShowArticleForm(true);
  };

  const handleArticleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingArticleId) {
        await cmsAPI.updateArticle(editingArticleId, articleForm);
      } else {
        await cmsAPI.createArticle(articleForm);
      }
      setShowArticleForm(false);
      loadTabData('cms');
    } catch (err) {
      alert(getApiError(err));
    }
  };

  const handleArticleStatus = async (id, status) => {
    try {
      await cmsAPI.updateArticle(id, { status });
      loadTabData('cms');
    } catch (err) {
      alert(getApiError(err));
    }
  };

  const handleArticlePin = async (id, isPinned) => {
    try {
      await cmsAPI.updateArticle(id, { is_pinned: isPinned });
      loadTabData('cms');
    } catch (err) {
      alert(getApiError(err));
    }
  };

  const switchTab = (key) => {
    if (key === 'ai-logs') setAiLogPage(1);
    setActiveTab(key);
    setSearchParams({ tab: key });
  };

  const formatLimit = (used, limit) => {
    if (!limit || limit <= 0) return `${used} / 不限制`;
    return `${used} / ${limit}`;
  };

  const aiLogTotalPages = Math.max(1, Math.ceil(aiLogTotal / AI_LOG_PAGE_SIZE));

  const renderDashboard = () => (
    <div>
      <div className="row g-3 mb-4">
        {KPI_CARDS.map((card) => (
          <div key={card.key} className="col-md-4 col-lg-3">
            <div className={`card border-${card.color} h-100`}>
              <div className="card-body text-center">
                <i className={`fas ${card.icon} fa-2x text-${card.color} mb-2`}></i>
                <h3 className="mb-0">{dashboard?.[card.key] ?? '-'}</h3>
                <small className="text-muted">{card.label}</small>
              </div>
            </div>
          </div>
        ))}
      </div>
      {dashboard?.adopt_by_status?.length > 0 && (
        <div className="card">
          <div className="card-header">领养申请状态分布</div>
          <div className="card-body">
            <div className="d-flex flex-wrap gap-2">
              {dashboard.adopt_by_status.map((item) => (
                <span key={item.online_status} className="badge bg-secondary fs-6">
                  {ONLINE_STATUS[item.online_status] || item.online_status}：{item.count}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderUsers = () => (
    <div className="table-responsive">
      <table className="table table-hover">
        <thead>
          <tr>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>{ROLE_LABELS[user.profile?.role] || user.profile?.role || '-'}</td>
              <td>{user.profile?.status === 1 ? '已封禁' : '正常'}</td>
              <td>
                <div className="btn-group btn-group-sm">
                  <button type="button" className="btn btn-outline-success" disabled={user.profile?.status !== 1} onClick={() => handleUserUpdate(user.id, { status: 0 })}>解封</button>
                  <button type="button" className="btn btn-outline-danger" disabled={user.profile?.status === 1} onClick={() => handleUserUpdate(user.id, { status: 1 })}>封禁</button>
                  <button
                    type="button"
                    className="btn btn-outline-primary"
                    disabled={user.profile?.role === 'admin'}
                    onClick={() => handleUserUpdate(user.id, { role: 'admin' })}
                  >
                    {user.profile?.role === 'admin' ? '已为管理员' : '设为管理员'}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderQuestionnairePreview = (answers) => {
    const entries = getQuestionnaireEntries(answers);
    if (!entries.length) return <span className="text-muted">无问卷数据</span>;
    return (
      <dl className="row mb-0 small">
        {entries.map(({ key, label, value }) => (
          <React.Fragment key={key}>
            <dt className="col-sm-4 text-muted">{label}</dt>
            <dd className="col-sm-8">{value}</dd>
          </React.Fragment>
        ))}
      </dl>
    );
  };

  const normalizeQuestionnaire = (rawQuestionnaire) => {
    if (!rawQuestionnaire) return null;
    if (typeof rawQuestionnaire === 'object') return rawQuestionnaire;
    if (typeof rawQuestionnaire === 'string') {
      try {
        const parsed = JSON.parse(rawQuestionnaire);
        return parsed && typeof parsed === 'object' ? parsed : null;
      } catch {
        return null;
      }
    }
    return null;
  };

  const renderAdoptAudit = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <p className="text-muted small mb-0">共 {applications.length} 条申请，点击「查看详情」可查看问卷与附件。</p>
        <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => loadTabData('adopt')}>
          <i className="fas fa-redo me-1"></i>刷新
        </button>
      </div>
      {applications.length === 0 ? (
        <div className="alert alert-light text-center mb-0">暂无领养申请记录</div>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>申请人</th>
                <th>宠物</th>
                <th>留言</th>
                <th>材料</th>
                <th>状态</th>
                <th>申请时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => {
                const isExpanded = reviewDetail?.id === app.id;
                const questionnaireData = isExpanded ? normalizeQuestionnaire(reviewDetail?.questionnaire) : null;
                return (
                  <React.Fragment key={app.id}>
                    <tr>
                      <td>{app.id}</td>
                      <td>{app.applicant?.username}</td>
                      <td>{app.pet?.name || app.pet_id}</td>
                      <td style={{ maxWidth: 140 }} className="text-truncate" title={app.message}>{app.message || '-'}</td>
                      <td>
                        {app.has_questionnaire ? <span className="badge bg-info text-dark me-1">问卷</span> : null}
                        {(app.attachment_count || 0) > 0 ? <span className="badge bg-secondary">附件 {app.attachment_count}</span> : null}
                        {!app.has_questionnaire && !(app.attachment_count > 0) ? <span className="text-muted small">待补充</span> : null}
                      </td>
                      <td><span className="badge bg-secondary">{ONLINE_STATUS[app.online_status] || app.online_status}</span></td>
                      <td><small>{app.created_at ? new Date(app.created_at).toLocaleString() : '-'}</small></td>
                      <td>
                        <button
                          type="button"
                          className="btn btn-outline-primary btn-sm mb-1"
                          onClick={() => loadReviewDetail(app.id)}
                          disabled={reviewLoadingId === app.id}
                        >
                          {reviewLoadingId === app.id ? '加载中...' : (isExpanded ? '收起详情' : '查看详情')}
                        </button>
                        {app.online_status === 'pending' ? (
                          <div className="d-flex flex-column gap-1 mt-1" style={{ minWidth: 200 }}>
                            <select
                              className="form-select form-select-sm"
                              value={getAuditFormForApp(app.id).online_status}
                              onChange={(e) => setAuditForm({
                                ...auditForm,
                                [app.id]: { ...getAuditFormForApp(app.id), online_status: e.target.value },
                              })}
                            >
                              <option value="approved">通过</option>
                              <option value="rejected">拒绝</option>
                              <option value="need_material">需补材料</option>
                            </select>
                            <input
                              type="text"
                              className="form-control form-control-sm"
                              placeholder="审核意见"
                              value={getAuditFormForApp(app.id).audit_opinion}
                              onChange={(e) => setAuditForm({
                                ...auditForm,
                                [app.id]: { ...getAuditFormForApp(app.id), audit_opinion: e.target.value },
                              })}
                            />
                            <button type="button" className="btn btn-success btn-sm" onClick={() => handleAudit(app.id)}>提交审核</button>
                          </div>
                        ) : (
                          <small className="text-muted d-block">{app.audit_opinion || '已审核'}</small>
                        )}
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr className="table-light">
                        <td colSpan={8}>
                          <div className="py-2">
                            <p className="mb-2"><strong>申请人：</strong>{reviewDetail.applicant?.username} {reviewDetail.applicant_phone_masked ? `（${reviewDetail.applicant_phone_masked}）` : ''}</p>
                            <p className="mb-2"><strong>宠物：</strong>{reviewDetail.pet?.name || '-'}</p>
                            <p className="mb-3"><strong>留言：</strong>{reviewDetail.message || '-'}</p>
                            <h6>问卷回答</h6>
                            <div className="mb-3">{renderQuestionnairePreview(questionnaireData)}</div>
                            <h6>附件</h6>
                            {reviewDetail.attachments?.length ? (
                              <ul className="list-unstyled mb-0">
                                {reviewDetail.attachments.map((att) => (
                                  <li key={att.id} className="mb-1">
                                    <a href={att.file_url} target="_blank" rel="noopener noreferrer">{formatAttachmentType(att.file_type)}</a>
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="text-muted small mb-0">暂无附件</p>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderPets = () => (
    <div>
      <div className="mb-3">
        <Link to="/add-pet" className="btn btn-success btn-sm">新建宠物档案</Link>
      </div>
      <div className="row">
        {pets.map((pet) => (
          <div key={pet.id} className="col-md-4 mb-3">
            <div className="card h-100">
              <div className="card-body text-center">
                <h6>{pet.name || SPECIES_LABELS[pet.species] || pet.species}</h6>
                <small className="text-muted d-block mb-2">
                  {SPECIES_LABELS[pet.species] || pet.species} · {ADOPTION_STATUS[pet.adoption_status] || pet.adoption_status}
                  <br />公开：{pet.is_public ? '是' : '否'}
                </small>
                <div className="d-flex flex-wrap gap-1 justify-content-center">
                  <Link to={`/pets/${pet.id}`} className="btn btn-outline-secondary btn-sm">前台</Link>
                  <button type="button" className="btn btn-outline-primary btn-sm" onClick={() => handlePetPatch(pet.id, { is_public: !pet.is_public })}>
                    {pet.is_public ? '隐藏' : '公开'}
                  </button>
                  <button type="button" className="btn btn-outline-warning btn-sm" onClick={() => handlePetPatch(pet.id, { adoption_status: 'available' })}>可领养</button>
                  <button type="button" className="btn btn-outline-danger btn-sm" onClick={() => handlePetDelete(pet.id)}>删除</button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCms = () => (
    <div>
      <button type="button" className="btn btn-success btn-sm mb-3" onClick={() => openArticleEditor(null)}>新建文章</button>
      {showArticleForm && (
        <form className="card mb-3" onSubmit={handleArticleSave}>
          <div className="card-body row g-2">
            <div className="col-md-6"><input className="form-control" placeholder="标题" value={articleForm.title} onChange={(e) => setArticleForm({ ...articleForm, title: e.target.value })} required /></div>
            <div className="col-md-3">
              <select className="form-select" value={articleForm.article_type} onChange={(e) => setArticleForm({ ...articleForm, article_type: e.target.value })}>
                {Object.entries(ARTICLE_TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="col-md-3">
              <select className="form-select" value={articleForm.status} onChange={(e) => setArticleForm({ ...articleForm, status: Number(e.target.value) })}>
                <option value={0}>草稿</option>
                <option value={1}>已发布</option>
                <option value={2}>已下线</option>
              </select>
            </div>
            <div className="col-12"><input className="form-control" placeholder="摘要" value={articleForm.summary} onChange={(e) => setArticleForm({ ...articleForm, summary: e.target.value })} /></div>
            <div className="col-12">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="articlePinned"
                  checked={!!articleForm.is_pinned}
                  onChange={(e) => setArticleForm({ ...articleForm, is_pinned: e.target.checked })}
                />
                <label className="form-check-label" htmlFor="articlePinned">置顶</label>
              </div>
            </div>
            <CmsMarkdownEditor value={articleForm.content} onChange={(v) => setArticleForm({ ...articleForm, content: v })} />
            <div className="col-12">
              <button type="submit" className="btn btn-primary btn-sm me-2">保存</button>
              <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setShowArticleForm(false)}>取消</button>
            </div>
          </div>
        </form>
      )}
      <div className="table-responsive">
        <table className="table table-hover">
          <thead>
            <tr><th>标题</th><th>类型</th><th>状态</th><th>操作</th></tr>
          </thead>
          <tbody>
            {articles.map((article) => (
              <tr key={article.id}>
                <td>
                  <Link to={`/cms/${article.id}`}>{article.title}</Link>
                  {article.is_pinned && <span className="badge bg-warning text-dark ms-1">置顶</span>}
                </td>
                <td>{ARTICLE_TYPES[article.article_type] || article.article_type}</td>
                <td>{article.status === 1 ? '已发布' : article.status === 0 ? '草稿' : '已下线'}</td>
                <td>
                  <div className="btn-group btn-group-sm">
                    <button
                      type="button"
                      className={`btn ${article.is_pinned ? 'btn-warning' : 'btn-outline-secondary'}`}
                      onClick={() => handleArticlePin(article.id, !article.is_pinned)}
                    >
                      {article.is_pinned ? '取消置顶' : '置顶'}
                    </button>
                    <button type="button" className="btn btn-outline-primary" onClick={() => openArticleEditor(article)}>编辑</button>
                    {article.status !== 1 && <button type="button" className="btn btn-outline-success" onClick={() => handleArticleStatus(article.id, 1)}>发布</button>}
                    {article.status === 1 && <button type="button" className="btn btn-outline-warning" onClick={() => handleArticleStatus(article.id, 2)}>下线</button>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const filteredModeration = moderation.filter((item) => {
    if (modFilter.content_type && item.content_type !== modFilter.content_type) return false;
    if (modFilter.action && item.action !== modFilter.action) return false;
    return true;
  });

  const renderModeration = () => (
    <div>
      <div className="row g-2 mb-3">
        <div className="col-md-4">
          <select
            className="form-select form-select-sm"
            value={modFilter.content_type}
            onChange={(e) => setModFilter({ ...modFilter, content_type: e.target.value })}
          >
            <option value="">全部内容类型</option>
            {CONTENT_TYPE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div className="col-md-4">
          <select
            className="form-select form-select-sm"
            value={modFilter.action}
            onChange={(e) => setModFilter({ ...modFilter, action: e.target.value })}
          >
            <option value="">全部操作</option>
            {Object.entries(MODERATION_ACTION_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      </div>
      <p className="text-muted small">处置记录由前台管理模式自动写入，此处仅可查看。</p>
      <div className="table-responsive">
        <table className="table table-hover">
          <thead>
            <tr>
              <th>时间</th>
              <th>操作人</th>
              <th>内容类型</th>
              <th>目标</th>
              <th>操作</th>
              <th>原因</th>
            </tr>
          </thead>
          <tbody>
            {filteredModeration.map((item) => (
              <tr key={item.id}>
                <td>{new Date(item.created_at).toLocaleString()}</td>
                <td>{item.operator?.username || '-'}</td>
                <td>{CONTENT_TYPE_OPTIONS.find((o) => o.value === item.content_type)?.label || item.content_type}</td>
                <td>
                  #{item.content_id}
                  {item.target_summary ? <small className="text-muted d-block">{item.target_summary}</small> : null}
                </td>
                <td><span className="badge bg-warning text-dark">{MODERATION_ACTION_LABELS[item.action] || item.action}</span></td>
                <td>{item.reason || '-'}</td>
              </tr>
            ))}
            {filteredModeration.length === 0 && (
              <tr><td colSpan={6} className="text-muted text-center">暂无处置记录</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderConfig = () => (
    <div>
      {aiLogStats && (
        <div className="alert alert-secondary py-2 small mb-3">
          <strong>AI 调用用量：</strong>
          今日 {formatLimit(aiLogStats.today_count, aiLogStats.daily_limit)}
          {' · '}
          累计 {formatLimit(aiLogStats.total_count, aiLogStats.total_limit)}
          <span className="text-muted ms-2">（0 表示不限制，可在下方配置）</span>
        </div>
      )}
      <div className="list-group">
        {configs.map((cfg) => {
          const isNumeric = cfg.config_key.endsWith('_limit') || cfg.config_key.endsWith('_mb');
          return (
            <div key={cfg.config_key} className="list-group-item">
              <div className="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <strong>{CONFIG_LABELS[cfg.config_key] || cfg.config_key}</strong>
                  <small className="text-muted d-block">{cfg.config_key}</small>
                  {cfg.description && <small className="text-muted d-block">{cfg.description}</small>}
                </div>
              </div>
              <div className="input-group">
                <input
                  type={isNumeric ? 'number' : 'text'}
                  min={isNumeric ? '0' : undefined}
                  className="form-control"
                  value={configEdits[cfg.config_key] ?? ''}
                  onChange={(e) => setConfigEdits({ ...configEdits, [cfg.config_key]: e.target.value })}
                />
                <button type="button" className="btn btn-success" onClick={() => handleConfigSave(cfg.config_key)}>保存</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderAiLogs = () => (
    <div>
      <div className="alert alert-info small">
        AI 日志用于审计平台三大 AI 功能：<strong>品种识别</strong>、<strong>领养文案生成</strong>、<strong>智能养宠问答</strong>。
        记录调用用户、成功与否、请求摘要与时间，便于排查故障与统计用量。限额在「系统配置」中设置。
      </div>
      {aiLogStats && (
        <p className="text-muted small mb-3">
          今日用量 {formatLimit(aiLogStats.today_count, aiLogStats.daily_limit)}
          {' · '}
          累计用量 {formatLimit(aiLogStats.total_count, aiLogStats.total_limit)}
        </p>
      )}
      <div className="table-responsive">
        <table className="table table-hover table-sm">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户</th>
              <th>功能</th>
              <th>成功</th>
              <th>请求</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            {aiLogs.map((log) => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>{log.user?.username || log.user}</td>
                <td>{FEATURE_TYPE_LABELS[log.feature_type] || log.feature_type}</td>
                <td>{log.success ? '是' : '否'}</td>
                <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }} title={log.request_meta}>{log.request_meta}</td>
                <td>{new Date(log.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {aiLogs.length === 0 && (
              <tr><td colSpan={6} className="text-muted text-center">暂无 AI 调用记录</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {aiLogTotalPages > 1 && (
        <nav className="d-flex justify-content-between align-items-center mt-3">
          <small className="text-muted">共 {aiLogTotal} 条，第 {aiLogPage} / {aiLogTotalPages} 页</small>
          <ul className="pagination pagination-sm mb-0">
            <li className={`page-item${aiLogPage <= 1 ? ' disabled' : ''}`}>
              <button type="button" className="page-link" onClick={() => setAiLogPage((p) => Math.max(1, p - 1))}>上一页</button>
            </li>
            <li className={`page-item${aiLogPage >= aiLogTotalPages ? ' disabled' : ''}`}>
              <button type="button" className="page-link" onClick={() => setAiLogPage((p) => Math.min(aiLogTotalPages, p + 1))}>下一页</button>
            </li>
          </ul>
        </nav>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard': return renderDashboard();
      case 'users': return renderUsers();
      case 'adopt': return renderAdoptAudit();
      case 'pets': return renderPets();
      case 'cms': return renderCms();
      case 'moderation': return renderModeration();
      case 'carousel': return <CarouselAdminPanel />;
      case 'config': return renderConfig();
      case 'ai-logs': return renderAiLogs();
      default: return null;
    }
  };

  return (
    <div className="py-3">
      <h2 className="mb-4"><i className="fas fa-cog me-2"></i>{SITE_NAME} 管理后台</h2>

      <div className="row">
        <div className="col-md-3 col-lg-2">
          <div className="list-group mb-4">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                type="button"
                className={`list-group-item list-group-item-action ${activeTab === tab.key ? 'active' : ''}`}
                onClick={() => switchTab(tab.key)}
              >
                <i className={`fas ${tab.icon} me-2`}></i>{tab.label}
              </button>
            ))}
          </div>
        </div>
        <div className="col-md-9 col-lg-10">
          {error && <div className="alert alert-danger">{error}</div>}
          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">加载中...</span>
              </div>
            </div>
          ) : (
            <div className="card shadow-sm">
              <div className="card-header">
                <h5 className="mb-0">{TABS.find((t) => t.key === activeTab)?.label}</h5>
              </div>
              <div className="card-body">{renderTabContent()}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
