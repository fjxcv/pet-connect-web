import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

<<<<<<< HEAD
const CmsMarkdownEditor = ({ value, onChange }) => {
  const [tab, setTab] = useState('edit');
=======
const CmsMarkdownEditor = ({
  value,
  onChange,
  required = false,
  rows = 12,
  minPreviewHeight = 280,
  placeholder,
}) => {
  const [tab, setTab] = useState('edit');
  const placeholderText = placeholder || '支持 Markdown 语法（标题、列表、链接等）';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

  return (
    <div className="col-12">
      <ul className="nav nav-tabs mb-2">
        <li className="nav-item">
          <button type="button" className={`nav-link ${tab === 'edit' ? 'active' : ''}`} onClick={() => setTab('edit')}>
            编辑
          </button>
        </li>
        <li className="nav-item">
          <button type="button" className={`nav-link ${tab === 'preview' ? 'active' : ''}`} onClick={() => setTab('preview')}>
            预览
          </button>
        </li>
      </ul>
      {tab === 'edit' ? (
        <textarea
          className="form-control font-monospace"
<<<<<<< HEAD
          rows={12}
          placeholder="支持 Markdown 语法（标题、列表、链接等）"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required
        />
      ) : (
        <div className="border rounded p-3 bg-white markdown-preview" style={{ minHeight: 280 }}>
=======
          rows={rows}
          placeholder={placeholderText}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
        />
      ) : (
        <div className="border rounded p-3 bg-white markdown-preview" style={{ minHeight: minPreviewHeight }}>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
          {value ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
          ) : (
            <p className="text-muted mb-0">暂无内容</p>
          )}
        </div>
      )}
    </div>
  );
};

export default CmsMarkdownEditor;
