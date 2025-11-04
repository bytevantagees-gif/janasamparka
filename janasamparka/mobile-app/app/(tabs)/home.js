import { View, Text, ScrollView, TouchableOpacity, StyleSheet, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from '../../locales/translations';
import { useAuth } from '../../contexts/AuthContext';
import { complaintsAPI } from '../../services/api';

export default function HomeScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { t } = useTranslation(language);
  const { user } = useAuth();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['myComplaints'],
    queryFn: () => complaintsAPI.getAll({ limit: 5 }),
  });

  const complaints = data?.data?.complaints || [];

  const quickActions = [
    {
      title: t('submitComplaint'),
      icon: 'add-circle',
      color: '#3B82F6',
      onPress: () => router.push('/(tabs)/submit'),
    },
    {
      title: t('trackComplaints'),
      icon: 'list',
      color: '#10B981',
      onPress: () => router.push('/(tabs)/complaints'),
    },
    {
      title: t('viewMap'),
      icon: 'map',
      color: '#F59E0B',
      onPress: () => router.push('/(tabs)/map'),
    },
  ];

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

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
    >
      {/* Welcome Header */}
      <View style={styles.header}>
        <Text style={styles.welcomeText}>{t('welcome')}</Text>
        <Text style={styles.userName}>{user?.name || user?.phone}</Text>
        <Text style={styles.subtitle}>{t('welcomeMessage')}</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t('quickActions')}</Text>
        <View style={styles.actionsGrid}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.actionCard, { borderColor: action.color }]}
              onPress={action.onPress}
            >
              <View style={[styles.actionIconContainer, { backgroundColor: action.color }]}>
                <Ionicons name={action.icon} size={28} color="#FFFFFF" />
              </View>
              <Text style={styles.actionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Complaints */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{t('recentComplaints')}</Text>
          <TouchableOpacity onPress={() => router.push('/(tabs)/complaints')}>
            <Text style={styles.viewAllText}>{t('view')} {t('allComplaints')}</Text>
          </TouchableOpacity>
        </View>

        {complaints.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="document-text-outline" size={64} color="#D1D5DB" />
            <Text style={styles.emptyText}>{t('noData')}</Text>
          </View>
        ) : (
          <View style={styles.complaintsList}>
            {complaints.map((complaint) => (
              <TouchableOpacity
                key={complaint.id}
                style={styles.complaintCard}
                onPress={() => router.push(`/complaint/${complaint.id}`)}
              >
                <View style={styles.complaintHeader}>
                  <Text style={styles.complaintTitle} numberOfLines={1}>
                    {complaint.title}
                  </Text>
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
                <Text style={styles.complaintDescription} numberOfLines={2}>
                  {complaint.description}
                </Text>
                <View style={styles.complaintFooter}>
                  <Text style={styles.categoryText}>
                    {t(complaint.category?.toLowerCase() || 'other')}
                  </Text>
                  <Text style={styles.dateText}>
                    {new Date(complaint.created_at).toLocaleDateString()}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#3B82F6',
    padding: 24,
    paddingTop: 16,
    paddingBottom: 32,
  },
  welcomeText: {
    fontSize: 16,
    color: '#DBEAFE',
    fontWeight: '500',
  },
  userName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#DBEAFE',
    marginTop: 8,
  },
  section: {
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  viewAllText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '600',
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  actionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    width: '30%',
    borderWidth: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  actionIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
  },
  complaintsList: {
    gap: 12,
  },
  complaintCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  complaintHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  complaintTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginRight: 8,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  complaintDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 12,
  },
  complaintFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  categoryText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#3B82F6',
  },
  dateText: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 16,
  },
});
