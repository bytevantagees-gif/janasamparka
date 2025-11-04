import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  Image,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from '../../locales/translations';
import { complaintsAPI } from '../../services/api';
import { Picker } from '@react-native-picker/picker';

export default function SubmitComplaintScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { language } = useLanguage();
  const { t } = useTranslation(language);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    latitude: null,
    longitude: null,
    images: [],
  });

  const [locationLoading, setLocationLoading] = useState(false);
  const [locationSource, setLocationSource] = useState(null); // 'gps', 'exif', or null

  const categories = [
    { value: 'roads', label: t('roads') },
    { value: 'water', label: t('water') },
    { value: 'electricity', label: t('electricity') },
    { value: 'drainage', label: t('drainage') },
    { value: 'sanitation', label: t('sanitation') },
    { value: 'street_lights', label: t('streetLights') },
    { value: 'parks', label: t('parks') },
    { value: 'other', label: t('other') },
  ];

  // Helper function to convert EXIF GPS coordinates to decimal degrees
  const convertExifToDecimal = (coordinate, ref) => {
    if (!coordinate || !Array.isArray(coordinate) || coordinate.length !== 3) {
      return null;
    }
    
    const degrees = coordinate[0];
    const minutes = coordinate[1];
    const seconds = coordinate[2];
    
    let decimal = degrees + minutes / 60 + seconds / 3600;
    
    // Adjust for hemisphere
    if (ref === 'S' || ref === 'W') {
      decimal = -decimal;
    }
    
    return decimal;
  };

  // Helper function to extract GPS from EXIF data
  const extractGPSFromExif = (exif) => {
    if (!exif) return null;
    
    const latitude = convertExifToDecimal(exif.GPSLatitude, exif.GPSLatitudeRef);
    const longitude = convertExifToDecimal(exif.GPSLongitude, exif.GPSLongitudeRef);
    
    if (latitude !== null && longitude !== null) {
      return { latitude, longitude };
    }
    
    return null;
  };

  const submitMutation = useMutation({
    mutationFn: (data) => complaintsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['myComplaints']);
      Alert.alert(t('success'), t('complaintSubmitted'), [
        {
          text: 'OK',
          onPress: () => {
            router.push('/(tabs)/complaints');
            // Reset form
            setFormData({
              title: '',
              description: '',
              category: '',
              latitude: null,
              longitude: null,
              images: [],
            });
            setLocationSource(null);
          },
        },
      ]);
    },
    onError: () => {
      Alert.alert(t('error'), t('complaintSubmitError'));
    },
  });

  const captureLocation = async () => {
    setLocationLoading(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('locationPermission'), t('locationPermissionMessage'), [
          { text: t('cancel'), style: 'cancel' },
          { text: t('openSettings'), onPress: () => Linking.openSettings() },
        ]);
        setLocationLoading(false);
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setFormData({
        ...formData,
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
      setLocationSource('gps');
      Alert.alert(t('success'), t('locationCaptured'));
    } catch (error) {
      Alert.alert(t('error'), t('locationError'));
    } finally {
      setLocationLoading(false);
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('cameraPermission'), t('cameraPermissionMessage'), [
          { text: t('cancel'), style: 'cancel' },
          { text: t('openSettings'), onPress: () => Linking.openSettings() },
        ]);
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.8,
        exif: true, // Request EXIF data
      });

      if (!result.canceled) {
        const asset = result.assets[0];
        
        // Try to extract GPS from EXIF first
        const gpsFromExif = extractGPSFromExif(asset.exif);
        
        if (gpsFromExif && !formData.latitude) {
          // Use EXIF GPS if no location captured yet
          setFormData({
            ...formData,
            images: [...formData.images, asset],
            latitude: gpsFromExif.latitude,
            longitude: gpsFromExif.longitude,
          });
          setLocationSource('exif');
          Alert.alert(
            t('success'),
            'Photo captured with GPS location from image metadata'
          );
        } else if (gpsFromExif) {
          // Photo has GPS but user already set location
          setFormData({
            ...formData,
            images: [...formData.images, asset],
          });
          Alert.alert(
            'Photo GPS Available',
            'This photo contains GPS data. Would you like to use it instead?',
            [
              {
                text: 'Keep Current',
                style: 'cancel',
              },
              {
                text: 'Use Photo GPS',
                onPress: () => {
                  setFormData(prev => ({
                    ...prev,
                    latitude: gpsFromExif.latitude,
                    longitude: gpsFromExif.longitude,
                  }));
                  setLocationSource('exif');
                },
              },
            ]
          );
        } else {
          // No EXIF GPS
          setFormData({
            ...formData,
            images: [...formData.images, asset],
          });
          if (!formData.latitude) {
            Alert.alert(
              'No GPS in Photo',
              'This photo does not contain GPS data. Please use "Capture Location" button.',
              [{ text: 'OK' }]
            );
          }
        }
      }
    } catch (error) {
      Alert.alert(t('error'), t('cameraError'));
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.8,
        exif: true, // Request EXIF data
      });

      if (!result.canceled) {
        const asset = result.assets[0];
        
        // Try to extract GPS from EXIF first
        const gpsFromExif = extractGPSFromExif(asset.exif);
        
        if (gpsFromExif && !formData.latitude) {
          // Use EXIF GPS if no location captured yet
          setFormData({
            ...formData,
            images: [...formData.images, asset],
            latitude: gpsFromExif.latitude,
            longitude: gpsFromExif.longitude,
          });
          setLocationSource('exif');
          Alert.alert(
            t('success'),
            'Location extracted from photo metadata'
          );
        } else if (gpsFromExif) {
          // Photo has GPS but user already set location
          setFormData({
            ...formData,
            images: [...formData.images, asset],
          });
          Alert.alert(
            'Photo GPS Available',
            'This photo contains GPS data. Would you like to use it instead?',
            [
              {
                text: 'Keep Current',
                style: 'cancel',
              },
              {
                text: 'Use Photo GPS',
                onPress: () => {
                  setFormData(prev => ({
                    ...prev,
                    latitude: gpsFromExif.latitude,
                    longitude: gpsFromExif.longitude,
                  }));
                  setLocationSource('exif');
                },
              },
            ]
          );
        } else {
          // No EXIF GPS
          setFormData({
            ...formData,
            images: [...formData.images, asset],
          });
          if (!formData.latitude) {
            Alert.alert(
              'No GPS in Photo',
              'This photo does not contain GPS data. Please use "Capture Location" button.',
              [{ text: 'OK' }]
            );
          }
        }
      }
    } catch (error) {
      Alert.alert(t('error'), 'Failed to pick image');
    }
  };

  const removeImage = (index) => {
    const newImages = formData.images.filter((_, i) => i !== index);
    setFormData({ ...formData, images: newImages });
  };

  const handleSubmit = () => {
    if (!formData.title || !formData.description || !formData.category) {
      Alert.alert(t('error'), 'Please fill in all required fields');
      return;
    }

    if (!formData.latitude || !formData.longitude) {
      Alert.alert(t('error'), 'Please capture location');
      return;
    }

    submitMutation.mutate(formData);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.form}>
        {/* Title */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>{t('complaintTitle')} *</Text>
          <TextInput
            style={styles.input}
            placeholder={t('enterTitle')}
            value={formData.title}
            onChangeText={(text) => setFormData({ ...formData, title: text })}
          />
        </View>

        {/* Description */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>{t('description')} *</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder={t('enterDescription')}
            value={formData.description}
            onChangeText={(text) => setFormData({ ...formData, description: text })}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />
        </View>

        {/* Category */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>{t('category')} *</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={formData.category}
              onValueChange={(value) => setFormData({ ...formData, category: value })}
              style={styles.picker}
            >
              <Picker.Item label={t('selectCategory')} value="" />
              {categories.map((cat) => (
                <Picker.Item key={cat.value} label={cat.label} value={cat.value} />
              ))}
            </Picker>
          </View>
        </View>

        {/* Location */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>{t('location')} *</Text>
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={captureLocation}
            disabled={locationLoading}
          >
            {locationLoading ? (
              <ActivityIndicator color="#3B82F6" />
            ) : (
              <>
                <Ionicons name="location" size={20} color="#3B82F6" />
                <Text style={styles.secondaryButtonText}>
                  {formData.latitude
                    ? t('locationCaptured')
                    : t('captureLocation')}
                </Text>
                {formData.latitude && (
                  <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                )}
              </>
            )}
          </TouchableOpacity>
          {/* Location Source Indicator */}
          {formData.latitude && locationSource && (
            <View style={styles.locationInfo}>
              <Ionicons 
                name={locationSource === 'exif' ? 'camera' : 'navigate'} 
                size={16} 
                color="#6B7280" 
              />
              <Text style={styles.locationInfoText}>
                {locationSource === 'exif' 
                  ? 'Location from photo metadata' 
                  : 'Location from device GPS'}
              </Text>
            </View>
          )}
        </View>

        {/* Photos */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>{t('photos')}</Text>
          <View style={styles.photoButtons}>
            <TouchableOpacity
              style={[styles.button, styles.secondaryButton, { flex: 1 }]}
              onPress={takePhoto}
            >
              <Ionicons name="camera" size={20} color="#3B82F6" />
              <Text style={styles.secondaryButtonText}>{t('takePhoto')}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, styles.secondaryButton, { flex: 1 }]}
              onPress={pickImage}
            >
              <Ionicons name="images" size={20} color="#3B82F6" />
              <Text style={styles.secondaryButtonText}>{t('chooseFromGallery')}</Text>
            </TouchableOpacity>
          </View>

          {/* Image Preview */}
          {formData.images.length > 0 && (
            <View style={styles.imageGrid}>
              {formData.images.map((image, index) => (
                <View key={index} style={styles.imageContainer}>
                  <Image source={{ uri: image.uri }} style={styles.image} />
                  <TouchableOpacity
                    style={styles.removeImageButton}
                    onPress={() => removeImage(index)}
                  >
                    <Ionicons name="close-circle" size={24} color="#EF4444" />
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          )}
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.button, styles.submitButton, submitMutation.isPending && styles.buttonDisabled]}
          onPress={handleSubmit}
          disabled={submitMutation.isPending}
        >
          {submitMutation.isPending ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.submitButtonText}>{t('submit')}</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  form: {
    padding: 16,
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1F2937',
  },
  textArea: {
    minHeight: 100,
    paddingTop: 12,
  },
  pickerContainer: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    gap: 8,
  },
  secondaryButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#3B82F6',
  },
  secondaryButtonText: {
    color: '#3B82F6',
    fontSize: 14,
    fontWeight: '600',
  },
  submitButton: {
    backgroundColor: '#3B82F6',
    marginTop: 8,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  photoButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  imageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 16,
  },
  imageContainer: {
    position: 'relative',
  },
  image: {
    width: 100,
    height: 100,
    borderRadius: 8,
  },
  removeImageButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#F3F4F6',
    borderRadius: 6,
    gap: 6,
  },
  locationInfoText: {
    fontSize: 12,
    color: '#6B7280',
    fontStyle: 'italic',
  },
});
