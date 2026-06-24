import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { aiAPI, lostFoundAPI, uploadAPI } from '../api/api';
import { LOST_FOUND_TYPE } from '../constants/site';
import { AMAP_KEY, AMAP_TILE_URL, AMAP_TILE_OPTIONS } from '../config/amap';
import { formatApiError, roundCoordinate } from '../utils/apiError';

/**
<<<<<<< HEAD
 * GCJ-02 转 WGS-84（火星坐标系 → GPS 标准坐标系）
 * 高德地图使用 GCJ-02，Leaflet/OpenStreetMap 使用 WGS-84
 * 如果不转换，高德搜索到的坐标在 Leaflet 地图上会有几百米偏移
 */
function gcj02ToWgs84(lat, lng) {
  const a = 6378245.0; // 长半轴
  const ee = 0.00669342162296594323; // 扁率
=======
 * GCJ-02 杞� WGS-84锛堢伀鏄熷潗鏍囩郴 鈫� GPS 鏍囧噯鍧愭爣绯伙級
 * 楂樺痉鍦板浘浣跨敤 GCJ-02锛孡eaflet/OpenStreetMap 浣跨敤 WGS-84
 * 濡傛灉涓嶈浆鎹紝楂樺痉鎼滅储鍒扮殑鍧愭爣鍦� Leaflet 鍦板浘涓婁細鏈夊嚑鐧剧背鍋忕Щ
 */
function gcj02ToWgs84(lat, lng) {
  const a = 6378245.0; // 闀垮崐杞�
  const ee = 0.00669342162296594323; // 鎵佺巼
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

  function transformLat(x, y) {
    let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
    ret += ((20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0) / 3.0;
    ret += ((20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin((y / 3.0) * Math.PI)) * 2.0) / 3.0;
    ret += ((160.0 * Math.sin((y / 12.0) * Math.PI) + 320.0 * Math.sin((y * Math.PI) / 30.0)) * 2.0) / 3.0;
    return ret;
  }

  function transformLng(x, y) {
    let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
    ret += ((20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0) / 3.0;
    ret += ((20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin((x / 3.0) * Math.PI)) * 2.0) / 3.0;
    ret += ((150.0 * Math.sin((x / 12.0) * Math.PI) + 300.0 * Math.sin((x / 30.0) * Math.PI)) * 2.0) / 3.0;
    return ret;
  }

<<<<<<< HEAD
  // 判断是否在中国境内，不在则不转换
=======
  // 鍒ゆ柇鏄惁鍦ㄤ腑鍥藉鍐咃紝涓嶅湪鍒欎笉杞崲
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  if (lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271) {
    return { lat, lng };
  }

  let dLat = transformLat(lng - 105.0, lat - 35.0);
  let dLng = transformLng(lng - 105.0, lat - 35.0);
  const radLat = (lat / 180.0) * Math.PI;
  let magic = Math.sin(radLat);
  magic = 1 - ee * magic * magic;
  const sqrtMagic = Math.sqrt(magic);
  dLat = (dLat * 180.0) / (((a * (1 - ee)) / (magic * sqrtMagic)) * Math.PI);
  dLng = (dLng * 180.0) / ((a / sqrtMagic) * Math.cos(radLat) * Math.PI);
  return {
    lat: lat - dLat,
    lng: lng - dLng,
  };
}

/**
<<<<<<< HEAD
 * 高德地图 POI 关键字搜索
 * https://restapi.amap.com/v3/place/text
 */
async function amapPlaceText(keywords, city = '成都') {
=======
 * 楂樺痉鍦板浘 POI 鍏抽敭瀛楁悳绱�
 * https://restapi.amap.com/v3/place/text
 */
async function amapPlaceText(keywords, city = '鎴愰兘') {
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  if (!keywords.trim()) return [];
  const url =
    `https://restapi.amap.com/v3/place/text?key=${AMAP_KEY}` +
    `&keywords=${encodeURIComponent(keywords)}` +
    `&types=&city=${encodeURIComponent(city)}` +
    `&offset=10&page=1&extensions=base`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.status !== '1' || !Array.isArray(data.pois)) {
<<<<<<< HEAD
    console.warn('高德 place/text 返回异常:', data);
=======
    console.warn('楂樺痉 place/text 杩斿洖寮傚父:', data);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    return [];
  }
  return data.pois.map((poi) => {
    const gcjLat = parseFloat(poi.location.split(',')[1]);
    const gcjLng = parseFloat(poi.location.split(',')[0]);
    return {
      id: poi.id,
      name: poi.name,
      address: poi.address || '',
      lat: gcjLat,
      lng: gcjLng,
      distance: poi.distance,
    };
  });
}

/**
<<<<<<< HEAD
 * 高德地图逆地理编码（坐标 → 文字地址）
 * 注意：传入的坐标需要是 GCJ-02 坐标系
 * 因为 Leaflet 地图用的是 WGS-84，所以需要先转成 GCJ-02 再请求高德 API
 * https://restapi.amap.com/v3/geocode/regeo
 */
async function amapRegeo(lat, lng) {
  // 将 WGS-84 转回 GCJ-02 再请求高德 API
  // 简单近似：直接用 WGS-84 坐标请求高德逆地理编码，高德会自动处理
=======
 * 楂樺痉鍦板浘閫嗗湴鐞嗙紪鐮侊紙鍧愭爣 鈫� 鏂囧瓧鍦板潃锛�
 * 娉ㄦ剰锛氫紶鍏ョ殑鍧愭爣闇€瑕佹槸 GCJ-02 鍧愭爣绯�
 * 鍥犱负 Leaflet 鍦板浘鐢ㄧ殑鏄� WGS-84锛屾墍浠ラ渶瑕佸厛杞垚 GCJ-02 鍐嶈姹傞珮寰� API
 * https://restapi.amap.com/v3/geocode/regeo
 */
async function amapRegeo(lat, lng) {
  // 灏� WGS-84 杞洖 GCJ-02 鍐嶈姹傞珮寰� API
  // 绠€鍗曡繎浼硷細鐩存帴鐢� WGS-84 鍧愭爣璇锋眰楂樺痉閫嗗湴鐞嗙紪鐮侊紝楂樺痉浼氳嚜鍔ㄥ鐞�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const location = `${lng},${lat}`;
  const url =
    `https://restapi.amap.com/v3/geocode/regeo?key=${AMAP_KEY}` +
    `&location=${encodeURIComponent(location)}` +
    `&radius=1000&extensions=base`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.status !== '1' || !data.regeocode) {
<<<<<<< HEAD
    console.warn('高德 regeo 返回异常:', data);
=======
    console.warn('楂樺痉 regeo 杩斿洖寮傚父:', data);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    return '';
  }
  return data.regeocode.formatted_address || '';
}

const LostFoundPublish = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    post_type: 'lost',
    pet_species: '',
    features: '',
    latitude: '',
    longitude: '',
    address_text: '',
    reward_amount: '0',
    contact_phone: '',
  });
  const [photoUrls, setPhotoUrls] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [locating, setLocating] = useState(false);
  const [locationHint, setLocationHint] = useState('');
  const [error, setError] = useState('');
  const [photoError, setPhotoError] = useState('');
  const [mapReady, setMapReady] = useState(false);
<<<<<<< HEAD
  const mapCenter = useMemo(() => [30.5728, 104.0668], []); // 默认成都
=======
  const mapCenter = useMemo(() => [30.5728, 104.0668], []); // 榛樿鎴愰兘
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const leafletMapRef = useRef(null);

<<<<<<< HEAD
  // ---- 地点搜索（高德 POI）----
=======
  // ---- 鍦扮偣鎼滅储锛堥珮寰� POI锛�----
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchTimerRef = useRef(null);
  const dropdownRef = useRef(null);

<<<<<<< HEAD
  // 防抖搜索
=======
  // 闃叉姈鎼滅储
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const handleSearchInput = (e) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    if (!val.trim()) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }
    searchTimerRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const results = await amapPlaceText(val);
        setSearchResults(results);
        setShowDropdown(results.length > 0);
      } catch (err) {
<<<<<<< HEAD
        console.error('地点搜索失败:', err);
=======
        console.error('鍦扮偣鎼滅储澶辫触:', err);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 400);
  };

<<<<<<< HEAD
  // 选中搜索结果
  const handleSelectResult = (poi) => {
    setSearchQuery(poi.name);
    setShowDropdown(false);
    // 更新表单
=======
  // 閫変腑鎼滅储缁撴灉
  const handleSelectResult = (poi) => {
    setSearchQuery(poi.name);
    setShowDropdown(false);
    // 鏇存柊琛ㄥ崟
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    setForm((f) => ({
      ...f,
      latitude: String(roundCoordinate(poi.lat)),
      longitude: String(roundCoordinate(poi.lng)),
      address_text: poi.address ? `${poi.name}, ${poi.address}` : poi.name,
    }));
<<<<<<< HEAD
    setLocationHint(`已定位到：${poi.name}`);
    // 移动地图标记
=======
    setLocationHint(`宸插畾浣嶅埌锛�${poi.name}`);
    // 绉诲姩鍦板浘鏍囪
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    if (leafletMapRef.current && markerRef.current) {
      leafletMapRef.current.setView([poi.lat, poi.lng], 16);
      markerRef.current.setLatLng([poi.lat, poi.lng]);
    }
  };

<<<<<<< HEAD
  // 点击外部关闭下拉
=======
  // 鐐瑰嚮澶栭儴鍏抽棴涓嬫媺
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const hasCoordinates = () => {
    const lat = parseFloat(form.latitude);
    const lng = parseFloat(form.longitude);
    return Number.isFinite(lat) && Number.isFinite(lng);
  };

<<<<<<< HEAD
  // 逆地理编码（高德）：坐标 → 文字地址
=======
  // 閫嗗湴鐞嗙紪鐮侊紙楂樺痉锛夛細鍧愭爣 鈫� 鏂囧瓧鍦板潃
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const reverseGeocode = useCallback(async (lat, lng) => {
    try {
      const addr = await amapRegeo(lat, lng);
      return addr;
    } catch {
      return '';
    }
  }, []);

<<<<<<< HEAD
  // 更新地图标记位置
=======
  // 鏇存柊鍦板浘鏍囪浣嶇疆
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  const updateMarkerPosition = useCallback(async (lat, lng) => {
    const roundedLat = roundCoordinate(lat);
    const roundedLng = roundCoordinate(lng);
    setForm((f) => ({
      ...f,
      latitude: String(roundedLat),
      longitude: String(roundedLng),
    }));
<<<<<<< HEAD
    // 高德逆地理编码获取地址
=======
    // 楂樺痉閫嗗湴鐞嗙紪鐮佽幏鍙栧湴鍧€
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    const addr = await reverseGeocode(roundedLat, roundedLng);
    if (addr) {
      setForm((f) => ({ ...f, address_text: addr }));
      setSearchQuery(addr);
    }
<<<<<<< HEAD
    setLocationHint(`已定位：${roundedLat}, ${roundedLng}`);
  }, [reverseGeocode]);

  // 初始化地图
=======
    setLocationHint(`宸插畾浣嶏細${roundedLat}, ${roundedLng}`);
  }, [reverseGeocode]);

  // 鍒濆鍖栧湴鍥�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  useEffect(() => {
    if (!mapRef.current || leafletMapRef.current) return;

    let cancelled = false;
    const initMap = () => {
      if (cancelled || !mapRef.current) return;
      const L = window.L;
      const map = L.map(mapRef.current).setView(mapCenter, 13);
      L.tileLayer(AMAP_TILE_URL, AMAP_TILE_OPTIONS).addTo(map);

      const marker = L.marker(mapCenter, { draggable: true }).addTo(map);
      markerRef.current = marker;
      leafletMapRef.current = map;

<<<<<<< HEAD
      // 点击地图移动标记
=======
      // 鐐瑰嚮鍦板浘绉诲姩鏍囪
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      map.on('click', (e) => {
        marker.setLatLng(e.latlng);
        updateMarkerPosition(e.latlng.lat, e.latlng.lng);
      });

<<<<<<< HEAD
      // 拖动标记
=======
      // 鎷栧姩鏍囪
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      marker.on('dragend', () => {
        const pos = marker.getLatLng();
        updateMarkerPosition(pos.lat, pos.lng);
      });

      if (!cancelled) setMapReady(true);
    };

    if (window.L) {
      initMap();
    } else {
      if (!document.querySelector('link[href*="leaflet.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }
      if (!document.querySelector('script[src*="leaflet.js"]')) {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = initMap;
<<<<<<< HEAD
        script.onerror = () => { if (!cancelled) setError('地图加载失败，请刷新页面重试'); };
=======
        script.onerror = () => { if (!cancelled) setError('鍦板浘鍔犺浇澶辫触锛岃鍒锋柊椤甸潰閲嶈瘯'); };
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        document.body.appendChild(script);
      } else {
        const check = setInterval(() => {
          if (window.L) {
            clearInterval(check);
            initMap();
          }
        }, 200);
      }
    }

    return () => {
      cancelled = true;
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
        markerRef.current = null;
        setMapReady(false);
      }
    };
  }, [mapCenter, updateMarkerPosition]);

<<<<<<< HEAD
  // 当使用当前位置时，移动地图和标记
=======
  // 褰撲娇鐢ㄥ綋鍓嶄綅缃椂锛岀Щ鍔ㄥ湴鍥惧拰鏍囪
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  useEffect(() => {
    if (mapReady && hasCoordinates() && leafletMapRef.current && markerRef.current) {
      const lat = parseFloat(form.latitude);
      const lng = parseFloat(form.longitude);
      if (Number.isFinite(lat) && Number.isFinite(lng)) {
        leafletMapRef.current.setView([lat, lng], 15);
        markerRef.current.setLatLng([lat, lng]);
      }
    }
  }, [form.latitude, form.longitude, mapReady]);

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
<<<<<<< HEAD
      setError('当前浏览器不支持定位，请换用手机浏览器或 Chrome/Edge。');
=======
      setError('褰撳墠娴忚鍣ㄤ笉鏀寔瀹氫綅锛岃鎹㈢敤鎵嬫満娴忚鍣ㄦ垨 Chrome/Edge銆�');
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      return;
    }
    setError('');
    setLocating(true);
    setLocationHint('');
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = roundCoordinate(pos.coords.latitude);
        const lng = roundCoordinate(pos.coords.longitude);
        setForm((f) => ({
          ...f,
          latitude: String(lat),
          longitude: String(lng),
        }));
<<<<<<< HEAD
        // 高德逆地理编码
=======
        // 楂樺痉閫嗗湴鐞嗙紪鐮�
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        const addr = await reverseGeocode(lat, lng);
        if (addr) {
          setForm((f) => ({ ...f, address_text: addr }));
          setSearchQuery(addr);
        }
        const meters = Math.round(pos.coords.accuracy);
<<<<<<< HEAD
        setLocationHint(`已记录当前位置（定位精度约 ${meters} 米）`);
=======
        setLocationHint(`宸茶褰曞綋鍓嶄綅缃紙瀹氫綅绮惧害绾� ${meters} 绫筹級`);
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        setLocating(false);
      },
      (geoErr) => {
        setLocating(false);
        const hints = {
<<<<<<< HEAD
          1: '您拒绝了位置权限，请在浏览器设置中允许定位后重试。',
          2: '暂时无法获取位置，请稍后重试或检查系统定位是否开启。',
          3: '定位超时，请到开阔处重试。',
        };
        setError(hints[geoErr.code] || '获取位置失败，请检查浏览器定位权限。');
=======
          1: '鎮ㄦ嫆缁濅簡浣嶇疆鏉冮檺锛岃鍦ㄦ祻瑙堝櫒璁剧疆涓厑璁稿畾浣嶅悗閲嶈瘯銆�',
          2: '鏆傛椂鏃犳硶鑾峰彇浣嶇疆锛岃绋嶅悗閲嶈瘯鎴栨鏌ョ郴缁熷畾浣嶆槸鍚﹀紑鍚€�',
          3: '瀹氫綅瓒呮椂锛岃鍒板紑闃斿閲嶈瘯銆�',
        };
        setError(hints[geoErr.code] || '鑾峰彇浣嶇疆澶辫触锛岃妫€鏌ユ祻瑙堝櫒瀹氫綅鏉冮檺銆�');
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 120000 },
    );
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handlePhotoUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    setUploading(true);
    setError('');
    try {
      const uploaded = [];
      for (const file of files) {
        const res = await uploadAPI.upload(file, 'lost-found');
        uploaded.push(res.data.url);
      }
      setPhotoUrls((prev) => [...prev, ...uploaded]);
    } catch (err) {
<<<<<<< HEAD
      setError('图片上传失败，请重试。');
=======
      setError('鍥剧墖涓婁紶澶辫触锛岃閲嶈瘯銆�');
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      console.error(err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const removePhoto = (index) => {
    setPhotoUrls((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const address = form.address_text.trim();
    if (!address) {
<<<<<<< HEAD
      setError('请填写事发地点或附近地标。');
      return;
    }
    if (!photoUrls.length) {
      setPhotoError('请至少上传 1 张宠物照片。');
=======
      setError('璇峰～鍐欎簨鍙戝湴鐐规垨闄勮繎鍦版爣銆�');
      return;
    }
    if (!photoUrls.length) {
      setPhotoError('璇疯嚦灏戜笂浼� 1 寮犲疇鐗╃収鐗囥€�');
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      return;
    }
    setPhotoError('');
    setSubmitting(true);
    setError('');
    try {
      const lat = roundCoordinate(form.latitude);
      const lng = roundCoordinate(form.longitude);
      const payload = {
        post_type: form.post_type,
        pet_species: form.pet_species,
        features: form.features,
        address_text: address,
        reward_amount: parseFloat(form.reward_amount) || 0,
        contact_phone: form.contact_phone || null,
        photo_urls: photoUrls,
      };
      if (lat != null && lng != null) {
        payload.latitude = lat;
        payload.longitude = lng;
      }
      const res = await lostFoundAPI.create(payload);
      navigate(`/lost-found/${res.data.id}`);
    } catch (err) {
<<<<<<< HEAD
      setError(formatApiError(err, '发布失败，请检查表单后重试。'));
=======
      const detail = err.response?.data?.detail;
      setError(
        detail === 'account_banned'
          ? '账号已被封禁，无法发布信息。'
          : formatApiError(err, '鍙戝竷澶辫触锛岃妫€鏌ヨ〃鍗曞悗閲嶈瘯銆�')
      );
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="py-3">
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
<<<<<<< HEAD
          <li className="breadcrumb-item"><Link to="/lost-found">报失寻主</Link></li>
          <li className="breadcrumb-item active">发布信息</li>
        </ol>
      </nav>

      <h2 className="mb-4"><i className="fas fa-edit me-2 text-success"></i>发布报失/寻主信息</h2>
=======
          <li className="breadcrumb-item"><Link to="/lost-found">鎶ュけ瀵讳富</Link></li>
          <li className="breadcrumb-item active">鍙戝竷淇℃伅</li>
        </ol>
      </nav>

      <h2 className="mb-4"><i className="fas fa-edit me-2 text-success"></i>鍙戝竷鎶ュけ/瀵讳富淇℃伅</h2>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit} className="card shadow-sm">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-12">
<<<<<<< HEAD
              <label className="form-label d-block">类型 <span className="text-danger">*</span></label>
=======
              <label className="form-label d-block">绫诲瀷 <span className="text-danger">*</span></label>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              <div className="btn-group w-100 flex-wrap" role="group">
                {Object.entries(LOST_FOUND_TYPE).map(([key, label]) => (
                  <button
                    key={key}
                    type="button"
                    className={`btn flex-fill ${form.post_type === key ? 'btn-success' : 'btn-outline-secondary'}`}
                    onClick={() => setForm((f) => ({ ...f, post_type: key }))}
                  >
                    {label}
<<<<<<< HEAD
                    <small className="d-block opacity-75">{key === 'lost' ? '宠物走失' : '发现流浪/招领'}</small>
=======
                    <small className="d-block opacity-75">{key === 'lost' ? '瀹犵墿璧板け' : '鍙戠幇娴佹氮/鎷涢'}</small>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                  </button>
                ))}
              </div>
            </div>
            <div className="col-md-6">
<<<<<<< HEAD
              <label className="form-label">宠物种类</label>
              <input type="text" name="pet_species" className="form-control" value={form.pet_species} onChange={handleChange} required placeholder="如：中华田园猫" />
            </div>
            <div className="col-12">
              <label className="form-label">特征描述</label>
              <button type="button" className="btn btn-outline-success btn-sm mb-2" onClick={async () => {
                if (!photoUrls[0]) { alert('请先上传照片'); return; }
=======
              <label className="form-label">瀹犵墿绉嶇被</label>
              <input type="text" name="pet_species" className="form-control" value={form.pet_species} onChange={handleChange} required placeholder="濡傦細涓崕鐢板洯鐚�" />
            </div>
            <div className="col-12">
              <label className="form-label">鐗瑰緛鎻忚堪</label>
              <button type="button" className="btn btn-outline-success btn-sm mb-2" onClick={async () => {
                if (!photoUrls[0]) { alert('璇峰厛涓婁紶鐓х墖'); return; }
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                try {
                  const res = await aiAPI.breedDetect({
                    image_url: photoUrls[0],
                    description: `${form.pet_species} ${form.features}`,
                  });
                  const parts = [
<<<<<<< HEAD
                    res.data.species && `物种：${res.data.species}`,
                    res.data.breed && `品种：${res.data.breed}`,
                    res.data.summary && res.data.summary !== '不确定' && `特征：${res.data.summary}`,
                  ].filter(Boolean);
                  setForm((f) => ({ ...f, features: parts.join('；') || res.data.result || f.features }));
                } catch (err) { alert(err.response?.data?.detail || 'AI 失败'); }
              }}>AI 识图辅助特征</button>
              <textarea name="features" className="form-control" rows={4} value={form.features} onChange={handleChange} required placeholder="毛色、体型、特殊标记等" />
            </div>

            {/* ========== 事发地点（地图选点 + 高德搜索） ========== */}
            <div className="col-12">
              <label className="form-label">
                事发地点 <small className="text-muted">（搜索地点，或在地图上点击/拖动标记精确定位）</small>
              </label>

              {/* 搜索框 + 操作按钮 */}
=======
                    res.data.species && `鐗╃锛�${res.data.species}`,
                    res.data.breed && `鍝佺锛�${res.data.breed}`,
                    res.data.summary && res.data.summary !== '涓嶇‘瀹�' && `鐗瑰緛锛�${res.data.summary}`,
                  ].filter(Boolean);
                  setForm((f) => ({ ...f, features: parts.join('锛�') || res.data.result || f.features }));
                } catch (err) { alert(err.response?.data?.detail || 'AI 澶辫触'); }
              }}>AI 璇嗗浘杈呭姪鐗瑰緛</button>
              <textarea name="features" className="form-control" rows={4} value={form.features} onChange={handleChange} required placeholder="姣涜壊銆佷綋鍨嬨€佺壒娈婃爣璁扮瓑" />
            </div>

            {/* ========== 浜嬪彂鍦扮偣锛堝湴鍥鹃€夌偣 + 楂樺痉鎼滅储锛� ========== */}
            <div className="col-12">
              <label className="form-label">
                浜嬪彂鍦扮偣 <small className="text-muted">锛堟悳绱㈠湴鐐癸紝鎴栧湪鍦板浘涓婄偣鍑�/鎷栧姩鏍囪绮剧‘瀹氫綅锛�</small>
              </label>

              {/* 鎼滅储妗� + 鎿嶄綔鎸夐挳 */}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              <div className="mb-2 position-relative" ref={dropdownRef}>
                <div className="d-flex flex-wrap align-items-center gap-2">
                  <div className="position-relative flex-grow-1" style={{ maxWidth: 500 }}>
                    <input
                      type="text"
                      className="form-control form-control-sm"
<<<<<<< HEAD
                      placeholder="搜索地点名称（如：春熙路、天府广场）"
=======
                      placeholder="鎼滅储鍦扮偣鍚嶇О锛堝锛氭槬鐔欒矾銆佸ぉ搴滃箍鍦猴級"
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                      value={searchQuery}
                      onChange={handleSearchInput}
                      onFocus={() => { if (searchResults.length > 0) setShowDropdown(true); }}
                    />
                    {searching && (
                      <span className="position-absolute end-0 top-50 translate-middle-y me-2">
                        <span className="spinner-border spinner-border-sm" role="status" />
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    className="btn btn-outline-success btn-sm"
                    onClick={handleUseCurrentLocation}
                    disabled={locating || submitting}
                  >
                    {locating ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
<<<<<<< HEAD
                        定位中...
=======
                        瀹氫綅涓�...
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                      </>
                    ) : (
                      <>
                        <i className="fas fa-location-arrow me-1" />
<<<<<<< HEAD
                        定位到我
=======
                        瀹氫綅鍒版垜
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                      </>
                    )}
                  </button>
                  {hasCoordinates() && (
<<<<<<< HEAD
                    <span className="badge bg-light text-success border">已定位</span>
                  )}
                </div>

                {/* 搜索下拉结果 */}
=======
                    <span className="badge bg-light text-success border">宸插畾浣�</span>
                  )}
                </div>

                {/* 鎼滅储涓嬫媺缁撴灉 */}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                {showDropdown && (
                  <ul
                    className="list-group position-absolute top-100 start-0 w-100 shadow-sm"
                    style={{ zIndex: 9999, maxWidth: 500, maxHeight: 280, overflowY: 'auto' }}
                  >
                    {searchResults.map((poi) => (
                      <li
                        key={poi.id}
                        className="list-group-item list-group-item-action py-2 px-3"
                        style={{ cursor: 'pointer', fontSize: 14 }}
                        onClick={() => handleSelectResult(poi)}
                      >
                        <div className="fw-medium">{poi.name}</div>
                        {poi.address && (
                          <div className="text-muted small">{poi.address}</div>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

<<<<<<< HEAD
              {/* 地址详情输入框 */}
=======
              {/* 鍦板潃璇︽儏杈撳叆妗� */}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              <input
                type="text"
                name="address_text"
                className="form-control form-control-sm mb-2"
                value={form.address_text}
                onChange={(e) => {
                  setForm({ ...form, address_text: e.target.value });
                  setSearchQuery(e.target.value);
                }}
                required
<<<<<<< HEAD
                placeholder="详细地址（自动填充，可手动修改）"
=======
                placeholder="璇︾粏鍦板潃锛堣嚜鍔ㄥ～鍏咃紝鍙墜鍔ㄤ慨鏀癸級"
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              />

              {locationHint && <small className="text-muted d-block mb-2">{locationHint}</small>}

<<<<<<< HEAD
              {/* Leaflet 地图 */}
=======
              {/* Leaflet 鍦板浘 */}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              <div
                ref={mapRef}
                style={{ width: '100%', height: 350, borderRadius: 8, border: '1px solid #ddd' }}
              />
            </div>

            <div className="col-md-6">
<<<<<<< HEAD
              <label className="form-label">悬赏金额（元）</label>
              <input type="number" step="0.01" min="0" name="reward_amount" className="form-control" value={form.reward_amount} onChange={handleChange} />
            </div>
            <div className="col-md-6">
              <label className="form-label">联系电话</label>
              <input type="tel" name="contact_phone" className="form-control" value={form.contact_phone} onChange={handleChange} placeholder="可选" />
            </div>
            <div className="col-12">
              <label className="form-label">照片 <span className="text-danger">*</span> <small className="text-muted">(至少 1 张)</small></label>
              <input type="file" className="form-control" accept="image/*" multiple onChange={handlePhotoUpload} disabled={uploading} />
              {uploading && <small className="text-muted">上传中...</small>}
=======
              <label className="form-label">鎮祻閲戦锛堝厓锛�</label>
              <input type="number" step="0.01" min="0" name="reward_amount" className="form-control" value={form.reward_amount} onChange={handleChange} />
            </div>
            <div className="col-md-6">
              <label className="form-label">鑱旂郴鐢佃瘽</label>
              <input type="tel" name="contact_phone" className="form-control" value={form.contact_phone} onChange={handleChange} placeholder="鍙€�" />
            </div>
            <div className="col-12">
              <label className="form-label">鐓х墖 <span className="text-danger">*</span> <small className="text-muted">(鑷冲皯 1 寮�)</small></label>
              <input type="file" className="form-control" accept="image/*" multiple onChange={handlePhotoUpload} disabled={uploading} />
              {uploading && <small className="text-muted">涓婁紶涓�...</small>}
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              {photoUrls.length > 0 && (
                <div className="d-flex flex-wrap gap-2 mt-2">
                  {photoUrls.map((url, idx) => (
                    <div key={url} className="position-relative">
                      <img src={url} alt="" style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 8 }} />
<<<<<<< HEAD
                      <button type="button" className="btn btn-danger btn-sm position-absolute top-0 end-0" style={{ padding: '0 4px', fontSize: 10 }} onClick={() => removePhoto(idx)}>×</button>
=======
                      <button type="button" className="btn btn-danger btn-sm position-absolute top-0 end-0" style={{ padding: '0 4px', fontSize: 10 }} onClick={() => removePhoto(idx)}>脳</button>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="card-footer">
          {photoError && <div className="alert alert-danger py-2 mb-2">{photoError}</div>}
          <div className="d-flex gap-2">
          <button type="submit" className="btn btn-success" disabled={submitting || uploading}>
<<<<<<< HEAD
            {submitting ? '提交中...' : '发布'}
          </button>
          <Link to="/lost-found" className="btn btn-outline-secondary">取消</Link>
=======
            {submitting ? '鎻愪氦涓�...' : '鍙戝竷'}
          </button>
          <Link to="/lost-found" className="btn btn-outline-secondary">鍙栨秷</Link>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
          </div>
        </div>
      </form>
    </div>
  );
};

export default LostFoundPublish;
