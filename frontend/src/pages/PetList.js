import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { petsAPI } from '../api/api';
import { ADOPTION_STATUS } from '../constants/site';
import AdminManageBar from '../components/AdminManageBar';
import { useManageMode } from '../context/ManageModeContext';
import { reverseAmapLocation } from '../utils/amapLocation';

const SPECIES_LABELS = {
  dog: '狗',
  cat: '猫',
  bird: '鸟',
  rabbit: '兔',
  fish: '鱼',
  other: '其他',
};

const GENDER_LABELS = {
  male: '公',
  female: '母',
  unknown: '未知',
};

const AGE_STAGE_OPTIONS = [
  { value: '', label: '不限阶段', min: null, max: null },
  { value: 'baby', label: '幼龄（0-6个月）', min: 0, max: 6 },
  { value: 'young', label: '青年（7-24个月）', min: 7, max: 24 },
  { value: 'adult', label: '成年（25-84个月）', min: 25, max: 84 },
  { value: 'senior', label: '高龄（85个月以上）', min: 85, max: null },
];

const NON_DOG_SPECIES = ['cat', 'bird', 'rabbit', 'fish', 'other'];

const HEALTH_STATUS_LABELS = {
  vaccinated: '已接种疫苗',
  neutered: '已绝育',
  spayed: '已绝育',
  dewormed: '已驱虫',
  healthy: '健康',
  'minor injury': '轻微伤病',
  minor_injury: '轻微伤病',
  'severe injury': '严重伤病',
  severe_injury: '严重伤病',
  injured: '有伤病',
  'under treatment': '治疗中',
  under_treatment: '治疗中',
  recovered: '已康复',
  unknown: '未知',
};

const ADOPTION_BADGE = {
  available: 'success',
  pending: 'warning text-dark',
  adopted: 'secondary',
};

const CITY_TO_PROVINCE = {
  '北京市': '北京市',
  '天津市': '天津市',
  '上海市': '上海市',
  '重庆市': '重庆市',
  '成都市': '四川省',
  '绵阳市': '四川省',
  '广州市': '广东省',
  '深圳市': '广东省',
  '佛山市': '广东省',
  '杭州市': '浙江省',
  '宁波市': '浙江省',
  '南京市': '江苏省',
  '苏州市': '江苏省',
  '无锡市': '江苏省',
  '武汉市': '湖北省',
  '长沙市': '湖南省',
  '西安市': '陕西省',
  '郑州市': '河南省',
  '济南市': '山东省',
  '青岛市': '山东省',
  '福州市': '福建省',
  '厦门市': '福建省',
  '昆明市': '云南省',
  '南宁市': '广西壮族自治区',
  '贵阳市': '贵州省',
  '哈尔滨市': '黑龙江省',
  '长春市': '吉林省',
  '沈阳市': '辽宁省',
  '合肥市': '安徽省',
  '南昌市': '江西省',
  '太原市': '山西省',
  '兰州市': '甘肃省',
  '石家庄市': '河北省',
  '海口市': '海南省',
  '呼和浩特市': '内蒙古自治区',
  '拉萨市': '西藏自治区',
  '银川市': '宁夏回族自治区',
  '西宁市': '青海省',
  '乌鲁木齐市': '新疆维吾尔自治区',
  '香港': '香港特别行政区',
  '澳门': '澳门特别行政区',
};

const CHINA_PROVINCES = [
  '北京市', '天津市', '上海市', '重庆市',
  '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省',
  '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省',
  '河南省', '湖北省', '湖南省', '广东省', '海南省',
  '四川省', '贵州省', '云南省', '陕西省', '甘肃省', '青海省',
  '台湾省',
  '内蒙古自治区', '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区',
  '香港特别行政区', '澳门特别行政区',
];

const inferRegionFromAddress = (address = '') => {
  const text = String(address || '');
  const provinceMatch = text.match(/([^省]+省|.+自治区|上海市|北京市|天津市|重庆市)/);
  const cityMatch = text.match(/([^市]+市|[^州]+州|[^地区]+地区)/);
  const city = cityMatch ? cityMatch[1] : '';
  const inferredProvince = provinceMatch ? provinceMatch[1] : (CITY_TO_PROVINCE[city] || '');
  return {
    country: text ? '中国' : '',
    province: inferredProvince,
    city,
  };
};

const normalizeRegion = (pet) => {
  const fallback = inferRegionFromAddress(pet.rescue_case_address);
  return {
    ...pet,
    country: pet.country || fallback.country,
    province: pet.province || fallback.province,
    city: pet.city || fallback.city,
  };
};

const getRegionDisplay = (pet) => {
  const normalized = normalizeRegion(pet);
  const region = [normalized.country, normalized.province, normalized.city].filter(Boolean).join(' / ');
  if (region) return region;
  return normalized.rescue_case_address || '未知';
};

const formatHealthStatus = (status) => {
  if (!status) return null;
  if (/[\u4e00-\u9fff]/.test(status)) return status;
  const lower = status.toLowerCase().trim();
  return HEALTH_STATUS_LABELS[lower] || status;
};

const formatSizeDisplay = (pet) => {
  if (pet.size_category_display) return pet.size_category_display;
  if (pet.species === 'dog') return null;
  if (NON_DOG_SPECIES.includes(pet.species)) return '小型';
  return null;
};

const formatAgeMonths = (months) => {
  if (months == null || months === '') return '未知';
  const m = Number(months);
  if (m < 12) return `${m}个月`;
  const years = Math.floor(m / 12);
  const rem = m % 12;
  if (rem === 0) return `${years}岁`;
  return `${years}岁${rem}个月`;
};

const buildRegionOptions = (pets) => {
  const normalizedPets = pets.map(normalizeRegion);
  const countries = [...new Set(normalizedPets.map((p) => p.country).filter(Boolean))].sort();
  if (normalizedPets.length > 0 && !countries.includes('中国')) {
    countries.unshift('中国');
  }
  const provinces = [...new Set(normalizedPets.map((p) => p.province).filter(Boolean))].sort();
  const cities = [...new Set(normalizedPets.map((p) => p.city).filter(Boolean))].sort();
  return { countries, provinces, cities };
};

const PetList = () => {
  const navigate = useNavigate();
  const { canManage } = useManageMode();
  const [searchParams, setSearchParams] = useSearchParams();

  const [pets, setPets] = useState([]);
  const [allAvailablePets, setAllAvailablePets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchText, setSearchText] = useState(searchParams.get('search') || '');
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [speciesFilter, setSpeciesFilter] = useState(searchParams.get('species') || '');
  const [genderFilter, setGenderFilter] = useState(searchParams.get('gender') || '');
  const [countryFilter, setCountryFilter] = useState(searchParams.get('country') || '');
  const [provinceFilter, setProvinceFilter] = useState(searchParams.get('province') || '');
  const [cityFilter, setCityFilter] = useState(searchParams.get('city') || '');
  const [ageMode, setAgeMode] = useState(searchParams.get('age_mode') || 'stage');
  const [ageStage, setAgeStage] = useState(searchParams.get('age_stage') || '');
  const [customAgeMin, setCustomAgeMin] = useState(searchParams.get('age_min') || '');
  const [customAgeMax, setCustomAgeMax] = useState(searchParams.get('age_max') || '');

  // 本地输入状态：仅在回车或失焦时才提交到上面的筛选状态，避免每次按键都触发 API 请求
  const [ageMinInput, setAgeMinInput] = useState(searchParams.get('age_min') || '');
  const [ageMaxInput, setAgeMaxInput] = useState(searchParams.get('age_max') || '');

  const [nearbyMode, setNearbyMode] = useState(searchParams.get('nearby') === 'true');
  const [radiusKm, setRadiusKm] = useState(searchParams.get('radius_km') || '10');
  const [nearbyLoading, setNearbyLoading] = useState(false);
  const [locationHint, setLocationHint] = useState('');
  const [userLocation, setUserLocation] = useState({
    lat: null,
    lon: null,
    province: '',
    city: '',
  });

  const regionOptions = useMemo(() => buildRegionOptions(allAvailablePets), [allAvailablePets]);
  const normalizedAllPets = useMemo(() => allAvailablePets.map(normalizeRegion), [allAvailablePets]);

  const fetchAllAvailablePets = useCallback(async () => {
    const response = await petsAPI.getAll({ adoption_status: 'available' });
    const list = Array.isArray(response.data) ? response.data : response.data.results || [];
    setAllAvailablePets(list);
  }, []);

  const buildCommonParams = useCallback(() => {
    const params = { adoption_status: 'available' };
    if (search) params.search = search;
    if (speciesFilter) params.species = speciesFilter;
    if (genderFilter) params.gender = genderFilter;
    if (countryFilter) params.country = countryFilter;
    if (provinceFilter) params.province = provinceFilter;
    if (cityFilter) params.city = cityFilter;
    if (ageMode === 'stage' && ageStage) {
      const selected = AGE_STAGE_OPTIONS.find((item) => item.value === ageStage);
      if (selected?.min != null) params.age_min = selected.min;
      if (selected?.max != null) params.age_max = selected.max;
    } else if (ageMode === 'custom') {
      if (customAgeMin !== '') params.age_min = customAgeMin;
      if (customAgeMax !== '') params.age_max = customAgeMax;
    }
    return params;
  }, [
    ageMode,
    ageStage,
    cityFilter,
    countryFilter,
    customAgeMax,
    customAgeMin,
    genderFilter,
    provinceFilter,
    search,
    speciesFilter,
  ]);

  const fetchPets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (nearbyMode) {
        if (!userLocation.lat || !userLocation.lon) {
          setPets([]);
          setLoading(false);
          return;
        }
        setNearbyLoading(true);
        const params = {
          ...buildCommonParams(),
          lat: userLocation.lat,
          lon: userLocation.lon,
          radius_km: radiusKm,
          same_province: true,
        };
        const provinceForNearby = provinceFilter || userLocation.province;
        if (provinceForNearby) {
          params.province = provinceForNearby;
        }
        if (userLocation.city) {
          params.city = userLocation.city;
        }
        const response = await petsAPI.getNearby(params);
        setPets(Array.isArray(response.data) ? response.data : []);
      } else {
        const response = await petsAPI.getAll(buildCommonParams());
        setPets(Array.isArray(response.data) ? response.data : response.data.results || []);
      }
    } catch (err) {
      setError('加载宠物列表失败，请稍后重试。');
      console.error(err);
    } finally {
      setNearbyLoading(false);
      setLoading(false);
    }
  }, [buildCommonParams, nearbyMode, provinceFilter, radiusKm, userLocation.city, userLocation.lat, userLocation.lon, userLocation.province]);

  useEffect(() => {
    fetchAllAvailablePets().catch((err) => console.error(err));
  }, [fetchAllAvailablePets]);

  useEffect(() => {
    fetchPets();
  }, [fetchPets]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (speciesFilter) params.set('species', speciesFilter);
    if (genderFilter) params.set('gender', genderFilter);
    if (countryFilter) params.set('country', countryFilter);
    if (provinceFilter) params.set('province', provinceFilter);
    if (cityFilter) params.set('city', cityFilter);
    params.set('age_mode', ageMode);
    if (ageMode === 'stage' && ageStage) params.set('age_stage', ageStage);
    if (ageMode === 'custom') {
      if (customAgeMin !== '') params.set('age_min', customAgeMin);
      if (customAgeMax !== '') params.set('age_max', customAgeMax);
    }
    if (nearbyMode) {
      params.set('nearby', 'true');
      params.set('radius_km', radiusKm);
    }
    setSearchParams(params, { replace: true });
  }, [
    ageMode,
    ageStage,
    cityFilter,
    countryFilter,
    customAgeMax,
    customAgeMin,
    genderFilter,
    nearbyMode,
    provinceFilter,
    radiusKm,
    search,
    setSearchParams,
    speciesFilter,
  ]);

  const handleConfirmSearch = () => {
    setSearch(searchText.trim());
  };

  const handleCustomAgeInput = (setter) => (event) => {
    const next = event.target.value.replace(/[^\d]/g, '');
    setter(next);
  };

  const handleConfirmAge = () => {
    setCustomAgeMin(ageMinInput);
    setCustomAgeMax(ageMaxInput);
  };

  const handleNearbySearch = () => {
    if (!navigator.geolocation) {
      setError('当前浏览器不支持定位，请更换浏览器重试。');
      return;
    }
    setError(null);
    setLocationHint('正在获取当前位置...');
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = Number(position.coords.latitude.toFixed(6));
        const lon = Number(position.coords.longitude.toFixed(6));
        let province = '';
        let city = '';
        try {
          const region = await reverseAmapLocation(lat, lon);
          province = region?.province || '';
          city = region?.city || '';
        } catch (err) {
          console.warn(err);
        }
        setUserLocation({ lat, lon, province, city });
        setNearbyMode(true);
        if (!provinceFilter && province) {
          setProvinceFilter(province);
        }
        setLocationHint(
          province
            ? `已定位：${province}${city ? ` ${city}` : ''}（附近搜索默认同省）`
            : '已定位：未识别省份，将按半径搜索'
        );
      },
      (geoErr) => {
        setLocationHint('');
        const message = geoErr.code === 1
          ? '定位权限被拒绝，请在浏览器设置中允许定位。'
          : '定位失败，请稍后重试。';
        setError(message);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  const clearFilters = () => {
    setSearchText('');
    setSearch('');
    setSpeciesFilter('');
    setGenderFilter('');
    setCountryFilter('');
    setProvinceFilter('');
    setCityFilter('');
    setAgeMode('stage');
    setAgeStage('');
    setCustomAgeMin('');
    setCustomAgeMax('');
    setAgeMinInput('');
    setAgeMaxInput('');
    setNearbyMode(false);
    setRadiusKm('10');
    setLocationHint('');
  };

  const hasActiveFilters = Boolean(
    search ||
      speciesFilter ||
      genderFilter ||
      countryFilter ||
      provinceFilter ||
      cityFilter ||
      ageStage ||
      customAgeMin ||
      customAgeMax ||
      nearbyMode
  );

  const filteredProvinceOptions = useMemo(() => {
    if (!countryFilter) return regionOptions.provinces;
    if (countryFilter === '中国') {
      const merged = [...new Set([...regionOptions.provinces, ...CHINA_PROVINCES])];
      return merged.sort();
    }
    return [
      ...new Set(
        normalizedAllPets
          .filter((p) => p.country === countryFilter)
          .map((p) => p.province)
          .filter(Boolean)
      ),
    ].sort();
  }, [normalizedAllPets, countryFilter, regionOptions.provinces]);

  const filteredCityOptions = useMemo(() => {
    return [
      ...new Set(
        normalizedAllPets
          .filter((p) => (!countryFilter || p.country === countryFilter))
          .filter((p) => (!provinceFilter || p.province === provinceFilter))
          .map((p) => p.city)
          .filter(Boolean)
      ),
    ].sort();
  }, [normalizedAllPets, countryFilter, provinceFilter]);

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">加载中...</span>
        </div>
        <p className="mt-2">正在加载宠物列表...</p>
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="pet-list-container">
      <div className="search-filter-section mb-4">
        <div className="container">
          <div className="row g-3 mb-3">
            <div className="col-md-9">
              <input
                type="text"
                className="form-control search-input"
                placeholder="按宠物名称搜索..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleConfirmSearch()}
              />
            </div>
            <div className="col-md-3">
              <button className="btn btn-success w-100" onClick={handleConfirmSearch}>
                搜索
              </button>
            </div>
          </div>

          <div className="row g-2 mb-2">
            <div className="col-6 col-md-2">
              <select className="form-select" value={speciesFilter} onChange={(e) => setSpeciesFilter(e.target.value)}>
                <option value="">全部物种</option>
                <option value="dog">狗</option>
                <option value="cat">猫</option>
                <option value="bird">鸟</option>
                <option value="rabbit">兔</option>
                <option value="fish">鱼</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div className="col-6 col-md-2">
              <select className="form-select" value={genderFilter} onChange={(e) => setGenderFilter(e.target.value)}>
                <option value="">全部性别</option>
                <option value="male">公</option>
                <option value="female">母</option>
              </select>
            </div>
            <div className="col-6 col-md-2">
              <select className="form-select" value={countryFilter} onChange={(e) => {
                setCountryFilter(e.target.value);
                setProvinceFilter('');
                setCityFilter('');
              }}>
                <option value="">国家</option>
                {regionOptions.countries.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>
            <div className="col-6 col-md-2">
              <select className="form-select" value={provinceFilter} onChange={(e) => {
                setProvinceFilter(e.target.value);
                setCityFilter('');
              }}>
                <option value="">省份</option>
                {filteredProvinceOptions.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>
            <div className="col-6 col-md-2">
              <select className="form-select" value={cityFilter} onChange={(e) => setCityFilter(e.target.value)}>
                <option value="">城市</option>
                {filteredCityOptions.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>
            <div className="col-6 col-md-2">
              <button className="btn btn-outline-secondary w-100" onClick={clearFilters} disabled={!hasActiveFilters}>
                清空筛选
              </button>
            </div>
          </div>

          <div className="row g-2 mb-2">
            <div className="col-12 col-md-2">
              <select className="form-select" value={ageMode} onChange={(e) => setAgeMode(e.target.value)}>
                <option value="stage">按阶段</option>
                <option value="custom">自定义范围</option>
              </select>
            </div>
            {ageMode === 'stage' ? (
              <div className="col-12 col-md-4">
                <select className="form-select" value={ageStage} onChange={(e) => setAgeStage(e.target.value)}>
                  {AGE_STAGE_OPTIONS.map((item) => (
                    <option key={item.value || 'all'} value={item.value}>{item.label}</option>
                  ))}
                </select>
              </div>
            ) : (
              <>
                <div className="col-6 col-md-2">
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    className="form-control"
                    placeholder="最小月龄"
                    value={ageMinInput}
                    onChange={handleCustomAgeInput(setAgeMinInput)}
                    onKeyDown={(e) => e.key === 'Enter' && handleConfirmAge()}
                    onBlur={handleConfirmAge}
                  />
                </div>
                <div className="col-6 col-md-2">
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    className="form-control"
                    placeholder="最大月龄"
                    value={ageMaxInput}
                    onChange={handleCustomAgeInput(setAgeMaxInput)}
                    onKeyDown={(e) => e.key === 'Enter' && handleConfirmAge()}
                    onBlur={handleConfirmAge}
                  />
                </div>
              </>
            )}
            <div className="col-6 col-md-2">
              <select
                className="form-select"
                value={radiusKm}
                onChange={(e) => setRadiusKm(e.target.value)}
              >
                <option value="3">3 公里</option>
                <option value="5">5 公里</option>
                <option value="10">10 公里</option>
                <option value="20">20 公里</option>
                <option value="50">50 公里</option>
              </select>
            </div>
            <div className="col-6 col-md-2">
              <button
                className={`btn w-100 ${nearbyMode ? 'btn-success' : 'btn-outline-success'}`}
                onClick={handleNearbySearch}
                disabled={nearbyLoading}
              >
                {nearbyLoading ? '搜索中...' : '附近搜索'}
              </button>
            </div>
            {nearbyMode && (
              <div className="col-12 col-md-2">
                <button className="btn btn-outline-secondary w-100" onClick={() => setNearbyMode(false)}>
                  关闭附近
                </button>
              </div>
            )}
          </div>
          {locationHint && <small className="text-muted">{locationHint}</small>}
        </div>
      </div>

      <div className="container mb-4 d-flex justify-content-between align-items-center">
        <h5 className="text-muted mb-0">
          共找到 <strong className="text-success">{pets.length}</strong> 只可领养宠物
        </h5>
        <Link to="/my-applications" className="btn btn-outline-success btn-sm">
          我的申请与核验
        </Link>
      </div>

      <div className="container">
        <div className="row">
          {pets.map((pet) => (
            <div key={pet.id} className="col-md-4 col-lg-3 mb-4">
              <div className="pet-card" onClick={() => navigate(`/pets/${pet.id}`)} style={{ cursor: 'pointer' }}>
                <div className="pet-card-img-wrapper">
                  <img
                    src={pet.photo_url || 'https://via.placeholder.com/300x200?text=Pet+Photo'}
                    className="pet-card-img"
                    alt={pet.name || '宠物'}
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/300x200?text=Pet+Photo';
                    }}
                  />
                </div>
                <div className="pet-card-body">
                  <div className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2" onClick={(e) => e.stopPropagation()}>
                    <span className={`badge bg-${ADOPTION_BADGE[pet.adoption_status] || 'secondary'}`}>
                      {ADOPTION_STATUS[pet.adoption_status] || '未知'}
                    </span>
                    <div className="flex-grow-1">
                      <AdminManageBar
                        compact
                        onEdit={() => navigate(`/add-pet?edit=${pet.id}`)}
                        onHide={async () => {
                          try {
                            await petsAPI.update(pet.id, { is_public: false });
                            fetchPets();
                          } catch (err) {
                            alert(err.response?.data?.detail || '操作失败');
                          }
                        }}
                        onDelete={async () => {
                          if (!window.confirm('确定删除？')) return;
                          try {
                            await petsAPI.delete(pet.id);
                            fetchPets();
                          } catch (err) {
                            alert(err.response?.data?.detail || '删除失败');
                          }
                        }}
                      />
                    </div>
                  </div>
                  <h5 className="pet-card-title">
                    {pet.name || '未命名宠物'}
                  </h5>
                  <div className="pet-card-info">
                    <div className="info-row"><span className="info-label">物种</span><span className="info-value">{SPECIES_LABELS[pet.species] || pet.species || '未知'}</span></div>
                    <div className="info-row"><span className="info-label">性别</span><span className="info-value">{GENDER_LABELS[pet.gender] || pet.gender || '未知'}</span></div>
                    <div className="info-row"><span className="info-label">年龄</span><span className="info-value">{formatAgeMonths(pet.age_months)}</span></div>
                    {formatSizeDisplay(pet) && <div className="info-row"><span className="info-label">体型</span><span className="info-value">{formatSizeDisplay(pet)}</span></div>}
                    <div className="info-row"><span className="info-label">地区</span><span className="info-value">{getRegionDisplay(pet)}</span></div>
                    {pet.distance_km != null && <div className="info-row"><span className="info-label">距离</span><span className="info-value">{pet.distance_km} km</span></div>}
                    {pet.health_status && <div className="info-row"><span className="info-label">健康</span><span className="info-value">{formatHealthStatus(pet.health_status)}</span></div>}
                  </div>
                  {canManage && !pet.is_public && <span className="badge bg-secondary mt-2">未公开</span>}
                </div>
              </div>
            </div>
          ))}
          {pets.length === 0 && (
            <div className="text-center py-5">
              <p className="text-muted">没有符合筛选条件的可领养宠物。</p>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .pet-list-container {
          background-color: #fafafa;
          min-height: 100vh;
          padding-top: 2rem;
        }
        .search-filter-section {
          background: #fff;
          border-radius: 16px;
          padding: 1.5rem 2rem;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        }
        .search-input {
          border-radius: 25px;
          border: 2px solid #e9ecef;
          height: 44px;
        }
        .pet-card {
          background: #fff;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
          transition: all 0.3s ease;
          height: 100%;
        }
        .pet-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }
        .pet-card-img {
          width: 100%;
          height: 200px;
          object-fit: cover;
        }
        .pet-card-body {
          padding: 1rem;
        }
        .pet-card-title {
          color: #333;
          font-size: 1.15rem;
          margin-bottom: 0.75rem;
        }
        .info-row {
          display: flex;
          font-size: 0.85rem;
          margin-bottom: 0.25rem;
        }
        .info-label {
          min-width: 52px;
          color: #999;
        }
        .info-value {
          color: #555;
          flex: 1;
        }
      `}</style>
    </div>
  );
};

export default PetList;
