import { useState } from 'react';
import { MapPin, Home, DollarSign, Filter } from 'lucide-react';
import PropertyMap from '../components/PropertyMap';

const MapPage = () => {
  const [activeTab, setActiveTab] = useState<'existing' | 'potential'>('existing');

  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8 bg-gray-50">
      <div className="flex flex-col items-start justify-between gap-4 mb-6 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800 md:text-3xl">Geographic Investment Map</h1>
          <p className="mt-1 text-sm text-gray-500">Explore existing deals and potential opportunities</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'existing'
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setActiveTab('existing')}
          >
            Existing Deals
          </button>
          <button
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeTab === 'potential'
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setActiveTab('potential')}
          >
            Potential Deals
          </button>
          <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 transition-colors bg-white rounded-lg hover:bg-gray-100">
            <Filter size={16} />
            Filters
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Map Container */}
        <div className="flex flex-col overflow-hidden bg-white shadow-sm lg:col-span-2 rounded-xl">
          <div className="h-[500px] md:h-[600px]">
            <PropertyMap />
          </div>

          {/* Legend */}
          <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-4 border-t border-gray-200">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                <span className="text-sm text-gray-700">Existing Deals</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="text-sm text-gray-700">Potential Opportunities</span>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>S: 150 units</span>
              <span>M: 150-200 units</span>
              <span>L: 200 units</span>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Selected Deal Card */}
          <div className="p-6 bg-white shadow-sm rounded-xl">
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <MapPin size={48} color="#e5e7eb" />
              <p className="mt-3 text-sm text-gray-500">Select a deal on the map to view details</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="p-6 bg-white shadow-sm rounded-xl">
            <h3 className="mb-4 text-lg font-semibold text-gray-800">Quick Stats</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center flex-shrink-0 w-10 h-10 rounded-lg bg-blue-50">
                  <Home size={16} className="text-blue-500" />
                </div>
                <div className="flex-1">
                  <span className="block text-xs text-gray-500">Total Units</span>
                  <span className="block text-lg font-bold text-gray-800">780</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center flex-shrink-0 w-10 h-10 rounded-lg bg-purple-50">
                  <DollarSign size={16} className="text-purple-500" />
                </div>
                <div className="flex-1">
                  <span className="block text-xs text-gray-500">Total Investment</span>
                  <span className="block text-lg font-bold text-gray-800">$150.0M</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center flex-shrink-0 w-10 h-10 rounded-lg bg-green-50">
                  <MapPin size={16} className="text-green-500" />
                </div>
                <div className="flex-1">
                  <span className="block text-xs text-gray-500">Markets</span>
                  <span className="block text-lg font-bold text-gray-800">4 Cities</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapPage;
