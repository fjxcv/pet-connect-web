<<<<<<< HEAD
import React, { useEffect, useState, useCallback } from 'react';
=======
import React, { useCallback, useEffect, useMemo, useState } from 'react';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { petsAPI } from '../api/api';
import { ADOPTION_STATUS } from '../constants/site';
import AdminManageBar from '../components/AdminManageBar';
import { useManageMode } from '../context/ManageModeContext';
<<<<<<< HEAD

// ===== 常量定义 =====
=======
import { reverseAmapLocation } from '../utils/amapLocation';
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

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

<<<<<<< HEAD
const AGE_RANGE_OPTIONS = [
  { value: '', label: '不限年龄' },
  { value: '0-6', label: '0-6个月（幼崽）' },
  { value: '6-12', label: '6-12个月（青少年）' },
  { value: '12-36', label: '1-3岁（成年）' },
  { value: '36-999', label: '3岁以上（中老年）' },
];

const SIZE_LABELS = {
  small: '小型',
  medium: '中型',
  large: '大型',
};

// 非犬类物种通常体型较小
const NON_DOG_SPECIES = ['cat', 'bird', 'rabbit', 'fish', 'other'];

// 健康状态中英文映射
=======
const AGE_STAGE_OPTIONS = [
  { value: '', label: '不限阶段', min: null, max: null },
  { value: 'baby', label: '幼龄（0-6个月）', min: 0, max: 6 },
  { value: 'young', label: '青年（7-24个月）', min: 7, max: 24 },
  { value: 'adult', label: '成年（25-84个月）', min: 25, max: 84 },
  { value: 'senior', label: '高龄（85个月以上）', min: 85, max: null },
];

const NON_DOG_SPECIES = ['cat', 'bird', 'rabbit', 'fish', 'other'];

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
const HEALTH_STATUS_LABELS = {
  vaccinated: '已接种疫苗',
  neutered: '已绝育',
  spayed: '已绝育',
  dewormed: '已驱虫',
  healthy: '健康',
  'minor injury': '轻微伤病',
<<<<<<< HEAD
  'minor_injury': '轻微伤病',
  'severe injury': '严重伤病',
  'severe_injury': '严重伤病',
  injured: '有伤病',
  'under treatment': '治疗中',
  'under_treatment': '治疗中',
=======
  minor_injury: '轻微伤病',
  'severe injury': '严重伤病',
  severe_injury: '严重伤病',
  injured: '有伤病',
  'under treatment': '治疗中',
  under_treatment: '治疗中',
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  recovered: '已康复',
  unknown: '未知',
};

<<<<<<< HEAD
// 格式化健康状态为中文显示
const formatHealthStatus = (status) => {
  if (!status) return null;
  // 如果已经是中文（包含中文字符），直接返回
  if (/[一-龥]/.test(status)) return status;
  // 尝试映射英文值（大小写不敏感）
  const lower = status.toLowerCase().trim();
  if (HEALTH_STATUS_LABELS[lower]) return HEALTH_STATUS_LABELS[lower];
  // 尝试逐一替换英文关键词
  let result = status;
  for (const [en, zh] of Object.entries(HEALTH_STATUS_LABELS)) {
    if (en.length > 3 && lower.includes(en)) {
      // 用正则替换，避免重复添加
      const regex = new RegExp(en.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      if (regex.test(result)) {
        result = result.replace(regex, zh);
      }
    }
  }
  // 如果替换后仍无中文，返回原值；否则返回替换结果
  return /[一-龥]/.test(result) ? result : status;
};

// 格式化体型显示：优先使用 size_category_display，否则根据物种推断
const formatSizeDisplay = (pet) => {
  if (pet.size_category_display) return pet.size_category_display;
  // 犬类没有填写体型时显示"未知"，非犬类默认"小型"
=======
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
  if (/[一-龥]/.test(status)) return status;
  const lower = status.toLowerCase().trim();
  return HEALTH_STATUS_LABELS[lower] || status;
};

const formatSizeDisplay = (pet) => {
  if (pet.size_category_display) return pet.size_category_display;
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  if (pet.species === 'dog') return null;
  if (NON_DOG_SPECIES.includes(pet.species)) return '小型';
  return null;
};

<<<<<<< HEAD
// 英文城市名 → 中文映射（兜底用）
const CITY_NAME_MAP = {
  chengdu: '成都市',
  beijing: '北京市',
  shanghai: '上海市',
  guangzhou: '广州市',
  shenzhen: '深圳市',
  hangzhou: '杭州市',
  nanjing: '南京市',
  wuhan: '武汉市',
  chongqing: '重庆市',
  xian: '西安市',
  changsha: '长沙市',
  zhengzhou: '郑州市',
  jinan: '济南市',
  qingdao: '青岛市',
  dalian: '大连市',
  xiamen: '厦门市',
  suzhou: '苏州市',
  kunming: '昆明市',
  fuzhou: '福州市',
  hefei: '合肥市',
  nanchang: '南昌市',
  taiyuan: '太原市',
  lanzhou: '兰州市',
  guiyang: '贵阳市',
  nanning: '南宁市',
  haerbin: '哈尔滨市',
  shenyang: '沈阳市',
  tianjin: '天津市',
};
const NORMALIZE_CITY_MAP = Object.fromEntries(
  Object.entries(CITY_NAME_MAP).map(([k, v]) => [k.replace(/\s/g, '').toLowerCase(), v])
);

// 从详细地址中提取市级名称，如"成都市锦江区东大街"→"成都市"
const extractCity = (address) => {
  if (!address) return null;
  // 尝试按"市"字截取，如"成都市锦江区…"→"成都市"
  const idx = address.indexOf('市');
  if (idx !== -1) return address.substring(0, idx + 1);
  // 全英文/拼音地址 → 尝试映射为中文城市名
  if (!/[一-龥]/.test(address)) {
    const normalized = address.replace(/\s/g, '').toLowerCase();
    // 先精确匹配
    if (NORMALIZE_CITY_MAP[normalized]) return NORMALIZE_CITY_MAP[normalized];
    // 再前缀匹配（如 "Chen" 匹配 "chengdu"）
    for (const [en, zh] of Object.entries(NORMALIZE_CITY_MAP)) {
      if (en.startsWith(normalized) || normalized.startsWith(en)) return zh;
    }
    return address;
  }
  // 中文地址但没有"市"字（可能为直辖市或区域）：取前6个字符
  return address.length > 6 ? address.substring(0, 6) : address;
};

=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
const formatAgeMonths = (months) => {
  if (months == null || months === '') return '未知';
  const m = Number(months);
  if (m < 12) return `${m}个月`;
  const years = Math.floor(m / 12);
  const rem = m % 12;
  if (rem === 0) return `${years}岁`;
  return `${years}岁${rem}个月`;
};

<<<<<<< HEAD
const ADOPTION_BADGE = {
  available: 'success',
  pending: 'warning text-dark',
  adopted: 'secondary',
};

// ===== 组件 =====

const PetList = () => {
  const navigate = useNavigate();
  const { canManage } = useManageMode();
  const [pets, setPets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // 筛选条件（实际生效的，会触发 API 请求）
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [speciesFilter, setSpeciesFilter] = useState(searchParams.get('species') || '');
  const [genderFilter, setGenderFilter] = useState(searchParams.get('gender') || '');
  const [ageRangeFilter, setAgeRangeFilter] = useState(searchParams.get('age_range') || '');
  const [locationFilter, setLocationFilter] = useState(searchParams.get('location') || '');

  // 输入框暂存值（未确认/未回车时不触发请求）
  const [searchText, setSearchText] = useState(searchParams.get('search') || '');
  const [locationText, setLocationText] = useState(searchParams.get('location') || '');

  // ===== 构建 API 参数 =====
  const buildApiParams = useCallback(() => {
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    const params = { adoption_status: 'available' };
    if (search) params.search = search;
    if (speciesFilter) params.species = speciesFilter;
    if (genderFilter) params.gender = genderFilter;
<<<<<<< HEAD
    if (locationFilter) params.location = locationFilter;
    if (ageRangeFilter) {
      const [min, max] = ageRangeFilter.split('-');
      if (min) params.age_min = min;
      if (max && max !== '999') params.age_max = max;
    }
    return params;
  }, [search, speciesFilter, genderFilter, ageRangeFilter, locationFilter]);

  // ===== 同步筛选条件到 URL =====
  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (speciesFilter) params.set('species', speciesFilter);
    if (genderFilter) params.set('gender', genderFilter);
    if (ageRangeFilter) params.set('age_range', ageRangeFilter);
    if (locationFilter) params.set('location', locationFilter);
    setSearchParams(params, { replace: true });
  }, [search, speciesFilter, genderFilter, ageRangeFilter, locationFilter, setSearchParams]);

  // ===== 请求宠物列表（除搜索外，其他筛选变化直接触发）=====
  const fetchPets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = buildApiParams();
      const response = await petsAPI.getAll(params);
      setPets(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (err) {
      setError('加载宠物列表失败，请稍后重试。');
      console.error('Error fetching pets:', err);
    } finally {
      setLoading(false);
    }
  }, [buildApiParams]);
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9

  useEffect(() => {
    fetchPets();
  }, [fetchPets]);

<<<<<<< HEAD
  // ===== 搜索确认按钮 =====
  const handleSearchConfirm = () => {
    setSearch(searchText.trim());
  };

  // 搜索框回车也触发搜索
  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') {
      setSearch(searchText.trim());
    }
  };

  // ===== 地区筛选：仅按回车触发 =====
  const handleLocationKeyDown = (e) => {
    if (e.key === 'Enter') {
      setLocationFilter(locationText.trim());
    }
  };

  // ===== 一键重置 =====
  const handleClearAll = () => {
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
    setSearchText('');
    setSearch('');
    setSpeciesFilter('');
    setGenderFilter('');
<<<<<<< HEAD
    setAgeRangeFilter('');
    setLocationText('');
    setLocationFilter('');
  };

  const hasActiveFilters = search || speciesFilter || genderFilter || ageRangeFilter || locationFilter;

  // ===== 活跃筛选标签 =====
  const activeFilterBadges = [];
  if (search) {
    activeFilterBadges.push({ key: 'search', label: `名称：${search}`, onRemove: () => { setSearch(''); setSearchText(''); } });
  }
  if (speciesFilter) {
    activeFilterBadges.push({
      key: 'species',
      label: `种类：${SPECIES_LABELS[speciesFilter] || speciesFilter}`,
      onRemove: () => setSpeciesFilter(''),
    });
  }
  if (genderFilter) {
    activeFilterBadges.push({
      key: 'gender',
      label: `性别：${GENDER_LABELS[genderFilter] || genderFilter}`,
      onRemove: () => setGenderFilter(''),
    });
  }
  if (ageRangeFilter) {
    const option = AGE_RANGE_OPTIONS.find((o) => o.value === ageRangeFilter);
    activeFilterBadges.push({
      key: 'age',
      label: `年龄：${option ? option.label : ageRangeFilter}`,
      onRemove: () => setAgeRangeFilter(''),
    });
  }
  if (locationFilter) {
    activeFilterBadges.push({
      key: 'location',
      label: `地区：${locationFilter}`,
      onRemove: () => { setLocationFilter(''); setLocationText(''); },
    });
  }

  // ===== 加载状态 =====
=======
    setCountryFilter('');
    setProvinceFilter('');
    setCityFilter('');
    setAgeMode('stage');
    setAgeStage('');
    setCustomAgeMin('');
    setCustomAgeMax('');
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

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
=======
    return <div className="alert alert-danger">{error}</div>;
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
  }

  return (
    <div className="pet-list-container">
<<<<<<< HEAD
      {/* ===== 筛选搜索区域 ===== */}
      <div className="search-filter-section mb-4">
        <div className="container">
          {/* 第一行：搜索框 + 确认按钮 */}
          <div className="row g-3 mb-3">
            <div className="col-md-9">
              <div className="search-box">
                <i className="fas fa-search search-icon"></i>
                <input
                  type="text"
                  className="form-control search-input"
                  placeholder="按宠物名称搜索..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onKeyDown={handleSearchKeyDown}
                />
              </div>
            </div>
            <div className="col-md-3">
              <button
                className="btn btn-success w-100 search-confirm-btn"
                onClick={handleSearchConfirm}
              >
                <i className="fas fa-search me-1"></i>搜索
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              </button>
            </div>
          </div>

<<<<<<< HEAD
          {/* 第二行：筛选条件 + 一键重置（同一行） */}
          <div className="row g-2 align-items-center">
            <div className="col-4 col-md-2">
              <select
                className="form-select filter-select"
                value={speciesFilter}
                onChange={(e) => setSpeciesFilter(e.target.value)}
              >
                <option value="">全部种类</option>
=======
          <div className="row g-2 mb-2">
            <div className="col-6 col-md-2">
              <select className="form-select" value={speciesFilter} onChange={(e) => setSpeciesFilter(e.target.value)}>
                <option value="">全部物种</option>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                <option value="dog">狗</option>
                <option value="cat">猫</option>
                <option value="bird">鸟</option>
                <option value="rabbit">兔</option>
                <option value="fish">鱼</option>
                <option value="other">其他</option>
              </select>
            </div>
<<<<<<< HEAD
            <div className="col-4 col-md-2">
              <select
                className="form-select filter-select"
                value={genderFilter}
                onChange={(e) => setGenderFilter(e.target.value)}
              >
                <option value="">全部性别</option>
                <option value="male">公</option>
                <option value="female">母</option>
                <option value="unknown">未知</option>
              </select>
            </div>
            <div className="col-4 col-md-2">
              <select
                className="form-select filter-select"
                value={ageRangeFilter}
                onChange={(e) => setAgeRangeFilter(e.target.value)}
              >
                <option value="">不限年龄</option>
                {AGE_RANGE_OPTIONS.filter((o) => o.value).map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="col-6 col-md-3">
              <div className="location-box">
                <i className="fas fa-map-marker-alt location-icon"></i>
                <input
                  type="text"
                  className="form-control location-input"
                  placeholder="按地区筛选（回车确认）..."
                  value={locationText}
                  onChange={(e) => setLocationText(e.target.value)}
                  onKeyDown={handleLocationKeyDown}
                />
              </div>
            </div>
            <div className="col-6 col-md-3">
              <button
                className="btn btn-outline-secondary w-100 reset-btn"
                onClick={handleClearAll}
                disabled={!hasActiveFilters}
              >
                <i className="fas fa-undo me-1"></i>一键重置
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
              </button>
            </div>
          </div>

<<<<<<< HEAD
          {/* 活跃筛选条件标签 */}
          {activeFilterBadges.length > 0 && (
            <div className="active-filters mt-3">
              <div className="d-flex flex-wrap align-items-center gap-2">
                <small className="text-muted me-1">当前筛选：</small>
                {activeFilterBadges.map((badge) => (
                  <span key={badge.key} className="badge bg-success d-flex align-items-center filter-badge">
                    {badge.label}
                    <button
                      type="button"
                      className="btn-close btn-close-white ms-2"
                      aria-label={`移除${badge.label}`}
                      onClick={badge.onRemove}
                    ></button>
                  </span>
                ))}
                <span className="badge bg-info text-dark">可领养</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ===== 结果统计 + 我的申请按钮 ===== */}
      <div className="container mb-4">
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="text-muted mb-0">
            共找到 <strong className="text-success">{pets.length}</strong> 只可领养宠物
          </h5>
          <div className="d-flex align-items-center gap-2">
            {hasActiveFilters && (
              <small className="text-muted">
                已应用 {activeFilterBadges.length} 个筛选条件
              </small>
            )}
            <Link to="/my-applications" className="btn btn-outline-success btn-sm my-applications-btn">
              <i className="fas fa-clipboard-list me-1"></i>我的申请与核验
            </Link>
          </div>
        </div>
      </div>

      {/* ===== 宠物卡片列表 ===== */}
=======
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
                    type="number"
                    min="0"
                    className="form-control"
                    placeholder="最小月龄"
                    value={customAgeMin}
                    onChange={(e) => setCustomAgeMin(e.target.value)}
                  />
                </div>
                <div className="col-6 col-md-2">
                  <input
                    type="number"
                    min="0"
                    className="form-control"
                    placeholder="最大月龄"
                    value={customAgeMax}
                    onChange={(e) => setCustomAgeMax(e.target.value)}
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

>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      <div className="container">
        <div className="row">
          {pets.map((pet) => (
            <div key={pet.id} className="col-md-4 col-lg-3 mb-4">
              <div className="pet-card" onClick={() => navigate(`/pets/${pet.id}`)} style={{ cursor: 'pointer' }}>
<<<<<<< HEAD
                {/* 宠物照片 */}
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD

                <div className="pet-card-body">
                  <div
                    className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="d-flex align-items-center gap-1 flex-wrap">
                      <span className={`badge bg-${ADOPTION_BADGE[pet.adoption_status] || 'secondary'}`}>
                        {ADOPTION_STATUS[pet.adoption_status] || '未知'}
                      </span>
                      {canManage && !pet.is_public && (
                        <span className="badge bg-secondary">未公开</span>
                      )}
                    </div>
                    <div className="flex-grow-1">
                      <AdminManageBar
                        compact
                        onEdit={() => window.location.assign(`/pets/${pet.id}`)}
                        onHide={async () => {
                          try {
                            await petsAPI.update(pet.id, { is_public: false });
                            alert('已设为不公开');
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
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
<<<<<<< HEAD

                  {/* 宠物名称 + 种类图标 */}
                  <h5 className="pet-card-title">
                    <i
                      className={`fas fa-${
                        pet.species === 'dog' ? 'dog' : pet.species === 'cat' ? 'cat' : 'paw'
                      } me-2 text-success`}
                    ></i>
                    {pet.name || '未命名宠物'}
                  </h5>

                  {/* 基本信息（无品种字段） */}
                  <div className="pet-card-info">
                    <div className="info-row">
                      <span className="info-label"><i className="fas fa-tag me-1"></i>种类</span>
                      <span className="info-value">{SPECIES_LABELS[pet.species] || pet.species || '未知'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label"><i className="fas fa-venus-mars me-1"></i>性别</span>
                      <span className="info-value">{GENDER_LABELS[pet.gender] || pet.gender || '未知'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label"><i className="fas fa-calendar-alt me-1"></i>年龄</span>
                      <span className="info-value">{formatAgeMonths(pet.age_months)}</span>
                    </div>
                    {/* 体型 */}
                    {formatSizeDisplay(pet) && (
                      <div className="info-row">
                        <span className="info-label"><i className="fas fa-weight me-1"></i>体型</span>
                        <span className="info-value">{formatSizeDisplay(pet)}</span>
                      </div>
                    )}
                    {/* 所在地区（截断到市级） */}
                    {pet.rescue_case_address && (
                      <div className="info-row">
                        <span className="info-label"><i className="fas fa-map-marker-alt me-1"></i>地区</span>
                        <span className="info-value" title={pet.rescue_case_address}>
                          {extractCity(pet.rescue_case_address)}
                        </span>
                      </div>
                    )}
                    {/* 健康状况 */}
                    {pet.health_status && (
                      <div className="info-row">
                        <span className="info-label"><i className="fas fa-heartbeat me-1"></i>健康</span>
                        <span className="info-value">{formatHealthStatus(pet.health_status)}</span>
                      </div>
                    )}
                  </div>
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
                </div>
              </div>
            </div>
          ))}
<<<<<<< HEAD

          {/* 空状态 */}
          {pets.length === 0 && (
            <div className="text-center py-5">
              <i className="fas fa-search fa-3x text-muted mb-3"></i>
              <p className="text-muted">没有符合筛选条件的可领养宠物。</p>
              {hasActiveFilters && (
                <button className="btn btn-outline-success mt-2" onClick={handleClearAll}>
                  <i className="fas fa-undo me-1"></i>清除全部筛选条件
                </button>
              )}
=======
          {pets.length === 0 && (
            <div className="text-center py-5">
              <p className="text-muted">没有符合筛选条件的可领养宠物。</p>
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
            </div>
          )}
        </div>
      </div>

<<<<<<< HEAD
      {/* ===== 样式 ===== */}
      <style>{`
        .pet-list-container {
          background-color: #FAFAFA;
          min-height: 100vh;
          padding-top: 2rem;
        }

        /* 筛选区域 */
        .search-filter-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem 2rem;
          box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }

        /* 搜索框 */
        .search-box { position: relative; }
        .search-icon {
          position: absolute;
          left: 16px;
          top: 50%;
          transform: translateY(-50%);
          color: #999;
          z-index: 10;
          font-size: 1rem;
        }
        .search-input {
          padding-left: 42px;
          border-radius: 25px;
          border: 2px solid #e9ecef;
          transition: all 0.3s ease;
          height: 44px;
        }
        .search-input:focus {
          border-color: #00C897;
          box-shadow: 0 0 0 0.2rem rgba(0, 200, 151, 0.2);
        }
        .search-confirm-btn {
          border-radius: 25px;
          height: 44px;
          transition: all 0.3s ease;
        }

        /* 地区输入框 */
        .location-box { position: relative; }
        .location-icon {
          position: absolute;
          left: 14px;
          top: 50%;
          transform: translateY(-50%);
          color: #999;
          z-index: 10;
          font-size: 0.9rem;
        }
        .location-input {
          padding-left: 36px;
          border-radius: 25px;
          border: 2px solid #e9ecef;
          transition: all 0.3s ease;
          height: 44px;
        }
        .location-input:focus {
          border-color: #00C897;
          box-shadow: 0 0 0 0.2rem rgba(0, 200, 151, 0.2);
        }

        /* 筛选下拉框 */
        .filter-select {
          border-radius: 25px;
          border: 2px solid #e9ecef;
          transition: all 0.3s ease;
          height: 44px;
          cursor: pointer;
          font-size: 0.9rem;
        }
        .filter-select:focus {
          border-color: #00C897;
          box-shadow: 0 0 0 0.2rem rgba(0, 200, 151, 0.2);
        }

        /* 重置按钮 */
        .reset-btn {
          border-radius: 25px;
          height: 44px;
          transition: all 0.3s ease;
          font-size: 0.9rem;
        }
        .reset-btn:hover:not(:disabled) {
          background-color: #dc3545;
          border-color: #dc3545;
          color: white;
        }

        /* 活跃筛选条件 */
        .active-filters {
          padding: 0.75rem 1rem;
          background-color: #f8f9fa;
          border-radius: 12px;
          border: 1px dashed #dee2e6;
        }
        .filter-badge {
          font-size: 0.82rem;
          padding: 0.4em 0.7em;
          border-radius: 20px;
        }

        /* 宠物卡片 */
        .pet-card {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 2px 12px rgba(0,0,0,0.06);
          transition: all 0.3s ease;
          height: 100%;
          display: flex;
          flex-direction: column;
        }
        .pet-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.12);
          border: 2px solid #00C897;
        }

        /* 卡片图片 */
        .pet-card-img-wrapper {
          position: relative;
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        }
        .pet-card-img {
          width: 100%;
          height: 200px;
          object-fit: cover;
        }
<<<<<<< HEAD
        .pet-status-badge {
          position: absolute;
          top: 12px;
          right: 12px;
          font-size: 0.75rem;
          padding: 0.35em 0.7em;
          border-radius: 20px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }

        /* 卡片内容 */
        .pet-card-body {
          padding: 1.25rem;
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        .pet-card-title {
          color: #333;
          margin-bottom: 0.75rem;
          font-size: 1.15rem;
          font-weight: 600;
        }

        /* 信息行 */
        .pet-card-info {
          margin-bottom: 0.5rem;
        }
        .info-row {
          display: flex;
          align-items: flex-start;
          font-size: 0.85rem;
          margin-bottom: 0.3rem;
          line-height: 1.5;
        }
        .info-label {
          color: #999;
          min-width: 52px;
          flex-shrink: 0;
=======
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
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
        }
        .info-value {
          color: #555;
          flex: 1;
        }
<<<<<<< HEAD

        /* 我的申请按钮 */
        .my-applications-btn {
          border-radius: 25px;
          border: 2px solid #00C897;
          color: #00C897;
          transition: all 0.3s ease;
          white-space: nowrap;
        }
        .my-applications-btn:hover {
          background-color: #00C897;
          color: white;
        }
=======
>>>>>>> 5981cf21ae81764086b722a469035686c308c5f9
      `}</style>
    </div>
  );
};

export default PetList;
