import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Image,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Linking,
  Animated,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function LoginScreen() {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRequestOTP = async () => {
    if (phone.length < 10) {
      alert('Please enter a valid phone number');
      return;
    }

    setLoading(true);
    try {
      // API call to request OTP
      // const response = await authAPI.requestOTP(phone);
      
      // Navigate to OTP screen
      router.push({
        pathname: '/(auth)/otp',
        params: { phone }
      });
    } catch (error) {
      alert(error.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <LinearGradient
        colors={['#3B82F6', '#2563EB', '#1D4ED8']}
        style={styles.gradient}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Logo Section */}
          <View style={styles.logoContainer}>
            {/* <View style={styles.emblemWrapper}>
              <Image
                source={require('../../assets/karnataka-emblem.png')}
                style={styles.emblem}
                resizeMode="contain"
              />
            </View> */}
            <Text style={styles.appTitle}>ಜನಸಂಪರ್ಕ</Text>
            <Text style={styles.appSubtitle}>Jana Samparka</Text>
            <Text style={styles.appDescription}>MLA Connect Platform</Text>
            <Text style={styles.govText}>Government of Karnataka</Text>
          </View>

          {/* Login Card */}
          <View style={styles.loginCard}>
            <View style={styles.cardHeader}>
              <Ionicons name="phone-portrait-outline" size={32} color="#2563EB" />
              <Text style={styles.cardTitle}>Login to Continue</Text>
              <Text style={styles.cardSubtitle}>Enter your mobile number</Text>
            </View>

            {/* Phone Input */}
            <View style={styles.inputContainer}>
              <View style={styles.inputWrapper}>
                <Ionicons name="call-outline" size={20} color="#64748B" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Mobile Number"
                  placeholderTextColor="#94A3B8"
                  value={phone}
                  onChangeText={setPhone}
                  keyboardType="phone-pad"
                  maxLength={10}
                  autoFocus
                />
              </View>
              <Text style={styles.inputHint}>
                Enter 10-digit mobile number without +91
              </Text>
            </View>

            {/* Login Button */}
            <TouchableOpacity
              style={[styles.loginButton, loading && styles.loginButtonDisabled]}
              onPress={handleRequestOTP}
              disabled={loading || phone.length < 10}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={loading ? ['#94A3B8', '#64748B'] : ['#3B82F6', '#2563EB']}
                style={styles.buttonGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
              >
                {loading ? (
                  <Text style={styles.buttonText}>Sending OTP...</Text>
                ) : (
                  <>
                    <Text style={styles.buttonText}>Request OTP</Text>
                    <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>

            {/* Quick Login Options */}
            <View style={styles.quickLogin}>
              <Text style={styles.quickLoginTitle}>Quick Test Login</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                style={styles.quickLoginScroll}
              >
                {[
                  { phone: '9999999999', role: 'Admin', icon: 'shield-checkmark' },
                  { phone: '8242226666', role: 'MLA', icon: 'business' },
                  { phone: '9876543211', role: 'Moderator', icon: 'people' },
                  { phone: '9876543214', role: 'Citizen', icon: 'person' },
                ].map((user, index) => (
                  <TouchableOpacity
                    key={index}
                    style={styles.quickLoginCard}
                    onPress={() => setPhone(user.phone)}
                  >
                    <Ionicons name={user.icon} size={20} color="#2563EB" />
                    <Text style={styles.quickLoginRole}>{user.role}</Text>
                    <Text style={styles.quickLoginPhone}>{user.phone}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          </View>

          {/* Developer Credits */}
          <View style={styles.creditsContainer}>
            <View style={styles.creditsCard}>
              <Text style={styles.creditsDeveloper}>
                Developed by <Text style={styles.creditsHighlight}>srbhandary</Text>
              </Text>
              <Text style={styles.creditsCompany}>
                Bytevantage Enterprise Solutions
              </Text>
              <Text style={styles.creditsLocation}>Mangalore, Karnataka</Text>
              
              <View style={styles.creditsLinks}>
                <TouchableOpacity
                  onPress={() => Linking.openURL('https://www.bytevantage.in')}
                  style={styles.creditsLinkButton}
                >
                  <Ionicons name="globe-outline" size={14} color="#3B82F6" />
                  <Text style={styles.creditsLink}>www.bytevantage.in</Text>
                </TouchableOpacity>
                
                <Text style={styles.creditsSeparator}>•</Text>
                
                <TouchableOpacity
                  onPress={() => Linking.openURL('mailto:srbhandary@bytevantage.in')}
                  style={styles.creditsLinkButton}
                >
                  <Ionicons name="mail-outline" size={14} color="#3B82F6" />
                  <Text style={styles.creditsLink}>srbhandary@bytevantage.in</Text>
                </TouchableOpacity>
              </View>
              
              <Text style={styles.creditsCopyright}>© 2025 All Rights Reserved</Text>
            </View>
          </View>
        </ScrollView>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
    paddingTop: 60,
  },
  
  // Logo Section
  logoContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  emblemWrapper: {
    width: 100,
    height: 100,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  emblem: {
    width: 70,
    height: 70,
  },
  appTitle: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  appSubtitle: {
    fontSize: 20,
    color: '#E0E7FF',
    fontWeight: '600',
    marginBottom: 4,
  },
  appDescription: {
    fontSize: 14,
    color: '#DBEAFE',
    marginBottom: 4,
  },
  govText: {
    fontSize: 12,
    color: '#BFDBFE',
    fontStyle: 'italic',
  },
  
  // Login Card
  loginCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 5,
    marginBottom: 20,
  },
  cardHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  cardTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1E293B',
    marginTop: 12,
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#64748B',
  },
  
  // Input
  inputContainer: {
    marginBottom: 20,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    borderRadius: 12,
    paddingHorizontal: 16,
    borderWidth: 2,
    borderColor: '#E2E8F0',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    height: 56,
    fontSize: 16,
    color: '#1E293B',
  },
  inputHint: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 8,
    marginLeft: 4,
  },
  
  // Button
  loginButton: {
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 20,
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  buttonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  
  // Quick Login
  quickLogin: {
    marginTop: 12,
  },
  quickLoginTitle: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 12,
    textAlign: 'center',
  },
  quickLoginScroll: {
    marginHorizontal: -24,
    paddingHorizontal: 24,
  },
  quickLoginCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    marginRight: 8,
    alignItems: 'center',
    minWidth: 100,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  quickLoginRole: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1E293B',
    marginTop: 6,
  },
  quickLoginPhone: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 2,
  },
  
  // Credits
  creditsContainer: {
    marginTop: 'auto',
    paddingTop: 20,
  },
  creditsCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  creditsDeveloper: {
    fontSize: 13,
    color: '#1E293B',
    marginBottom: 4,
    fontWeight: '500',
  },
  creditsHighlight: {
    color: '#2563EB',
    fontWeight: '700',
  },
  creditsCompany: {
    fontSize: 13,
    color: '#475569',
    fontWeight: '600',
    marginBottom: 2,
  },
  creditsLocation: {
    fontSize: 11,
    color: '#64748B',
    marginBottom: 12,
  },
  creditsLinks: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  creditsLinkButton: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  creditsLink: {
    fontSize: 11,
    color: '#3B82F6',
    marginLeft: 4,
  },
  creditsSeparator: {
    fontSize: 11,
    color: '#94A3B8',
    marginHorizontal: 8,
  },
  creditsCopyright: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 4,
  },
});
