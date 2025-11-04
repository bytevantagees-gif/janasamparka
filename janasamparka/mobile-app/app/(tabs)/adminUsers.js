import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTranslation } from '../../locales/translations';
import { useLanguage } from '../../contexts/LanguageContext';

export default function AdminUsers() {
  const { language } = useLanguage();
  const { t } = useTranslation(language);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('adminUsers')}</Text>
      <Text style={styles.subtitle}>{t('adminUsersDesc')}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#F8FAFC',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1D4ED8',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748B',
  },
});
