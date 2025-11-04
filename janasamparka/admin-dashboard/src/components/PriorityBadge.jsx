import React from 'react';
import PropTypes from 'prop-types';

/**
 * PriorityBadge - Displays complaint priority score with visual indicators
 * 
 * Features:
 * - Visual priority levels (URGENT, HIGH, MEDIUM, LOW)
 * - Queue position display
 * - Emergency indicator
 * - SLA countdown
 */
const PriorityBadge = ({ 
  score, 
  isEmergency = false, 
  queuePosition = null,
  slaDeadline = null,
  category = 'general'
}) => {
  // Determine priority level from score (0-1)
  const getPriorityLevel = (score) => {
    if (score >= 0.8) return 'urgent';
    if (score >= 0.6) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
  };

  const priority = score ? getPriorityLevel(score) : 'low';

  // Priority styling
  const priorityStyles = {
    urgent: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-500',
      icon: '🚨',
      label: 'URGENT'
    },
    high: {
      bg: 'bg-orange-100',
      text: 'text-orange-800',
      border: 'border-orange-500',
      icon: '⚠️',
      label: 'HIGH'
    },
    medium: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      border: 'border-yellow-500',
      icon: '📌',
      label: 'MEDIUM'
    },
    low: {
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      border: 'border-gray-500',
      icon: '📋',
      label: 'LOW'
    }
  };

  const style = priorityStyles[priority];

  // Calculate days remaining for SLA
  const getDaysRemaining = () => {
    if (!slaDeadline) return null;
    const deadline = new Date(slaDeadline);
    const today = new Date();
    const diffTime = deadline - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysRemaining = getDaysRemaining();
  const isOverdue = daysRemaining !== null && daysRemaining < 0;
  const isNearDeadline = daysRemaining !== null && daysRemaining <= 2 && daysRemaining >= 0;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Priority Badge */}
      <div 
        className={`
          inline-flex items-center gap-1 px-3 py-1 rounded-full border-2
          ${style.bg} ${style.text} ${style.border}
          font-semibold text-sm
          ${isEmergency ? 'animate-pulse' : ''}
        `}
      >
        <span className="text-base">{style.icon}</span>
        <span>{style.label}</span>
        {score && (
          <span className="ml-1 text-xs opacity-75">
            ({(score * 100).toFixed(0)})
          </span>
        )}
      </div>

      {/* Queue Position */}
      {queuePosition !== null && queuePosition > 0 && (
        <div className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-blue-100 text-blue-800 text-xs font-medium">
          <span>#{queuePosition}</span>
          <span className="opacity-75">in queue</span>
        </div>
      )}

      {/* SLA Countdown */}
      {daysRemaining !== null && (
        <div 
          className={`
            inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium
            ${isOverdue 
              ? 'bg-red-100 text-red-800' 
              : isNearDeadline 
                ? 'bg-orange-100 text-orange-800'
                : 'bg-green-100 text-green-800'
            }
          `}
        >
          <span>⏱</span>
          {isOverdue ? (
            <span className="font-bold">OVERDUE by {Math.abs(daysRemaining)} days</span>
          ) : (
            <span>{daysRemaining} {daysRemaining === 1 ? 'day' : 'days'} left</span>
          )}
        </div>
      )}

      {/* Emergency Indicator */}
      {isEmergency && (
        <div className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-red-600 text-white text-xs font-bold animate-pulse">
          <span>🆘</span>
          <span>EMERGENCY</span>
        </div>
      )}
    </div>
  );
};

PriorityBadge.propTypes = {
  score: PropTypes.number, // 0-1 priority score
  isEmergency: PropTypes.bool,
  queuePosition: PropTypes.number,
  slaDeadline: PropTypes.string, // ISO date string
  category: PropTypes.string
};

export default PriorityBadge;
