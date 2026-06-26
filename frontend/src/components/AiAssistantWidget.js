/**
 * @file AiAssistantWidget.js
 * @module PawRescue
 * @description 智能养宠问答挂件（可拖拽浮窗）。
 */

import React, { useEffect, useRef, useState } from 'react';
import { aiAPI } from '../api/api';
import './AiAssistantWidget.css';
const DRAG_THRESHOLD_PX = 8;
const T = {
  welcome: '\u4f60\u597d\uff0c\u6211\u662f\u6696\u722a\u667a\u80fd\u517b\u5ba0\u52a9\u624b\uff0c\u6709\u4ec0\u4e48\u517b\u5ba0\u95ee\u9898\u53ef\u4ee5\u95ee\u6211\u3002',
  loginFirst: '\u8bf7\u5148\u767b\u5f55\u540e\u518d\u4f7f\u7528\u667a\u80fd\u52a9\u624b',
  title: '\u667a\u80fd\u517b\u5ba0\u52a9\u624b',
  dragTitle: '\u62d6\u52a8\u4f4d\u7f6e',
  dragAria: '\u62d6\u52a8\u52a9\u624b\u4f4d\u7f6e',
  close: '\u5173\u95ed',
  disclaimer: 'AI \u56de\u7b54\u4ec5\u4f9b\u53c2\u8003\uff0c\u4e0d\u80fd\u66ff\u4ee3\u517d\u533b\u8bca\u65ad\uff1b\u5ba0\u7269\u4e0d\u9002\u6216\u751f\u75c5\u8bf7\u5c3d\u5feb\u5c31\u533b\u3002',
  thinking: '\u601d\u8003\u4e2d...',
  placeholder: '\u8f93\u5165\u517b\u5ba0\u95ee\u9898...',
  send: '\u53d1\u9001',
  fabTitle: '\u667a\u80fd\u517b\u5ba0\u52a9\u624b\uff08\u62d6\u52a8\u53ef\u79fb\u52a8\u4f4d\u7f6e\uff0c\u70b9\u51fb\u6253\u5f00\uff09',
  quotaExceeded: '\u4eca\u65e5\u6216\u7d2f\u8ba1 AI \u8c03\u7528\u5df2\u8fbe\u4e0a\u9650\uff0c\u8bf7\u8054\u7cfb\u7ba1\u7406\u5458',
  llmNotConfigured: '\u672a\u914d\u7f6e LLM\uff0c\u8bf7\u8054\u7cfb\u7ba1\u7406\u5458',
  timeout: '\u8bf7\u6c42\u8d85\u65f6\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5',
  genericFail: '\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u786e\u8ba4\u540e\u7aef\u5df2\u542f\u52a8\u4e14 LLM \u5df2\u914d\u7f6e',
};
/**
 * 功能：智能养宠助手浮窗，调用 aiAPI.qa。
 * 【权限】visitor 需登录；user/admin 可用。
 */
const AiAssistantWidget = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: T.welcome },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [pos, setPos] = useState({ x: null, y: null });
  const [pointerActive, setPointerActive] = useState(false);
  const rootRef = useRef(null);
  const dragOffsetRef = useRef({ offsetX: 0, offsetY: 0 });
  const pointerStartRef = useRef({ x: 0, y: 0 });
  const dragModeRef = useRef('fab');
  const movedRef = useRef(false);
  useEffect(() => {
    const saved = localStorage.getItem('aiWidgetPos');
    if (saved) {
      try {
        setPos(JSON.parse(saved));
      } catch {
        /* ignore */
      }
    }
  }, []);
  const savePosition = (x, y) => {
    const next = { x, y };
    setPos(next);
    localStorage.setItem('aiWidgetPos', JSON.stringify(next));
  };
  const beginPointerDrag = (e, mode) => {
    if (!rootRef.current) return;
    const rect = rootRef.current.getBoundingClientRect();
    dragOffsetRef.current = {
      offsetX: e.clientX - rect.left,
      offsetY: e.clientY - rect.top,
    };
    pointerStartRef.current = { x: e.clientX, y: e.clientY };
    dragModeRef.current = mode;
    movedRef.current = mode === 'handle';
    setPointerActive(true);
    if (mode === 'handle') {
      document.body.classList.add('ai-widget-dragging');
    }
  };
  useEffect(() => {
    if (!pointerActive) return undefined;
    const onMove = (e) => {
      if (!movedRef.current && dragModeRef.current === 'fab') {
        const dx = e.clientX - pointerStartRef.current.x;
        const dy = e.clientY - pointerStartRef.current.y;
        if (dx * dx + dy * dy < DRAG_THRESHOLD_PX * DRAG_THRESHOLD_PX) {
          return;
        }
        movedRef.current = true;
        document.body.classList.add('ai-widget-dragging');
      }
      if (!movedRef.current) return;
      setPos({
        x: e.clientX - dragOffsetRef.current.offsetX,
        y: e.clientY - dragOffsetRef.current.offsetY,
      });
    };
    const onUp = (e) => {
      if (movedRef.current) {
        savePosition(
          e.clientX - dragOffsetRef.current.offsetX,
          e.clientY - dragOffsetRef.current.offsetY,
        );
      } else if (dragModeRef.current === 'fab') {
        setOpen((o) => !o);
      }
      movedRef.current = false;
      setPointerActive(false);
      document.body.classList.remove('ai-widget-dragging');
    };
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('pointercancel', onUp);
    return () => {
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointercancel', onUp);
      document.body.classList.remove('ai-widget-dragging');
    };
  }, [pointerActive]);
  const onDragHandleDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    beginPointerDrag(e, 'handle');
  };
  const onFabPointerDown = (e) => {
    e.preventDefault();
    beginPointerDrag(e, 'fab');
    e.currentTarget.setPointerCapture(e.pointerId);
  };
  /** 功能：将 API 错误转为友好提示。 */
  const formatAiError = (err) => {
    const status = err.response?.status;
    let detail = err.response?.data?.detail || '';
    if (typeof detail !== 'string') detail = String(detail || '');
    if (status === 401) return T.loginFirst;
    if (status === 429) return detail || T.quotaExceeded;
    if (status === 503) return detail || T.llmNotConfigured;
    if (status === 502) return detail || T.genericFail;
    if (err.code === 'ECONNABORTED') return T.timeout;
    if (detail) return detail;
    return T.genericFail;
  };
  /** 功能：发送问题调用 AI。【权限】需 token。 */
  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    // 【权限】游客未登录
    if (!localStorage.getItem('token')) {
      alert(T.loginFirst);
      return;
    }
    const nextMsgs = [...messages, { role: 'user', content: q }];
    setMessages(nextMsgs);
    setInput('');
    setLoading(true);
    try {
      const history = nextMsgs.slice(-8);
      const res = await aiAPI.qa({ question: q, history });
      setMessages((m) => [...m, { role: 'assistant', content: res.data.answer }]);
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: formatAiError(err) }]);
    } finally {
      setLoading(false);
    }
  };
  const style = pos.x != null ? { left: pos.x, top: pos.y, right: 'auto', bottom: 'auto' } : {};
  const fabDragging = pointerActive && movedRef.current;
  return (
    <div className="ai-widget-root" style={style} ref={rootRef}>
      {open && (
        <div className="ai-panel card shadow">
          <div className="card-header d-flex justify-content-between align-items-center py-2 gap-2">
            <button
              type="button"
              className="ai-drag-handle btn btn-sm btn-light border"
              title={T.dragTitle}
              aria-label={T.dragAria}
              onPointerDown={onDragHandleDown}
            >
              <i className="fas fa-grip-lines" />
            </button>
            <span className="fw-semibold small flex-grow-1 text-center">{T.title}</span>
            <button type="button" className="btn-close btn-sm" aria-label={T.close} onClick={() => setOpen(false)} />
          </div>
          <div className="ai-disclaimer" role="note">
            <i className="fas fa-exclamation-triangle text-warning" aria-hidden />
            <span>{T.disclaimer}</span>
          </div>
          <div className="ai-panel-messages">
            {messages.map((m, i) => (
              <div key={i} className={`ai-msg ai-msg-${m.role}`}>{m.content}</div>
            ))}
            {loading && <div className="text-muted small">{T.thinking}</div>}
          </div>
          <div className="card-footer p-2">
            <div className="input-group input-group-sm">
              <input
                className="form-control ai-panel-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && send()}
                placeholder={T.placeholder}
              />
              <button type="button" className="btn btn-success" onClick={send} disabled={loading}>{T.send}</button>
            </div>
          </div>
        </div>
      )}
      <button
        type="button"
        className={`ai-fab btn btn-success rounded-circle shadow${fabDragging ? ' ai-fab-dragging' : ''}`}
        onPointerDown={onFabPointerDown}
        title={T.fabTitle}
        aria-expanded={open}
      >
        <i className="fas fa-robot" />
      </button>
    </div>
  );
};

export default AiAssistantWidget;

