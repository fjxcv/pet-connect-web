/**
 * @file adoptQuestionnaireDisplay.js
 * @module PawRescue
 * @description 工具函数：adoptQuestionnaireDisplay。
 */

const QUESTIONNAIRE_FIELD_ORDER = [
  'full_name',
  'address',
  'phone',
  'wechat',
  'gender',
  'age',
  'housing_type',
  'housing_type_other',
  'own_or_rent',
  'outdoor_areas',
  'outdoor_areas_other',
  'roommate_consent',
  'has_pet_experience',
  'pet_experience_desc',
  'future_changes',
];
const QUESTIONNAIRE_LABELS = {
  full_name: '\u59d3\u540d',
  address: '\u5730\u5740',
  phone: '\u8054\u7cfb\u7535\u8bdd',
  wechat: '\u5fae\u4fe1\u53f7',
  gender: '\u6027\u522b',
  age: '\u5e74\u9f84',
  housing_type: '\u4f4f\u5b85\u7c7b\u578b',
  housing_type_other: '\u5176\u4ed6\u4f4f\u5b85\u7c7b\u578b',
  own_or_rent: '\u4f4f\u623f\u60c5\u51b5',
  outdoor_areas: '\u6237\u5916\u533a\u57df',
  outdoor_areas_other: '\u5176\u4ed6\u6237\u5916\u533a\u57df',
  roommate_consent: '\u540c\u4f4f\u4eba/\u623f\u4e1c\u662f\u5426\u540c\u610f',
  has_pet_experience: '\u662f\u5426\u517b\u8fc7\u5ba0\u7269',
  pet_experience_desc: '\u517b\u5ba0\u7ecf\u9a8c',
  future_changes: '\u672a\u6765\u751f\u6d3b\u53d8\u5316\u8bf4\u660e',
};
const VALUE_MAPS = {
  gender: {
    male: '\u7537',
    female: '\u5973',
    undisclosed: '\u4e0d\u613f\u900f\u9732',
  },
  housing_type: {
    villa: '\u522b\u5885',
    apartment: '\u666e\u901a\u4f4f\u5b85',
    courtyard: '\u4e61\u6751\u5ead\u9662',
    farm: '\u519c\u573a',
    other: '\u5176\u4ed6',
  },
  own_or_rent: {
    own: '\u81ea\u6709\u623f',
    rent: '\u79df\u623f',
  },
  outdoor_areas: {
    yard: '\u9662\u5b50\u6216\u540e\u9662',
    park: '\u5bb6\u9644\u8fd1\u7684\u516c\u56ed',
    rooftop: '\u5c4b\u9876\u548c\u505c\u8f66\u573a',
    other: '\u5176\u4ed6',
  },
  roommate_consent: {
    yes: '\u662f',
    no: '\u5426',
  },
  has_pet_experience: {
    yes: '\u662f',
    no: '\u5426',
  },
};
const ATTACHMENT_TYPE_LABELS = {
  id_card: '\u8eab\u4efd\u8bc1',
  housing_proof: '\u4f4f\u623f\u8bc1\u660e',
  other: '\u5176\u4ed6\u9644\u4ef6',
};

export const formatQuestionnaireValue = (key, value) => {
  if (value == null || value === '') return '-';
  if (key === 'outdoor_areas' && Array.isArray(value)) {
    const map = VALUE_MAPS.outdoor_areas;
    return value.map((item) => map[item] || item).join('\u3001') || '-';
  }
  const map = VALUE_MAPS[key];
  if (map && typeof value === 'string') {
    return map[value] || value;
  }
  if (Array.isArray(value)) {
    return value.join('\u3001');
  }
  return String(value);
};

export const getQuestionnaireEntries = (answers) => {
  if (!answers || typeof answers !== 'object') return [];
  const keys = [
    ...QUESTIONNAIRE_FIELD_ORDER.filter((key) => key in answers),
    ...Object.keys(answers).filter((key) => !QUESTIONNAIRE_FIELD_ORDER.includes(key)),
  ];
  return keys
    .filter((key) => {
      const value = answers[key];
      if (value == null || value === '') return false;
      if (Array.isArray(value) && value.length === 0) return false;
      return true;
    })
    .map((key) => ({
      key,
      label: QUESTIONNAIRE_LABELS[key] || key,
      value: formatQuestionnaireValue(key, answers[key]),
    }));
};

export const formatAttachmentType = (fileType) => ATTACHMENT_TYPE_LABELS[fileType] || fileType || '\u9644\u4ef6';

export default getQuestionnaireEntries;

