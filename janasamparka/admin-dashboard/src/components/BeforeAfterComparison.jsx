import { useState } from 'react';
import { ChevronLeft, ChevronRight, Maximize2, X, Calendar, User } from 'lucide-react';

const BeforeAfterComparison = ({ beforePhotos = [], afterPhotos = [] }) => {
  const [selectedBefore, setSelectedBefore] = useState(0);
  const [selectedAfter, setSelectedAfter] = useState(0);
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Handle slider drag
  const handleMouseDown = () => setIsDragging(true);
  
  const handleMouseUp = () => setIsDragging(false);
  
  const handleMouseMove = (e) => {
    if (!isDragging) return;
    const container = e.currentTarget.getBoundingClientRect();
    const position = ((e.clientX - container.left) / container.width) * 100;
    setSliderPosition(Math.min(Math.max(position, 0), 100));
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    const touch = e.touches[0];
    const container = e.currentTarget.getBoundingClientRect();
    const position = ((touch.clientX - container.left) / container.width) * 100;
    setSliderPosition(Math.min(Math.max(position, 0), 100));
  };

  const beforePhoto = beforePhotos[selectedBefore];
  const afterPhoto = afterPhotos[selectedAfter];

  if (beforePhotos.length === 0 && afterPhotos.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">No before/after photos available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Comparison Slider */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Before/After Comparison</h3>
          <p className="text-sm text-gray-500 mt-1">Drag the slider to compare photos</p>
        </div>

        <div 
          className="relative w-full aspect-[16/9] bg-gray-900 cursor-ew-resize select-none"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleMouseUp}
        >
          {/* Before Photo */}
          {beforePhoto && (
            <div className="absolute inset-0">
              <img
                src={beforePhoto.url}
                alt="Before"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                Before
              </div>
            </div>
          )}

          {/* After Photo with Clip Path */}
          {afterPhoto && (
            <div 
              className="absolute inset-0"
              style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
            >
              <img
                src={afterPhoto.url}
                alt="After"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                After
              </div>
            </div>
          )}

          {/* Slider Handle */}
          {beforePhoto && afterPhoto && (
            <>
              <div
                className="absolute top-0 bottom-0 w-1 bg-white shadow-lg cursor-ew-resize"
                style={{ left: `${sliderPosition}%` }}
                onMouseDown={handleMouseDown}
                onTouchStart={handleMouseDown}
              >
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-full p-2 shadow-lg">
                  <div className="flex items-center gap-0.5">
                    <ChevronLeft className="h-4 w-4 text-gray-700" />
                    <ChevronRight className="h-4 w-4 text-gray-700" />
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Fullscreen Button */}
          <button
            onClick={() => setIsFullscreen(true)}
            className="absolute bottom-4 right-4 bg-black/50 hover:bg-black/70 text-white p-2 rounded-lg transition-colors"
          >
            <Maximize2 className="h-5 w-5" />
          </button>

          {/* No Photos Message */}
          {!beforePhoto && !afterPhoto && (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-white text-lg">No photos to compare</p>
            </div>
          )}
        </div>

        {/* Photo Info */}
        <div className="grid grid-cols-2 divide-x divide-gray-200 bg-gray-50">
          {/* Before Info */}
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Before Photo</h4>
            {beforePhoto ? (
              <div className="space-y-2 text-xs text-gray-600">
                <div className="flex items-center gap-2">
                  <Calendar className="h-3 w-3" />
                  <span>{new Date(beforePhoto.created_at).toLocaleDateString()}</span>
                </div>
                {beforePhoto.caption && (
                  <p className="text-gray-700">{beforePhoto.caption}</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No before photo uploaded</p>
            )}
          </div>

          {/* After Info */}
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">After Photo</h4>
            {afterPhoto ? (
              <div className="space-y-2 text-xs text-gray-600">
                <div className="flex items-center gap-2">
                  <Calendar className="h-3 w-3" />
                  <span>{new Date(afterPhoto.created_at).toLocaleDateString()}</span>
                </div>
                {afterPhoto.caption && (
                  <p className="text-gray-700">{afterPhoto.caption}</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Work not yet completed</p>
            )}
          </div>
        </div>
      </div>

      {/* Thumbnail Gallery */}
      {(beforePhotos.length > 1 || afterPhotos.length > 1) && (
        <div className="grid grid-cols-2 gap-4">
          {/* Before Thumbnails */}
          {beforePhotos.length > 1 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Before Photos ({beforePhotos.length})</h4>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {beforePhotos.map((photo, index) => (
                  <button
                    key={photo.id}
                    onClick={() => setSelectedBefore(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                      selectedBefore === index ? 'border-red-500' : 'border-gray-200'
                    }`}
                  >
                    <img
                      src={photo.url}
                      alt={`Before ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* After Thumbnails */}
          {afterPhotos.length > 1 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">After Photos ({afterPhotos.length})</h4>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {afterPhotos.map((photo, index) => (
                  <button
                    key={photo.id}
                    onClick={() => setSelectedAfter(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                      selectedAfter === index ? 'border-green-500' : 'border-gray-200'
                    }`}
                  >
                    <img
                      src={photo.url}
                      alt={`After ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
          <button
            onClick={() => setIsFullscreen(false)}
            className="absolute top-4 right-4 text-white hover:text-gray-300 p-2"
          >
            <X className="h-8 w-8" />
          </button>
          
          <div 
            className="relative w-full h-full cursor-ew-resize"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleMouseUp}
          >
            {/* Before Photo */}
            {beforePhoto && (
              <div className="absolute inset-0">
                <img
                  src={beforePhoto.url}
                  alt="Before"
                  className="w-full h-full object-contain"
                />
              </div>
            )}

            {/* After Photo with Clip Path */}
            {afterPhoto && (
              <div 
                className="absolute inset-0"
                style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
              >
                <img
                  src={afterPhoto.url}
                  alt="After"
                  className="w-full h-full object-contain"
                />
              </div>
            )}

            {/* Slider Handle */}
            {beforePhoto && afterPhoto && (
              <div
                className="absolute top-0 bottom-0 w-1 bg-white shadow-lg cursor-ew-resize"
                style={{ left: `${sliderPosition}%` }}
                onMouseDown={handleMouseDown}
                onTouchStart={handleMouseDown}
              >
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-full p-3 shadow-lg">
                  <div className="flex items-center gap-1">
                    <ChevronLeft className="h-6 w-6 text-gray-700" />
                    <ChevronRight className="h-6 w-6 text-gray-700" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BeforeAfterComparison;
