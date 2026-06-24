import { useCallback, useEffect, useState } from 'react';
<<<<<<< HEAD
import { Link, useNavigate } from 'react-router-dom';
=======
import { Link, NavLink, useNavigate } from 'react-router-dom';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
import { authAPI } from '../api/api';
import { SITE_NAME } from '../constants/site';
import { logout } from '../utils/auth';
import { isAdminUser } from './AdminRoute';
import { useManageMode } from '../context/ManageModeContext';

<<<<<<< HEAD
=======
const MAIN_NAV = [
  { to: '/', label: '\u9996\u9875', end: true },
  { to: '/pets', label: '\u9886\u517b\u5ba0\u7269' },
  { to: '/cms', label: '\u79d1\u666e\u516c\u544a' },
  { to: '/lost-found', label: '\u62a5\u5931\u5bfb\u4e3b' },
  { to: '/community', label: '\u793e\u533a' },
  { to: '/rescue', label: '\u6551\u52a9\u8ddf\u8e2a' },
];

const ADMIN_NAV = [
  { to: '/add-pet', label: '\u6dfb\u52a0\u6863\u6848' },
  { to: '/admin', label: '\u7ba1\u7406\u540e\u53f0' },
];

const mainNavClass = ({ isActive }) =>
  `nav-link navbar-main-link${isActive ? ' active' : ''}`;

const adminNavClass = ({ isActive }) =>
  `nav-link navbar-main-link navbar-main-link--admin${isActive ? ' active' : ''}`;

const authNavClass = ({ isActive }) =>
  `nav-link navbar-auth-link${isActive ? ' active' : ''}`;

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
    home: '首页', pets: '领养宠物', cms: '科普公告', lost: '报失寻主', comm: '社区', rescue: '救助跟踪',
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
=======
    profile: '\u4e2a\u4eba\u4e2d\u5fc3',
    publicPage: '\u6211\u7684\u4e3b\u9875',
    editProfile: '\u7f16\u8f91\u8d44\u6599',
    my: '\u6211\u7684\u6551\u52a9',
    admin: '\u7ba1\u7406\u540e\u53f0',
    out: '\u9000\u51fa\u767b\u5f55',
    login: '\u767b\u5f55',
    reg: '\u6ce8\u518c',
    user: '\u7528\u6237',
    manage: '\u7ba1\u7406\u6a21\u5f0f',
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark navbar-main" style={{ backgroundColor: '#ff8c00' }}>
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/"><i className="fas fa-paw me-2"></i>{SITE_NAME}</Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="\u5c55\u5f00\u5bfc\u822a"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto navbar-main-pills">
            {MAIN_NAV.map(({ to, label, end }) => (
              <li className="nav-item" key={to}>
                <NavLink className={mainNavClass} to={to} end={end}>
                  {label}
                </NavLink>
              </li>
            ))}
            {token && isAdmin && ADMIN_NAV.map(({ to, label }) => (
              <li className="nav-item" key={to}>
                <NavLink className={adminNavClass} to={to}>
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
          <ul className="navbar-nav align-items-lg-center gap-lg-2">
            {token && isAdmin && (
              <li className="nav-item form-check form-switch text-white mb-0 px-2">
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
                  <Link
                    className="nav-link py-2"
=======
                  <NavLink
                    className={({ isActive }) => `nav-link py-2 navbar-user-link${isActive ? ' active' : ''}`}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                    to="/account"
                    onClick={() => setUserMenuOpen(false)}
                    title={L.profile}
                  >
                    {user?.profile?.nickname || user?.username || L.user}
<<<<<<< HEAD
                  </Link>
=======
                  </NavLink>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                  <button
                    className="nav-link dropdown-toggle btn"
                    type="button"
                    aria-expanded={userMenuOpen}
<<<<<<< HEAD
                    aria-label="用户菜单"
=======
                    aria-label="\u7528\u6237\u83dc\u5355"
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
                <li className="nav-item"><Link className="nav-link" to="/login">{L.login}</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/register">{L.reg}</Link></li>
=======
                <li className="nav-item">
                  <NavLink className={authNavClass} to="/login">{L.login}</NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className={authNavClass} to="/register">{L.reg}</NavLink>
                </li>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};
<<<<<<< HEAD
=======

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
export default Navbar;
