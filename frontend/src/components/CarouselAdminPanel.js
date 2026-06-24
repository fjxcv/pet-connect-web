import React, { useCallback, useEffect, useState } from 'react';
import { petsAPI, portalAPI, uploadAPI } from '../api/api';

const emptyForm = () => ({
  title: '',
  image_url: '',
  link_url: '',
  sort_order: 0,
  status: 1,
});

const toList = (data) => (Array.isArray(data) ? data : data?.results ?? []);

const CarouselAdminPanel = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm());
  const [editingId, setEditingId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [adoptPets, setAdoptPets] = useState([]);
  const [selectedPetId, setSelectedPetId] = useState('');

  const loadItems = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await portalAPI.getCarousel();
      setItems(toList(res.data));
    } catch (err) {
      setError(err.response?.data?.detail || err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAdoptPets = useCallback(async () => {
    try {
      const res = await petsAPI.getAll({ adoption_status: 'available', is_public: 'true' });
      setAdoptPets(toList(res.data));
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    loadItems();
    loadAdoptPets();
  }, [loadItems, loadAdoptPets]);

  const openEditor = (item) => {
    if (item) {
      setEditingId(item.id);
      setForm({
        title: item.title || '',
        image_url: item.image_url || '',
        link_url: item.link_url || '',
        sort_order: item.sort_order ?? 0,
        status: item.status ?? 1,
      });
    } else {
      setEditingId(null);
      setForm(emptyForm());
      setSelectedPetId('');
    }
    setShowForm(true);
  };

  const handlePetFill = (petId) => {
    setSelectedPetId(petId);
    const pet = adoptPets.find((p) => String(p.id) === String(petId));
    if (!pet) return;
    if (!pet.photo_url) {
      alert('该宠物暂无照片，请手动上传轮播图');
      return;
    }
    setForm((f) => ({
      ...f,
      title: pet.name || f.title,
      image_url: pet.photo_url,
      link_url: `/pets/${pet.id}`,
    }));
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await uploadAPI.upload(file);
      const url = res.data?.url || res.data?.file_url;
      if (url) setForm((f) => ({ ...f, image_url: url }));
      else alert('上传成功但未返回 URL');
    } catch (err) {
      alert('图片上传失败');
      console.error(err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.image_url.trim()) {
      alert('请填写或上传轮播图片');
      return;
    }
    try {
      const payload = {
        ...form,
        sort_order: Number(form.sort_order) || 0,
        status: Number(form.status),
      };
      if (editingId) {
        await portalAPI.updateCarousel(editingId, payload);
      } else {
        await portalAPI.createCarousel(payload);
      }
      setShowForm(false);
      loadItems();
    } catch (err) {
      alert(err.response?.data?.detail || '保存失败');
    }
  };

<<<<<<< HEAD
=======
  const handleMove = async (index, dir) => {
    const next = index + dir;
    if (next < 0 || next >= items.length) return;
    const reordered = [...items];
    [reordered[index], reordered[next]] = [reordered[next], reordered[index]];
    try {
      await Promise.all(
        reordered
          .map((it, i) => (it.sort_order === i ? null : portalAPI.updateCarousel(it.id, { sort_order: i })))
          .filter(Boolean)
      );
      setItems(reordered.map((it, i) => ({ ...it, sort_order: i })));
    } catch (err) {
      alert('排序失败');
      loadItems();
    }
  };

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const handleDelete = async (id) => {
    if (!window.confirm('确定删除该轮播项？')) return;
    try {
      await portalAPI.deleteCarousel(id);
      loadItems();
    } catch (err) {
      alert('删除失败');
    }
  };

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      {error && <div className="alert alert-danger">{error}</div>}
      <button type="button" className="btn btn-success btn-sm mb-3" onClick={() => openEditor(null)}>
        新建轮播
      </button>

      {showForm && (
        <form className="card mb-4" onSubmit={handleSave}>
          <div className="card-header">{editingId ? '编辑轮播' : '新建轮播'}</div>
          <div className="card-body row g-2">
            <div className="col-12">
              <label className="form-label">从待领养宠物快捷填充</label>
              <select
                className="form-select"
                value={selectedPetId}
                onChange={(e) => handlePetFill(e.target.value)}
              >
                <option value="">选择宠物（可选）</option>
                {adoptPets.map((pet) => (
                  <option key={pet.id} value={pet.id} disabled={!pet.photo_url}>
                    {pet.name || `宠物 #${pet.id}`}{!pet.photo_url ? '（无照片）' : ''}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-6">
              <label className="form-label">标题</label>
              <input className="form-control" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="col-md-3">
              <label className="form-label">排序</label>
              <input type="number" className="form-control" value={form.sort_order} onChange={(e) => setForm({ ...form, sort_order: e.target.value })} />
            </div>
            <div className="col-md-3">
              <label className="form-label">状态</label>
              <select className="form-select" value={form.status} onChange={(e) => setForm({ ...form, status: Number(e.target.value) })}>
                <option value={1}>上线</option>
                <option value={0}>下线</option>
              </select>
            </div>
            <div className="col-12">
              <label className="form-label">图片 URL</label>
              <div className="input-group mb-2">
                <input className="form-control" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} required />
                <label className="btn btn-outline-secondary mb-0">
                  {uploading ? '上传中…' : '上传图片'}
                  <input type="file" accept="image/*" hidden onChange={handleImageUpload} disabled={uploading} />
                </label>
              </div>
              {form.image_url && (
                <img src={form.image_url} alt="预览" className="img-thumbnail" style={{ maxHeight: 120 }} />
              )}
            </div>
            <div className="col-12">
              <label className="form-label">跳转链接</label>
              <input className="form-control" placeholder="/pets/1 或 https://..." value={form.link_url} onChange={(e) => setForm({ ...form, link_url: e.target.value })} />
            </div>
            <div className="col-12">
              <button type="submit" className="btn btn-primary btn-sm me-2">保存</button>
              <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setShowForm(false)}>取消</button>
            </div>
          </div>
        </form>
      )}

      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>缩略图</th>
              <th>标题</th>
              <th>链接</th>
              <th>排序</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
<<<<<<< HEAD
            {items.map((item) => (
=======
            {items.map((item, index) => (
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              <tr key={item.id}>
                <td>
                  {item.image_url ? (
                    <img src={item.image_url} alt="" style={{ width: 80, height: 48, objectFit: 'cover' }} className="rounded" />
                  ) : '-'}
                </td>
                <td>{item.title || '-'}</td>
                <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.link_url || '-'}</td>
                <td>{item.sort_order}</td>
                <td>{item.status === 1 ? <span className="badge bg-success">上线</span> : <span className="badge bg-secondary">下线</span>}</td>
                <td>
                  <div className="btn-group btn-group-sm">
<<<<<<< HEAD
=======
                    <button type="button" className="btn btn-outline-secondary" onClick={() => handleMove(index, -1)} disabled={index === 0} title="上移">↑</button>
                    <button type="button" className="btn btn-outline-secondary" onClick={() => handleMove(index, 1)} disabled={index === items.length - 1} title="下移">↓</button>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                    <button type="button" className="btn btn-outline-primary" onClick={() => openEditor(item)}>编辑</button>
                    <button type="button" className="btn btn-outline-danger" onClick={() => handleDelete(item.id)}>删除</button>
                  </div>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="text-muted text-center">暂无轮播项</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CarouselAdminPanel;
