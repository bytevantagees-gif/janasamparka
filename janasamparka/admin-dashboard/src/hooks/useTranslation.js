import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../locales/translations';

export const useTranslation = () => {
  const { language } = useLanguage();

  const t = (key, fallback) => {
    if (!key) return '';
    return (
      translations[language]?.[key] ||
      translations.en?.[key] ||
      fallback ||
      key
    );
  };

  return { t, language };
};
