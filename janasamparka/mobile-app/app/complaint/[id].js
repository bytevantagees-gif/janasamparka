import { View, Text, ScrollView, StyleSheet, Image, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from '../../locales/translations';
import { complaintsAPI } from '../../services/api';

export default function ComplaintDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const { language } = useLanguage();
  const { t } = useTranslation(language);

  const { data, isLoading, error } = useQuery({
    queryKey: ['complaint', id],
    queryFn: () => complaintsAPI.getById(id),
    enabled: !!id,
  });

  const complaint = data?.data;

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

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>{t('loading')}</Text>
      </View>
    );
  }

  if (error || !complaint) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="alert-circle-outline" size={64} color="#EF4444" />
        <Text style={styles.errorText}>{t('error')}</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: t('complaintDetails') }} />
      <ScrollView style={styles.container}>
        {/* Status Badge */}
        <View style={styles.statusContainer}>
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

        {/* Title */}
        <View style={styles.section}>
          <Text style={styles.title}>{complaint.title}</Text>
          <View style={styles.categoryBadge}>
            <Ionicons name="pricetag" size={16} color="#3B82F6" />
            <Text style={styles.categoryText}>
              {t(complaint.category?.toLowerCase() || 'other')}
            </Text>
          </View>
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('description')}</Text>
          <Text style={styles.description}>{complaint.description}</Text>
        </View>

        {/* Images */}
        {complaint.images && complaint.images.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('photos')}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.imageGrid}>
                {complaint.images.map((image, index) => (
                  <Image
                    key={index}
                    source={{ uri: image }}
                    style={styles.image}
                    resizeMode="cover"
                  />
                ))}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Details */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Details</Text>
          <View style={styles.detailsCard}>
            <DetailRow
              icon="calendar-outline"
              label={t('createdOn')}
              value={formatDate(complaint.created_at)}
            />
            <DetailRow
              icon="time-outline"
              label={t('updatedOn')}
              value={formatDate(complaint.updated_at)}
            />
            {complaint.ward_name && (
              <DetailRow
                icon="location-outline"
                label={t('ward')}
                value={complaint.ward_name}
              />
            )}
            {complaint.constituency_name && (
              <DetailRow
                icon="business-outline"
                label={t('constituency')}
                value={complaint.constituency_name}
              />
            )}
            {complaint.assigned_department && (
              <DetailRow
                icon="briefcase-outline"
                label={t('department')}
                value={complaint.assigned_department}
              />
            )}
            {complaint.latitude && complaint.longitude && (
              <DetailRow
                icon="pin-outline"
                label={t('location')}
                value={`${complaint.latitude.toFixed(6)}, ${complaint.longitude.toFixed(6)}`}
              />
            )}
          </View>
        </View>

        {/* Timeline */}
        {complaint.timeline && complaint.timeline.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('timeline')}</Text>
            <View style={styles.timelineCard}>
              {complaint.timeline.map((item, index) => (
                <View key={index} style={styles.timelineItem}>
                  <View
                    style={[
                      styles.timelineDot,
                      { backgroundColor: getStatusColor(item.status) },
                    ]}
                  />
                  <View style={styles.timelineContent}>
                    <Text style={styles.timelineStatus}>
                      {t(item.status?.toLowerCase() || 'pending')}
                    </Text>
                    {item.comment && (
                      <Text style={styles.timelineComment}>{item.comment}</Text>
                    )}
                    <Text style={styles.timelineDate}>
                      {formatDate(item.created_at)}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>
    </>
  );
}

function DetailRow({ icon, label, value }) {
  return (
    <View style={styles.detailRow}>
      <View style={styles.detailLabel}>
        <Ionicons name={icon} size={18} color="#6B7280" />
        <Text style={styles.detailLabelText}>{label}</Text>
      </View>
      <Text style={styles.detailValue}>{value}</Text>
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    paddingHorizontal: 32,
  },
  errorText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#374151',
    marginTop: 16,
  },
  backButton: {
    marginTop: 24,
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#3B82F6',
    borderRadius: 8,
  },
  backButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  statusContainer: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  statusBadge: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 16,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
    textTransform: 'uppercase',
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginTop: 12,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  categoryText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 12,
  },
  description: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
  },
  imageGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 12,
  },
  detailsCard: {
    gap: 4,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  detailLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flex: 1,
  },
  detailLabelText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: 14,
    color: '#1F2937',
    fontWeight: '600',
    flex: 1,
    textAlign: 'right',
  },
  timelineCard: {
    paddingLeft: 8,
  },
  timelineItem: {
    flexDirection: 'row',
    paddingBottom: 20,
  },
  timelineDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginTop: 4,
    marginRight: 12,
  },
  timelineContent: {
    flex: 1,
  },
  timelineStatus: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
    textTransform: 'capitalize',
  },
  timelineComment: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  timelineDate: {
    fontSize: 12,
    color: '#9CA3AF',
  },
});
