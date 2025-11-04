import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from '../../locales/translations';
import { complaintsAPI } from '../../services/api';

export default function MapScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { t } = useTranslation(language);

  const { data, isLoading } = useQuery({
    queryKey: ['complaintsMap'],
    queryFn: () => complaintsAPI.getAll({}),
  });

  const complaints = data?.data?.complaints || [];
  const complaintsWithLocation = complaints.filter((c) => c.latitude && c.longitude);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending':
      case 'submitted':
        return '#F59E0B';
      case 'assigned':
        return '#3B82F6';
      case 'in_progress':
        return '#8B5CF6';
      case 'resolved':
        return '#10B981';
      case 'closed':
        return '#6B7280';
      case 'rejected':
        return '#EF4444';
      default:
        return '#9CA3AF';
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>{t('loading')}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Ionicons name="location" size={24} color="#3B82F6" />
          <Text style={styles.headerTitle}>{t('map')}</Text>
        </View>
        <View style={styles.countBadge}>
          <Text style={styles.countText}>
            {complaintsWithLocation.length} {t('complaints')}
          </Text>
        </View>
      </View>

      {/* Info Banner */}
      <View style={styles.infoBanner}>
        <Ionicons name="information-circle" size={20} color="#3B82F6" />
        <Text style={styles.infoBannerText}>
          Map view requires a development build. Showing list of complaints with location data.
        </Text>
      </View>

      {/* Complaints List */}
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {complaintsWithLocation.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="location-outline" size={64} color="#D1D5DB" />
            <Text style={styles.emptyText}>{t('noComplaints')}</Text>
            <Text style={styles.emptySubtext}>No complaints with location data yet</Text>
          </View>
        ) : (
          complaintsWithLocation.map((complaint) => (
            <TouchableOpacity
              key={complaint.id}
              style={styles.card}
              onPress={() => router.push(`/complaint/${complaint.id}`)}
            >
              <View style={styles.cardHeader}>
                <View
                  style={[
                    styles.locationIcon,
                    { backgroundColor: getStatusColor(complaint.status) },
                  ]}
                >
                  <Ionicons name="location" size={20} color="#FFFFFF" />
                </View>
                <View style={styles.cardHeaderText}>
                  <Text style={styles.cardTitle} numberOfLines={1}>
                    {complaint.title}
                  </Text>
                  <View style={styles.locationInfo}>
                    <Ionicons name="navigate" size={12} color="#6B7280" />
                    <Text style={styles.locationText}>
                      {complaint.latitude?.toFixed(4)}, {complaint.longitude?.toFixed(4)}
                    </Text>
                  </View>
                </View>
              </View>

              <Text style={styles.cardDescription} numberOfLines={2}>
                {complaint.description}
              </Text>

              <View style={styles.cardFooter}>
                <View style={styles.categoryBadge}>
                  <Ionicons name="pricetag" size={12} color="#6B7280" />
                  <Text style={styles.categoryText}>
                    {t(complaint.category?.toLowerCase() || 'other')}
                  </Text>
                </View>
                <View
                  style={[
                    styles.statusBadge,
                    { backgroundColor: getStatusColor(complaint.status) },
                  ]}
                >
                  <Text style={styles.statusText}>
                    {t(complaint.status?.toLowerCase() || 'pending')}
                  </Text>
                </View>
              </View>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6B7280',
  },
  header: {
    backgroundColor: '#FFFFFF',
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F2937',
  },
  countBadge: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  countText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#3B82F6',
  },
  infoBanner: {
    backgroundColor: '#EFF6FF',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 8,
    gap: 8,
  },
  infoBannerText: {
    flex: 1,
    fontSize: 12,
    color: '#1E40AF',
    lineHeight: 16,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 12,
  },
  locationIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardHeaderText: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  locationText: {
    fontSize: 12,
    color: '#6B7280',
  },
  cardDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  categoryText: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
