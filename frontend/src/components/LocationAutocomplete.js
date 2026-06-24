import React, { useEffect, useRef, useState } from 'react';
import { searchAmapPlaces } from '../utils/amapLocation';

const emptyLocation = {
  country: '中国',
  province: '',
  city: '',
  district: '',
  location_text: '',
  latitude: null,
  longitude: null,
};

const LocationAutocomplete = ({
  value,
  onChange,
  required = false,
  defaultCity = '',
  placeholder = '输入地点关键词，选择候选地址',
}) => {
  const [query, setQuery] = useState(value?.location_text || '');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const wrapperRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    setQuery(value?.location_text || '');
  }, [value?.location_text]);

  useEffect(() => {
    const onDocumentClick = (event) => {
      if (!wrapperRef.current?.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', onDocumentClick);
    return () => document.removeEventListener('mousedown', onDocumentClick);
  }, []);

  const handleSearch = (text) => {
    setQuery(text);
    if (timerRef.current) clearTimeout(timerRef.current);
    if (!text.trim()) {
      setResults([]);
      setShowDropdown(false);
      onChange({ ...emptyLocation, country: value?.country || '中国', location_text: '' });
      return;
    }
    timerRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const list = await searchAmapPlaces(text, defaultCity);
        setResults(list);
        setShowDropdown(list.length > 0);
      } catch (error) {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);
  };

  const handlePick = (item) => {
    onChange({
      country: item.country || '中国',
      province: item.province || '',
      city: item.city || '',
      district: item.district || '',
      location_text: item.location_text || item.name || '',
      latitude: Number.isFinite(item.latitude) ? Number(item.latitude.toFixed(6)) : null,
      longitude: Number.isFinite(item.longitude) ? Number(item.longitude.toFixed(6)) : null,
    });
    setQuery(item.location_text || item.name || '');
    setShowDropdown(false);
  };

  return (
    <div ref={wrapperRef} className="position-relative">
      <input
        type="text"
        className="form-control"
        value={query}
        required={required}
        placeholder={placeholder}
        onFocus={() => {
          if (results.length > 0) setShowDropdown(true);
        }}
        onChange={(e) => handleSearch(e.target.value)}
      />
      {searching && (
        <span className="position-absolute top-50 end-0 translate-middle-y me-2">
          <span className="spinner-border spinner-border-sm" role="status" />
        </span>
      )}
      {showDropdown && (
        <div
          className="position-absolute start-0 end-0 mt-1 border bg-white rounded shadow-sm"
          style={{ zIndex: 1050, maxHeight: 260, overflowY: 'auto' }}
        >
          {results.map((item) => (
            <button
              key={item.id}
              type="button"
              className="dropdown-item py-2"
              onClick={() => handlePick(item)}
            >
              <div className="fw-semibold">{item.name}</div>
              <small className="text-muted">
                {[item.province, item.city, item.district, item.address].filter(Boolean).join(' ')}
              </small>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default LocationAutocomplete;
