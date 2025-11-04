import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Image,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useTranslation } from '../locales/translations';

export default function LoginScreen() {
  const [phone, setPhone] = useState('');
  const [otp, setOTP] = useState('');
  const [step, setStep] = useState('phone'); // 'phone' or 'otp'
  const [loading, setLoading] = useState(false);

  const { requestOTP, verifyOTP } = useAuth();
  const { language, toggleLanguage } = useLanguage();
  const { t } = useTranslation(language);

  const handleRequestOTP = async () => {
    if (!phone || phone.length !== 10) {
      Alert.alert(t('error'), 'Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    try {
      console.log('Requesting OTP for:', `+91${phone}`);
      const result = await requestOTP(`+91${phone}`);
      console.log('OTP Response:', result);
      Alert.alert(t('success'), t('otpSent'));
      setStep('otp');
    } catch (error) {
      console.error('OTP Request Error:', error);
      console.error('Error details:', error.response?.data || error.message);
      const errorMsg = error.response?.data?.detail || error.message || t('otpError');
      Alert.alert(t('error'), `Failed to send OTP: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      Alert.alert(t('error'), 'Please enter a valid 6-digit OTP');
      return;
    }

    setLoading(true);
    try {
      console.log('Verifying OTP for:', `+91${phone}`);
      await verifyOTP(`+91${phone}`, otp);
      console.log('OTP verified successfully');
      Alert.alert(t('success'), t('loginSuccess'));
    } catch (error) {
      console.error('OTP Verification Error:', error);
      console.error('Error details:', error.response?.data || error.message);
      const errorMsg = error.response?.data?.detail || error.message || t('invalidOTP');
      Alert.alert(t('error'), `Verification failed: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.content}>
        {/* Language Toggle */}
        <TouchableOpacity style={styles.languageButton} onPress={toggleLanguage}>
          <Text style={styles.languageText}>
            {language === 'en' ? 'ಕನ್ನಡ' : 'English'}
          </Text>
        </TouchableOpacity>

        {/* Logo/Header */}
        <View style={styles.header}>
          <Text style={styles.appName}>{t('appName')}</Text>
          <Text style={styles.subtitle}>{t('welcomeMessage')}</Text>
        </View>

        {/* Form */}
        <View style={styles.form}>
          {step === 'phone' ? (
            <>
              <Text style={styles.label}>{t('phoneNumber')}</Text>
              <View style={styles.phoneInputContainer}>
                <Text style={styles.countryCode}>+91</Text>
                <TextInput
                  style={styles.phoneInput}
                  placeholder={t('enterPhoneNumber')}
                  value={phone}
                  onChangeText={setPhone}
                  keyboardType="phone-pad"
                  maxLength={10}
                />
              </View>

              <TouchableOpacity
                style={[styles.button, loading && styles.buttonDisabled]}
                onPress={handleRequestOTP}
                disabled={loading}
              >
                <Text style={styles.buttonText}>
                  {loading ? t('loading') : t('requestOTP')}
                </Text>
              </TouchableOpacity>
            </>
          ) : (
            <>
              <Text style={styles.label}>{t('enterOTP')}</Text>
              <TextInput
                style={styles.input}
                placeholder="000000"
                value={otp}
                onChangeText={setOTP}
                keyboardType="number-pad"
                maxLength={6}
                autoFocus
              />

              <TouchableOpacity
                style={[styles.button, loading && styles.buttonDisabled]}
                onPress={handleVerifyOTP}
                disabled={loading}
              >
                <Text style={styles.buttonText}>
                  {loading ? t('loading') : t('verifyOTP')}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.linkButton}
                onPress={() => setStep('phone')}
              >
                <Text style={styles.linkText}>{t('resendOTP')}</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
  },
  languageButton: {
    alignSelf: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#3B82F6',
    borderRadius: 8,
  },
  languageText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  header: {
    marginTop: 40,
    marginBottom: 40,
    alignItems: 'center',
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  form: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  phoneInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    marginBottom: 24,
  },
  countryCode: {
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#374151',
    borderRightWidth: 1,
    borderRightColor: '#D1D5DB',
  },
  phoneInput: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 24,
    textAlign: 'center',
    letterSpacing: 8,
  },
  button: {
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  linkButton: {
    marginTop: 16,
    alignItems: 'center',
  },
  linkText: {
    color: '#3B82F6',
    fontSize: 14,
    fontWeight: '500',
  },
});
