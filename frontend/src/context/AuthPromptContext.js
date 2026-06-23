import React, { createContext, useCallback, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthPromptContext = createContext(null);

export const AuthPromptProvider = ({ children }) => {
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);

  const promptLogin = useCallback(() => setVisible(true), []);

  const requireAuth = useCallback(() => {
    if (localStorage.getItem('token')) return true;
    setVisible(true);
    return false;
  }, []);

  const close = useCallback(() => setVisible(false), []);

  return (
    <AuthPromptContext.Provider value={{ requireAuth, promptLogin, close }}>
      {children}
      {visible && (
        <div className="modal fade show d-block" tabIndex="-1" role="dialog" style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}>
          <div className="modal-dialog modal-dialog-centered" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">请先登录</h5>
                <button type="button" className="btn-close" onClick={close} aria-label="Close" />
              </div>
              <div className="modal-body">
                <p>请先登录以使用互动功能。</p>
              </div>
              <div className="modal-footer justify-content-center">
                <button type="button" className="btn btn-secondary me-2" onClick={close}>
                  取消
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => {
                    setVisible(false);
                    navigate('/login');
                  }}
                >
                  去登录
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </AuthPromptContext.Provider>
  );
};

export const useAuthPrompt = () => useContext(AuthPromptContext);

export default AuthPromptContext;
