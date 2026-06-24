import { AMAP_KEY } from '../config/amap';

const normalizeAmapResponse = (json) => (json && typeof json === 'object' ? json : {});

export const parseAmapAddress = (addressComponent = {}) => ({
  country: addressComponent.country || '中国',
  province: addressComponent.province || '',
  city: Array.isArray(addressComponent.city)
    ? (addressComponent.city[0] || '')
    : (addressComponent.city || addressComponent.province || ''),
  district: addressComponent.district || '',
});

export async function searchAmapPlaces(keywords, city = '') {
  if (!keywords?.trim()) return [];
  const url =
    `https://restapi.amap.com/v3/place/text?key=${AMAP_KEY}` +
    `&keywords=${encodeURIComponent(keywords.trim())}` +
    `&city=${encodeURIComponent(city)}` +
    '&offset=10&page=1&extensions=all';
  const res = await fetch(url);
  const json = normalizeAmapResponse(await res.json());
  if (json.status !== '1' || !Array.isArray(json.pois)) return [];
  return json.pois
    .filter((poi) => poi.location)
    .map((poi) => {
      const [lng, lat] = String(poi.location).split(',');
      const parsed = parseAmapAddress(poi.pname || poi.cityname ? {
        country: '中国',
        province: poi.pname,
        city: poi.cityname,
        district: poi.adname,
      } : {});
      return {
        id: poi.id || `${poi.name}-${poi.location}`,
        name: poi.name || '',
        address: poi.address || '',
        location_text: poi.address ? `${poi.name}，${poi.address}` : (poi.name || ''),
        latitude: lat ? Number(lat) : null,
        longitude: lng ? Number(lng) : null,
        ...parsed,
      };
    });
}

export async function reverseAmapLocation(latitude, longitude) {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;
  const location = `${longitude},${latitude}`;
  const url =
    `https://restapi.amap.com/v3/geocode/regeo?key=${AMAP_KEY}` +
    `&location=${encodeURIComponent(location)}` +
    '&extensions=all&radius=1000';
  const res = await fetch(url);
  const json = normalizeAmapResponse(await res.json());
  if (json.status !== '1' || !json.regeocode) return null;
  const component = parseAmapAddress(json.regeocode.addressComponent || {});
  return {
    ...component,
    latitude,
    longitude,
    location_text: json.regeocode.formatted_address || '',
  };
}
