<<<<<<< HEAD
import React, { useCallback, useEffect, useState } from 'react';
=======
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Carousel } from 'bootstrap';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
import { Link } from 'react-router-dom';
import { aiAPI, portalAPI, uploadAPI } from '../api/api';
import BreedDetectResult from '../components/BreedDetectResult';
import { SITE_NAME } from '../constants/site';
import birdImg from '../Photo/bird.webp';
import catImg from '../Photo/cat.webp';
import dogImg from '../Photo/dog.webp';
import fishImg from '../Photo/fish.webp';
import rabbitImg from '../Photo/rabbit.jpeg';

<<<<<<< HEAD
=======
const toList = (data) => (Array.isArray(data) ? data : data?.results ?? []);

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
const STATS_CONFIG = [
  { key: 'total_rescued', label: '累计救助', icon: 'fa-check-circle', color: 'success' },
  { key: 'total_adopted', label: '累计领养', icon: 'fa-home', color: 'primary' },
  { key: 'searching_count', label: '正在寻找', icon: 'fa-search', color: 'danger' },
  { key: 'today_reported', label: '今日上报', icon: 'fa-flag', color: 'warning' },
];

const PET_CATEGORIES = [
  { name: '猫', image: catImg, link: '/pets?type=cat' },
  { name: '狗', image: dogImg, link: '/pets?type=dog' },
  { name: '鸟', image: birdImg, link: '/pets?type=bird' },
  { name: '兔', image: rabbitImg, link: '/pets?type=rabbit' },
  { name: '鱼', image: fishImg, link: '/pets?type=fish' },
];

const Home = () => {
  const [carouselItems, setCarouselItems] = useState([]);
  const [carouselLoading, setCarouselLoading] = useState(true);
<<<<<<< HEAD
=======
  const carouselRef = useRef(null);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const [aiImageUrl, setAiImageUrl] = useState('');
  const [aiDesc, setAiDesc] = useState('');
  const [aiDetectData, setAiDetectData] = useState(null);
  const [aiError, setAiError] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);

  const [dashboard, setDashboard] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState(false);

  const normalizeCarouselTitle = (title) => {
    if (!title) return '';
    const t = String(title).trim();
    if (/welcome\s*to\s*adoption/i.test(t)) return '欢迎领养';
    return t;
  };

  useEffect(() => {
    const fetchCarousel = async () => {
      try {
        const response = await portalAPI.getCarousel();
<<<<<<< HEAD
        const items = (response.data || []).map((item) => ({
=======
        const items = toList(response.data).map((item) => ({
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
          ...item,
          title: normalizeCarouselTitle(item.title),
        }));
        setCarouselItems(items);
      } catch (err) {
        console.error('Error fetching carousel:', err);
      } finally {
        setCarouselLoading(false);
      }
    };
    fetchCarousel();
  }, []);

<<<<<<< HEAD
=======
  // 轮播是异步渲染的，Bootstrap 的 data-bs-ride 不会自动初始化，故手动启用自动轮播
  useEffect(() => {
    if (carouselLoading || carouselItems.length === 0 || !carouselRef.current) return undefined;
    const instance = Carousel.getOrCreateInstance(carouselRef.current, { interval: 5000, ride: 'carousel' });
    instance.cycle();
    return () => {
      try { instance.dispose(); } catch (e) { /* element already unmounted */ }
    };
  }, [carouselLoading, carouselItems]);

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    setStatsError(false);
    try {
      const res = await portalAPI.getStats();
      setStats(res.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setStatsError(true);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const fetchDashboard = useCallback(async () => {
    setDashboardLoading(true);
    setDashboardError(false);
    try {
      const res = await portalAPI.getDashboard();
      setDashboard(res.data);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setDashboardError(true);
    } finally {
      setDashboardLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return (
    <div>
      {/* 轮播图 */}
      {!carouselLoading && carouselItems.length > 0 && (
<<<<<<< HEAD
        <div id="homeCarousel" className="carousel slide mb-4" data-bs-ride="carousel">
=======
        <div id="homeCarousel" ref={carouselRef} className="carousel slide mb-4">
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
          <div className="carousel-indicators">
            {carouselItems.map((item, index) => (
              <button
                key={item.id}
                type="button"
                data-bs-target="#homeCarousel"
                data-bs-slide-to={index}
                className={index === 0 ? 'active' : ''}
                aria-current={index === 0 ? 'true' : undefined}
                aria-label={`第 ${index + 1} 张`}
              ></button>
            ))}
          </div>
          <div className="carousel-inner rounded-3 overflow-hidden shadow">
            {carouselItems.map((item, index) => (
              <div key={item.id} className={`carousel-item ${index === 0 ? 'active' : ''}`}>
                {item.link_url ? (
                  item.link_url.startsWith('http') ? (
                    <a href={item.link_url} target="_blank" rel="noopener noreferrer">
                      <img src={item.image_url} className="d-block w-100" alt={item.title || '轮播图'} style={{ maxHeight: '400px', objectFit: 'cover' }} />
                    </a>
                  ) : (
                    <Link to={item.link_url}>
                      <img src={item.image_url} className="d-block w-100" alt={item.title || '轮播图'} style={{ maxHeight: '400px', objectFit: 'cover' }} />
                    </Link>
                  )
                ) : (
                  <img src={item.image_url} className="d-block w-100" alt={item.title || '轮播图'} style={{ maxHeight: '400px', objectFit: 'cover' }} />
                )}
                {item.title && (
                  <div className="carousel-caption d-none d-md-block">
                    <h5>{item.title}</h5>
                  </div>
                )}
              </div>
            ))}
          </div>
          <button className="carousel-control-prev" type="button" data-bs-target="#homeCarousel" data-bs-slide="prev">
            <span className="carousel-control-prev-icon" aria-hidden="true"></span>
            <span className="visually-hidden">上一张</span>
          </button>
          <button className="carousel-control-next" type="button" data-bs-target="#homeCarousel" data-bs-slide="next">
            <span className="carousel-control-next-icon" aria-hidden="true"></span>
            <span className="visually-hidden">下一张</span>
          </button>
        </div>
      )}

      {/* 核心数据统计 */}
      <div className="container py-4">
        <h4 className="text-center mb-4">
          <i className="fas fa-chart-bar me-2 text-success"></i>
          平台数据概览
        </h4>
        {statsLoading ? (
          <div className="text-center py-3">
            <div className="spinner-border spinner-border-sm text-success" role="status"></div>
            <span className="ms-2 text-muted small">加载统计数据...</span>
          </div>
        ) : statsError ? (
          <div className="text-center py-3">
            <span className="text-muted small">统计数据加载失败</span>
            <button className="btn btn-sm btn-outline-secondary ms-2" onClick={fetchStats}>
              <i className="fas fa-redo me-1"></i>重试</button>
          </div>
        ) : stats ? (
          <div className="row g-3 justify-content-center">
            {STATS_CONFIG.map((item) => (
              <div key={item.key} className="col-md-2 col-4">
                <div className={`card border-${item.color} text-center h-100 shadow-sm`}>
                  <div className="card-body py-3">
                    <i className={`fas ${item.icon} fa-2x text-${item.color} mb-2`}></i>
                    <h3 className="mb-0 fw-bold">{stats[item.key] ?? '-'}</h3>
                    <small className="text-muted">{item.label}</small>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {/* 最新聚合动态 */}
      <div className="container py-4">
        <h4 className="text-center mb-4">
          <i className="fas fa-bolt me-2 text-warning"></i>
          最新动态
        </h4>
        {dashboardLoading ? (
          <div className="text-center py-4">
            <div className="spinner-border spinner-border-sm text-warning" role="status"></div>
            <span className="ms-2 text-muted small">加载最新动态...</span>
          </div>
        ) : dashboardError ? (
          <div className="text-center py-4">
            <span className="text-muted small">动态加载失败</span>
            <button className="btn btn-sm btn-outline-secondary ms-2" onClick={fetchDashboard}>
              <i className="fas fa-redo me-1"></i>重新加载</button>
          </div>
        ) : dashboard ? (
          <div className="row g-4">
            {/* 紧急寻主 */}
            <div className="col-md-4">
              <div className="card shadow-sm h-100">
                <div className="card-header bg-danger text-white">
                  <i className="fas fa-exclamation-triangle me-2"></i>紧急寻主
                </div>
                <div className="card-body">
                  {dashboard.urgent_lost?.length > 0 ? (
                    <ul className="list-unstyled mb-0">
                      {dashboard.urgent_lost.map((item) => (
                        <li key={item.id} className="mb-2 pb-2 border-bottom">
                          <Link to={`/lost-found/${item.id}`} className="text-decoration-none">
                            <small className="d-block text-truncate fw-medium">
                              {item.pet_species} - {item.address_text}
                            </small>
                          </Link>
                          <small className="text-muted">
                            {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                            {item.reward_amount > 0 && (
                              <span className="badge bg-warning text-dark ms-1">悬赏 ¥{item.reward_amount}</span>
                            )}
                          </small>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted small mb-0">暂无报失信息</p>
                  )}
                  <Link to="/lost-found" className="btn btn-outline-danger btn-sm mt-2 w-100">
                    查看全部 <i className="fas fa-arrow-right ms-1"></i>
                  </Link>
                </div>
              </div>
            </div>

            {/* 科普文章 */}
            <div className="col-md-4">
              <div className="card shadow-sm h-100">
                <div className="card-header bg-success text-white">
                  <i className="fas fa-graduation-cap me-2"></i>科普文章
                </div>
                <div className="card-body">
                  {dashboard.science_articles?.length > 0 ? (
                    <ul className="list-unstyled mb-0">
                      {dashboard.science_articles.map((item) => (
                        <li key={item.id} className="mb-2 pb-2 border-bottom">
                          <Link to={`/cms/${item.id}`} className="text-decoration-none">
                            <small className="d-block text-truncate fw-medium">{item.title}</small>
                          </Link>
                          <small className="text-muted">
                            {item.published_at ? new Date(item.published_at).toLocaleDateString() : ''}
                          </small>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted small mb-0">暂无科普文章</p>
                  )}
                  <Link to="/cms?type=science" className="btn btn-outline-success btn-sm mt-2 w-100">
                    查看更多 <i className="fas fa-arrow-right ms-1"></i>
                  </Link>
                </div>
              </div>
            </div>

            {/* 最新公告 */}
            <div className="col-md-4">
              <div className="card shadow-sm h-100">
                <div className="card-header bg-warning text-dark">
                  <i className="fas fa-bullhorn me-2"></i>最新公告
                </div>
                <div className="card-body">
                  {dashboard.announcements?.length > 0 ? (
                    <ul className="list-unstyled mb-0">
                      {dashboard.announcements.map((item) => (
                        <li key={item.id} className="mb-2 pb-2 border-bottom">
                          <Link to={`/cms/${item.id}`} className="text-decoration-none">
                            <small className="d-block text-truncate fw-medium">{item.title}</small>
                          </Link>
                          <small className="text-muted">
                            {item.published_at ? new Date(item.published_at).toLocaleDateString() : ''}
                          </small>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted small mb-0">暂无公告</p>
                  )}
                  <Link to="/cms?type=announcement" className="btn btn-outline-warning btn-sm mt-2 w-100">
                    查看全部公告 <i className="fas fa-arrow-right ms-1"></i>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Hero 区域 */}
      <div className="hero-section text-center py-5 position-relative">
        <div className="hero-background">
          <div className="floating-pets">
            <i className="fas fa-paw pet-float-1"></i>
            <i className="fas fa-bone pet-float-2"></i>
            <i className="fas fa-dog pet-float-3"></i>
            <i className="fas fa-cat pet-float-4"></i>
            <i className="fas fa-heart pet-float-5"></i>
          </div>
        </div>

        <div className="container position-relative z-2">
          <h1 className="display-4 fw-bold mb-4">
            <span className="text-dark">寻找你的</span>
            <br />
            <span className="text-warning">完美宠物伙伴</span>
          </h1>
          <p className="lead mb-5 text-muted">
            {SITE_NAME} 连接爱心人士与待领养宠物，参与流浪动物救助，共建温暖的人宠社区。
          </p>
          <div className="d-flex justify-content-center gap-3 mb-5 flex-wrap">
            <Link to="/pets" className="btn btn-success btn-lg px-4 py-3 shadow hero-btn">
              <i className="fas fa-search me-2 btn-icon"></i>
              浏览宠物
            </Link>
            <Link to="/register" className="btn btn-outline-secondary btn-lg px-4 py-3 shadow hero-btn">
              <i className="fas fa-users me-2 btn-icon"></i>
              加入社区
            </Link>
          </div>
        </div>
      </div>

      {/* AI 品种识别 */}
      <div className="container py-4">
        <div className="card shadow-sm border-success">
          <div className="card-body">
            <h4 className="card-title"><i className="fas fa-robot me-2 text-success" />AI 品种识别</h4>
            <p className="text-muted small">上传宠物照片后，将使用基于 Oxford-IIIT Pet 等公开数据集训练的本地 CNN 模型识别品种（Top 候选与置信度）。</p>
            <div className="row g-2 align-items-end">
              <div className="col-md-4">
                <label className="form-label small">上传图片</label>
                <input type="file" className="form-control form-control-sm" accept="image/*" onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  try {
                    const res = await uploadAPI.upload(file, 'ai');
                    setAiImageUrl(res.data.url);
                  } catch {
                    alert('上传失败');
                  }
                }} />
              </div>
              <div className="col-md-5">
                <label className="form-label small">文字描述（可选）</label>
                <input className="form-control form-control-sm" value={aiDesc} onChange={(e) => setAiDesc(e.target.value)} placeholder="如：橙色短毛、绿眼睛" />
              </div>
              <div className="col-md-3">
                <button type="button" className="btn btn-success w-100" disabled={aiLoading} onClick={async () => {
                  if (!localStorage.getItem('token')) { alert('请先登录'); return; }
                  if (!aiImageUrl) { alert('请先上传图片'); return; }
                  setAiLoading(true);
                  setAiDetectData(null);
                  setAiError('');
                  try {
                    const res = await aiAPI.breedDetect({ image_url: aiImageUrl, description: aiDesc });
                    setAiDetectData({
                      species: res.data.species,
                      breed: res.data.breed,
                      summary: res.data.summary,
                      result: res.data.result,
                      confidence: res.data.confidence,
                      breed_candidates: res.data.breed_candidates,
                      low_confidence: res.data.low_confidence,
                    });
                  } catch (err) {
                    let msg = err.response?.data?.detail;
                    if (err.code === 'ECONNABORTED') {
                      msg = '识别超时，请稍后重试（AI 分析约需 10–30 秒）';
                    } else if (!msg) {
                      msg = err.message || '识别失败，请确认已登录且后端已启动';
                    }
                    setAiError(msg);
                  } finally {
                    setAiLoading(false);
                  }
                }}>
                  {aiLoading ? '识别中...' : '开始识别'}
                </button>
              </div>
            </div>
            {aiError && (
              <div className="alert alert-danger mt-3 mb-0 small">{aiError}</div>
            )}
            {aiDetectData && (
              <div className="alert alert-success mt-3 mb-0">
                <BreedDetectResult data={aiDetectData} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 宠物分类 */}
      <div className="pet-categories-section py-5">
        <div className="container">
          <h3 className="text-center mb-5">浏览宠物分类</h3>
          <div className="row justify-content-center">
            {PET_CATEGORIES.map((category, index) => (
              <div key={index} className="col-md-2 col-4 col-6 mb-4 text-center">
                <Link to={category.link} className="text-decoration-none">
                  <div className="pet-category-circle">
                    <img
                      src={category.image}
                      alt={category.name}
                      className="pet-category-img"
                    />
                    <div className="pet-category-overlay">
                      <span className="pet-category-text">{category.name}</span>
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        .hero-section {
          background: linear-gradient(135deg, #FFF8F0 0%, #FAFAFA 100%);
          min-height: 60vh;
          display: flex;
          align-items: center;
          position: relative;
          overflow: hidden;
        }

        .hero-background {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          opacity: 0.1;
          z-index: 1;
        }

        .floating-pets {
          position: relative;
          width: 100%;
          height: 100%;
        }

        .pet-float-1, .pet-float-2, .pet-float-3, .pet-float-4, .pet-float-5 {
          position: absolute;
          font-size: 3rem;
          color:rgb(91, 215, 60);
          animation: float 6s ease-in-out infinite;
        }

        .pet-float-1 { top: 20%; left: 10%; animation-delay: 0s; }
        .pet-float-2 { top: 30%; right: 15%; animation-delay: 1s; }
        .pet-float-3 { bottom: 25%; left: 20%; animation-delay: 2s; }
        .pet-float-4 { bottom: 15%; right: 25%; animation-delay: 3s; }
        .pet-float-5 { top: 50%; left: 50%; animation-delay: 4s; }

        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(10deg); }
        }

        .hero-btn {
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .hero-btn:hover {
          transform: translateY(-3px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .hero-btn:hover .btn-icon {
          transform: translateX(5px);
        }

        .btn-icon {
          transition: transform 0.3s ease;
        }

        .btn-success {
          background-color: #00C897;
          border-color: #00C897;
          color: white;
        }

        .btn-success:hover {
          background-color: #00B386;
          border-color: #00B386;
          color: white;
        }

        .pet-categories-section {
          background-color: #FFF8F0;
        }

        .pet-category-circle {
          position: relative;
          width: 120px;
          height: 120px;
          border-radius: 50%;
          overflow: hidden;
          margin: 0 auto;
          box-shadow: 0 4px 15px rgba(0,0,0,0.1);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          cursor: pointer;
        }

        .pet-category-circle:hover {
          transform: scale(1.15) translateY(-5px);
          box-shadow: 0 12px 35px rgba(0,0,0,0.2);
        }

        .pet-category-circle:hover .pet-category-text {
          color: #444444;
        }

        .pet-category-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.4s ease;
        }

        .pet-category-circle:hover .pet-category-img {
          transform: scale(1.1);
        }

        .pet-category-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: linear-gradient(transparent, rgba(255,255,255,0.9));
          color: #444444;
          padding: 15px 5px 8px;
          font-size: 12px;
          font-weight: bold;
          transition: all 0.3s ease;
        }

        .pet-category-text {
          display: block;
          text-align: center;
          transition: color 0.3s ease;
        }

        .z-2 {
          z-index: 2;
        }
      `}</style>
    </div>
  );
};

export default Home;
