import { useState } from 'react';
import { censusApi } from '../services/censusApi';
import type { DemographicData } from '../types/census';

export default function MarketAnalysis() {
  const [zipcode, setZipcode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demographics, setDemographics] = useState<DemographicData | null>(null);
  const [amiPercent, setAmiPercent] = useState<30 | 50 | 60 | 80>(60);
  const [bedrooms, setBedrooms] = useState(2);
  const [amiResult, setAmiResult] = useState<any>(null);

  const handleSearch = async () => {
    if (!zipcode || zipcode.length !== 5) {
      setError('Please enter a valid 5-digit ZIP code');
      return;
    }

    setLoading(true);
    setError(null);
    setDemographics(null);
    setAmiResult(null);

    try {
      const response = await censusApi.getDemographics(zipcode);

      if (response.success && response.data) {
        setDemographics(response.data);
      } else {
        setError(response.error || 'Failed to fetch demographic data');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateAMI = async () => {
    if (!demographics) return;

    try {
      const response = await censusApi.calculateAMI({
        zipcode: demographics.zipcode,
        ami_percent: amiPercent,
        bedrooms: bedrooms,
      });

      if (response.success && response.data) {
        setAmiResult(response.data);
      }
    } catch (err) {
      console.error('Error calculating AMI:', err);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Market Analysis</h1>

      {/* Search Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Search Demographics by ZIP Code</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Enter ZIP Code (e.g., 95814)"
            value={zipcode}
            onChange={(e) => setZipcode(e.target.value)}
            maxLength={5}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : 'Search'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Demographics Results */}
      {demographics && (
        <>
          {/* Population Overview */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">
              Demographics for ZIP Code {demographics.zipcode}
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Data Year: {demographics.dataYear} | Last Updated: {new Date(demographics.lastUpdated).toLocaleDateString()}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Total Population</p>
                <p className="text-2xl font-bold text-blue-900">
                  {formatNumber(demographics.population.total_population)}
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600">Total Households</p>
                <p className="text-2xl font-bold text-green-900">
                  {formatNumber(demographics.population.total_households)}
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600">Avg Household Size</p>
                <p className="text-2xl font-bold text-purple-900">
                  {demographics.population.avg_household_size.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          {/* Income Statistics */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Income Statistics</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm text-gray-600">Median Income</p>
                <p className="text-xl font-bold text-yellow-900">
                  {formatCurrency(demographics.income.median_household_income)}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">30% AMI</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(demographics.income.ami_30_percent)}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">50% AMI</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(demographics.income.ami_50_percent)}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">60% AMI</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(demographics.income.ami_60_percent)}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">80% AMI</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(demographics.income.ami_80_percent)}
                </p>
              </div>
            </div>

            {/* Income Distribution Chart */}
            <h3 className="text-lg font-semibold mb-3">Income Distribution</h3>
            <div className="space-y-2">
              {Object.entries(demographics.income.income_distribution).map(([bracket, count]) => {
                const total = demographics.population.total_households;
                const percentage = total > 0 ? (count / total) * 100 : 0;
                const formattedBracket = bracket.replace(/_/g, ' ').replace(/k/g, 'K');

                return (
                  <div key={bracket} className="flex items-center gap-4">
                    <div className="w-32 text-sm text-gray-600">{formattedBracket}</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                      <div
                        className="bg-blue-600 h-6 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-semibold">
                        {formatNumber(count)} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Housing Market */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Housing Market</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-indigo-50 rounded-lg">
                <p className="text-sm text-gray-600">Median Home Value</p>
                <p className="text-xl font-bold text-indigo-900">
                  {formatCurrency(demographics.housing.median_home_value)}
                </p>
              </div>
              <div className="p-4 bg-pink-50 rounded-lg">
                <p className="text-sm text-gray-600">Median Rent</p>
                <p className="text-xl font-bold text-pink-900">
                  {formatCurrency(demographics.housing.median_gross_rent)}
                </p>
              </div>
              <div className="p-4 bg-teal-50 rounded-lg">
                <p className="text-sm text-gray-600">Total Housing Units</p>
                <p className="text-xl font-bold text-teal-900">
                  {formatNumber(demographics.housing.total_housing_units)}
                </p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <p className="text-sm text-gray-600">Occupancy Rate</p>
                <p className="text-xl font-bold text-orange-900">
                  {demographics.housing.occupancy_rate.toFixed(1)}%
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <p className="text-sm text-gray-600">Occupied Units</p>
                <p className="text-lg font-semibold">{formatNumber(demographics.housing.occupied_units)}</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <p className="text-sm text-gray-600">Owner Occupied</p>
                <p className="text-lg font-semibold">{formatNumber(demographics.housing.owner_occupied)}</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <p className="text-sm text-gray-600">Renter Occupied</p>
                <p className="text-lg font-semibold">{formatNumber(demographics.housing.renter_occupied)}</p>
              </div>
            </div>
          </div>

          {/* Employment */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Employment</h2>
            <div className="p-4 bg-red-50 rounded-lg inline-block">
              <p className="text-sm text-gray-600">Unemployment Rate</p>
              <p className="text-2xl font-bold text-red-900">
                {demographics.unemploymentRate.toFixed(1)}%
              </p>
            </div>
          </div>

          {/* AMI Calculator */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">AMI Rent Calculator</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AMI Percentage
                </label>
                <select
                  value={amiPercent}
                  onChange={(e) => setAmiPercent(parseInt(e.target.value) as 30 | 50 | 60 | 80)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={30}>30% AMI</option>
                  <option value={50}>50% AMI</option>
                  <option value={60}>60% AMI</option>
                  <option value={80}>80% AMI</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bedrooms
                </label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  value={bedrooms}
                  onChange={(e) => setBedrooms(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={handleCalculateAMI}
                  className="w-full px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Calculate
                </button>
              </div>
            </div>

            {amiResult && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">Calculation Results</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Income Limit ({amiResult.ami_percent}% AMI)</p>
                    <p className="text-lg font-bold text-green-900">
                      {formatCurrency(amiResult.ami_income_limit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Maximum Monthly Rent</p>
                    <p className="text-lg font-bold text-green-900">
                      {formatCurrency(amiResult.max_rent)}
                    </p>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Based on 30% of monthly income for {amiResult.bedrooms} bedroom unit
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
