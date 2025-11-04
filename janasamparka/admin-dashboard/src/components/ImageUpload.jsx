/**
 * Image Upload Component
 * Supports drag & drop, multiple files, preview, and progress tracking
 */
import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, FileVideo, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';

const ImageUpload = ({ 
  complaintId, 
  photoType = 'evidence',
  onUploadComplete,
  maxFiles = 5,
  maxFileSize = 10 * 1024 * 1024, // 10MB
}) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [errors, setErrors] = useState([]);
  const fileInputRef = useRef(null);

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'video/mp4', 'video/mov'];

  const validateFile = (file) => {
    // Check file type
    if (!allowedTypes.includes(file.type)) {
      return `${file.name}: Invalid file type. Only images and videos are allowed.`;
    }

    // Check file size
    if (file.size > maxFileSize) {
      return `${file.name}: File too large. Maximum size is ${maxFileSize / (1024 * 1024)}MB.`;
    }

    return null;
  };

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files || []);
    addFiles(selectedFiles);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const droppedFiles = Array.from(event.dataTransfer.files || []);
    addFiles(droppedFiles);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const addFiles = (newFiles) => {
    const validationErrors = [];
    const validFiles = [];

    newFiles.forEach(file => {
      const error = validateFile(file);
      if (error) {
        validationErrors.push(error);
      } else {
        validFiles.push({
          file,
          id: Math.random().toString(36).substr(2, 9),
          preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
          status: 'pending'
        });
      }
    });

    if (validFiles.length + files.length > maxFiles) {
      validationErrors.push(`Maximum ${maxFiles} files allowed`);
      return;
    }

    setFiles(prev => [...prev, ...validFiles]);
    setErrors(validationErrors);
  };

  const removeFile = (fileId) => {
    setFiles(prev => {
      const file = prev.find(f => f.id === fileId);
      if (file?.preview) {
        URL.revokeObjectURL(file.preview);
      }
      return prev.filter(f => f.id !== fileId);
    });
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setErrors([]);

    const formData = new FormData();
    files.forEach(({ file }) => {
      formData.append('files', file);
    });
    formData.append('complaint_id', complaintId);
    formData.append('photo_type', photoType);

    try {
      const response = await api.post('/api/media/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress({ percent: percentCompleted });
        },
      });

      // Mark all as successful
      setFiles(prev => prev.map(f => ({ ...f, status: 'success' })));

      // Call completion callback
      if (onUploadComplete) {
        onUploadComplete(response.data);
      }

      // Clear files after a delay
      setTimeout(() => {
        files.forEach(({ preview }) => {
          if (preview) URL.revokeObjectURL(preview);
        });
        setFiles([]);
        setUploadProgress({});
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' })));
      setErrors([error.response?.data?.detail || 'Upload failed. Please try again.']);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 hover:bg-primary-50 transition-colors"
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          <span className="font-semibold text-primary-600">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Images or videos (max {maxFiles} files, {maxFileSize / (1024 * 1024)}MB each)
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={allowedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* File Preview List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">
            Selected Files ({files.length}/{maxFiles})
          </h4>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {files.map((fileItem) => (
              <div key={fileItem.id} className="relative group">
                <div className="aspect-square rounded-lg border-2 border-gray-200 overflow-hidden bg-gray-50">
                  {fileItem.preview ? (
                    <img
                      src={fileItem.preview}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <FileVideo className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                  
                  {/* Status Overlay */}
                  {fileItem.status === 'success' && (
                    <div className="absolute inset-0 bg-green-500 bg-opacity-75 flex items-center justify-center">
                      <CheckCircle className="h-8 w-8 text-white" />
                    </div>
                  )}
                  {fileItem.status === 'error' && (
                    <div className="absolute inset-0 bg-red-500 bg-opacity-75 flex items-center justify-center">
                      <AlertCircle className="h-8 w-8 text-white" />
                    </div>
                  )}
                </div>

                {/* Remove Button */}
                {fileItem.status === 'pending' && (
                  <button
                    onClick={() => removeFile(fileItem.id)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}

                {/* File Name */}
                <p className="mt-1 text-xs text-gray-600 truncate">
                  {fileItem.file.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">
                {errors.length} error{errors.length > 1 ? 's' : ''}
              </h3>
              <div className="mt-1 text-sm text-red-700">
                <ul className="list-disc pl-5 space-y-1">
                  {errors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Button */}
      {files.length > 0 && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            {files.length} file{files.length > 1 ? 's' : ''} ready to upload
          </p>
          <button
            onClick={uploadFiles}
            disabled={uploading}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                Uploading... {uploadProgress.percent}%
              </>
            ) : (
              <>
                <Upload className="-ml-1 mr-2 h-4 w-4" />
                Upload Files
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
