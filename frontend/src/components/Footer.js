/**
 * @file Footer.js
 * @module PawRescue
 * @description 可复用组件：Footer。
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { SITE_NAME } from '../constants/site';
const Footer = () => (
  <footer className="footer-gradient text-white py-5 mt-auto">
    <div className="container">
      <div className="row mb-4 text-start text-md-center">
        <div className="col-md-4 mb-4 mb-md-0">
          <h5 className="fw-bold mb-3">联系我们</h5>
          <p className="mb-2"><i className="fas fa-map-marker-alt me-2 text-warning"></i>四川省成都市高新区暖爪路 88 号</p>
          <p className="mb-2"><i className="fas fa-phone me-2 text-warning"></i>400-888-0628（工作日 9:00-18:00）</p>
          <p><i className="fas fa-envelope me-2 text-warning"></i>service@nuanzhao-rescue.cn</p>
        </div>
        <div className="col-md-4 mb-4 mb-md-0">
          <h5 className="fw-bold mb-3">快捷入口</h5>
          <div className="d-flex flex-column gap-2 align-items-md-center">
            <Link to="/pets" className="footer-link text-white">领养宠物</Link>
            <Link to="/cms" className="footer-link text-white">科普与公告</Link>
            <Link to="/lost-found" className="footer-link text-white">报失寻主</Link>
            <Link to="/community" className="footer-link text-white">互动社区</Link>
          </div>
        </div>
        <div className="col-md-4">
          <h5 className="fw-bold mb-3">关注我们</h5>
          <div className="d-flex justify-content-md-center gap-4">
            <button type="button" className="btn btn-link text-white p-0"><i className="fab fa-weixin fa-2x"></i></button>
            <button type="button" className="btn btn-link text-white p-0"><i className="fab fa-weibo fa-2x"></i></button>
            <button type="button" className="btn btn-link text-white p-0"><i className="fas fa-play-circle fa-2x"></i></button>
          </div>
          <p className="small text-white-50 mt-3">社交平台链接仅为展示，暂未开放跳转</p>
        </div>
      </div>
      <hr className="border-light" />
      <div className="text-center small">&copy; {new Date().getFullYear()} <strong>{SITE_NAME}</strong> · 保留所有权利</div>
    </div>
    <style>{`.footer-gradient{background:linear-gradient(135deg,rgb(9,17,65),rgb(8,17,60));}`}</style>
  </footer>
);

export default Footer;

