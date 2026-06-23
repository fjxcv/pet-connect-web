import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/api';
import { SITE_NAME } from '../constants/site';
import { logout } from '../utils/auth';
import { isAdminUser } from './AdminRoute';
import { useManageMode } from '../context/ManageModeContext';

const Navbar = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const token = localStorage.getItem('token');
  const { manageMode, setManageMode, refreshAdmin } = useManageMode();

  const fetchUserProfile = useCallback(async () => {
    if (!token) return;
    try {
      const res = await authAPI.getProfile();
      setUser(res.data);
      const admin = isAdminUser(res.data);
      setIsAdmin(admin);
      refreshAdmin();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        setUser(null);
        setIsAdmin(false);
        navigate('/login');
      }
    }
  }, [navigate, token, refreshAdmin]);

  useEffect(() => {
    if (token) fetchUserProfile();
    else {
      setUser(null);
      setIsAdmin(false);
    }
  }, [token, fetchUserProfile]);

  useEffect(() => {
    if (!userMenuOpen) return undefined;
    const close = () => setUserMenuOpen(false);
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [userMenuOpen]);

  const handleLogout = () => {
    logout(navigate);
    setUser(null);
    setIsAdmin(false);
    setManageMode(false);
  };

  const L = {
    home: '首页', pets: '领养宠物', cms: '科普公告', lost: '报失寻主', comm: '社区', rescue: '救助追踪',
    add: '添加档案', dash: '我的领养', admin: '管理后台', profile: '个人中心', publicPage: '我的主页', editProfile: '编辑资料', my: '我的救助', out: '退出登录', login: '登录', reg: '注册', user: '用户', manage: '管理模式',
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: '#ff8c00' }}>
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/"><i className="fas fa-paw me-2"></i>{SITE_NAME}</Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"><span className="navbar-toggler-icon"></span></button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item"><Link className="nav-link" to="/">{L.home}</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/pets">{L.pets}</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/cms">{L.cms}</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/lost-found">{L.lost}</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/community">{L.comm}</Link></li>
            <li className="nav-item"><Link className="nav-link" to="/rescue">{L.rescue}</Link></li>
            {token && isAdmin && <li className="nav-item"><Link className="nav-link" to="/add-pet">{L.add}</Link></li>}
            {token && isAdmin && <li className="nav-item"><Link className="nav-link" to="/admin">{L.admin}</Link></li>}
          </ul>
          <ul className="navbar-nav align-items-center gap-2">
            {token && isAdmin && (
              <li className="nav-item form-check form-switch text-white mb-0">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="manageModeSwitch"
                  checked={manageMode}
                  onChange={(e) => setManageMode(e.target.checked)}
                />
                <label className="form-check-label small ms-1" htmlFor="manageModeSwitch">{L.manage}</label>
              </li>
            )}
            {token ? (
              <li className={`nav-item dropdown${userMenuOpen ? ' show' : ''}`}>
                <div className="d-flex align-items-center" onClick={(e) => e.stopPropagation()}>
                  <Link
                    className="nav-link py-2"
                    to="/account"
                    onClick={() => setUserMenuOpen(false)}
                    title={L.profile}
                  >
                    {user?.profile?.nickname || user?.username || L.user}
                  </Link>
                  <button
                    className="nav-link dropdown-toggle btn"
                    type="button"
                    aria-expanded={userMenuOpen}
                    aria-label="用户菜单"
                    onClick={() => setUserMenuOpen((open) => !open)}
                    style={{ background: 'transparent', border: 'none', color: 'inherit', paddingLeft: 0 }}
                  />
                </div>
                <ul className={`dropdown-menu dropdown-menu-end${userMenuOpen ? ' show' : ''}`}>
                  <li><Link className="dropdown-item" to="/account" onClick={() => setUserMenuOpen(false)}>{L.profile}</Link></li>
                  {user?.id && (
                    <li>
                      <Link className="dropdown-item" to={`/users/${user.id}`} onClick={() => setUserMenuOpen(false)}>
                        {L.publicPage}
                      </Link>
                    </li>
                  )}
                  <li><Link className="dropdown-item" to="/profile" onClick={() => setUserMenuOpen(false)}>{L.editProfile}</Link></li>
                  {!isAdmin && <li><Link className="dropdown-item" to="/my-rescues" onClick={() => setUserMenuOpen(false)}>{L.my}</Link></li>}
                  {isAdmin && <li><Link className="dropdown-item" to="/admin" onClick={() => setUserMenuOpen(false)}>{L.admin}</Link></li>}
                  <li><hr className="dropdown-divider" /></li>
                  <li><button type="button" className="dropdown-item" onClick={() => { setUserMenuOpen(false); handleLogout(); }}>{L.out}</button></li>
                </ul>
              </li>
            ) : (
              <>
                <li className="nav-item"><Link className="nav-link" to="/login">{L.login}</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/register">{L.reg}</Link></li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
