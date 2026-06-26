/**
 * @file amap.js
 * @module PawRescue
 * @description 源码：frontend/src/config/amap.js
 */

// Gaode (AMap) Web API key and Leaflet tile layer

// Apply at: https://console.amap.com/dev/key/app

export const AMAP_KEY = process.env.REACT_APP_AMAP_KEY || 'e9b57a099f261b32a70742305ae7e705';

export const AMAP_TILE_URL =

  'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}';

export const AMAP_TILE_OPTIONS = {

  maxZoom: 19,

  subdomains: ['1', '2', '3', '4'],

  attribution: '\u00a9 \u9ad8\u5fb7\u5730\u56fe',

};

