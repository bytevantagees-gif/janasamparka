import { useState } from 'react';
import { X, Building2, AlertCircle, CheckCircle, User } from 'lucide-react';

function DepartmentAssignModal({ isOpen, onClose, complaint, onAssign }) {
  const [selectedDepartment, setSelectedDepartment] = useState(complaint?.dept_id || '');
  const [selectedOfficer, setSelectedOfficer] = useState('');
  const [priority, setPriority] = useState(complaint?.priority || 'medium');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  // Mock departments data - replace with API call
  const departments = [
    { id: '1', name: 'Public Works Department (PWD)', code: 'PWD', officers: [
      { id: 'o1', name: 'Engineer Ramesh Kumar' },
      { id: 'o2', name: 'Officer Suresh Naik' },
    ]},
    { id: '2', name: 'Water Supply Department', code: 'WSD', officers: [
      { id: 'o3', name: 'Officer Sanjay Rao' },
      { id: 'o4', name: 'Engineer Prakash' },
    ]},
    { id: '3', name: 'Electricity Department (MESCOM)', code: 'MESCOM', officers: [
      { id: 'o5', name: 'Engineer Prakash Shetty' },
      { id: 'o6', name: 'Technician Mohan Das' },
    ]},
    { id: '4', name: 'Sanitation & Health', code: 'HEALTH', officers: [
      { id: 'o7', name: 'Dr. Anita Bhat' },
      { id: 'o8', name: 'Officer Vijay Kumar' },
    ]},
    { id: '5', name: 'Education Department', code: 'EDU', officers: [
      { id: 'o9', name: 'Principal Mohan Das' },
      { id: 'o10', name: 'Officer Ravi Shankar' },
    ]},
  ];

  const selectedDept = departments.find(d => d.id === selectedDepartment);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedDepartment) {
      alert('Please select a department');
      return;
    }

    setLoading(true);
    
    try {
      await onAssign({
        complaint_id: complaint.id,
        department_id: selectedDepartment,
        officer_id: selectedOfficer || null,
        priority: priority,
        note: note.trim(),
      });
      
      onClose();
    } catch (error) {
      alert('Failed to assign department: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-suggest department based on category
  const getSuggestedDepartment = () => {
    const category = complaint?.category?.toLowerCase();
    if (category === 'road' || category === 'infrastructure') return departments[0];
    if (category === 'water') return departments[1];
    if (category === 'electricity') return departments[2];
    if (category === 'sanitation' || category === 'health') return departments[3];
    if (category === 'education') return departments[4];
    return null;
  };

  const suggestedDept = getSuggestedDepartment();

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          aria-hidden="true"
          onClick={onClose}
        ></div>

        {/* Center modal */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900" id="modal-title">
              Assign Department
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Complaint Info */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-900 mb-1">{complaint?.title}</p>
            <p className="text-xs text-gray-500">Category: {complaint?.category}</p>
            {complaint?.dept_name && (
              <p className="text-xs text-gray-600 mt-2">
                Currently assigned to: <span className="font-medium">{complaint.dept_name}</span>
              </p>
            )}
          </div>

          {/* Auto-suggestion */}
          {suggestedDept && !selectedDepartment && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-blue-800">
                    <strong>Suggested:</strong> {suggestedDept.name}
                  </p>
                  <button
                    type="button"
                    onClick={() => setSelectedDepartment(suggestedDept.id)}
                    className="mt-2 text-xs text-blue-700 hover:text-blue-800 font-medium underline"
                  >
                    Use this department
                  </button>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Department Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Department <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedDepartment}
                onChange={(e) => {
                  setSelectedDepartment(e.target.value);
                  setSelectedOfficer(''); // Reset officer when department changes
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                required
              >
                <option value="">-- Select Department --</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name} ({dept.code})
                  </option>
                ))}
              </select>
            </div>

            {/* Officer Selection (if department selected) */}
            {selectedDept && selectedDept.officers.length > 0 && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Assign to Officer (Optional)
                </label>
                <select
                  value={selectedOfficer}
                  onChange={(e) => setSelectedOfficer(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">-- Department Head will assign --</option>
                  {selectedDept.officers.map((officer) => (
                    <option key={officer.id} value={officer.id}>
                      {officer.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Priority Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority Level
              </label>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { value: 'low', label: 'Low', color: 'gray' },
                  { value: 'medium', label: 'Medium', color: 'blue' },
                  { value: 'high', label: 'High', color: 'yellow' },
                  { value: 'urgent', label: 'Urgent', color: 'red' },
                ].map((p) => (
                  <label
                    key={p.value}
                    className={`flex items-center justify-center p-2 border-2 rounded-lg cursor-pointer transition-all ${
                      priority === p.value
                        ? `border-${p.color}-500 bg-${p.color}-50`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="priority"
                      value={p.value}
                      checked={priority === p.value}
                      onChange={(e) => setPriority(e.target.value)}
                      className="sr-only"
                    />
                    <span className={`text-sm font-medium ${
                      priority === p.value ? `text-${p.color}-700` : 'text-gray-700'
                    }`}>
                      {p.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Assignment Note */}
            <div className="mb-6">
              <label htmlFor="note" className="block text-sm font-medium text-gray-700 mb-2">
                Assignment Note (Optional)
              </label>
              <textarea
                id="note"
                rows="3"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add instructions or context for the assigned department..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Assignment Summary */}
            {selectedDepartment && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-green-800">
                      <strong>Assignment Summary:</strong>
                    </p>
                    <ul className="mt-2 text-sm text-green-700 space-y-1">
                      <li>• Department: {selectedDept?.name}</li>
                      {selectedOfficer && (
                        <li>• Officer: {selectedDept?.officers.find(o => o.id === selectedOfficer)?.name}</li>
                      )}
                      <li>• Priority: {priority.charAt(0).toUpperCase() + priority.slice(1)}</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !selectedDepartment}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Assigning...
                  </>
                ) : (
                  <>
                    <Building2 className="mr-2 h-4 w-4" />
                    Assign Department
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default DepartmentAssignModal;
