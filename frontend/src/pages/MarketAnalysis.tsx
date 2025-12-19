import { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Home,
  DollarSign,
  Users,
  TrendingUp,
  Search,
  AlertCircle,
} from 'lucide-react';
import type { DemographicData } from '../types/census';

const MarketAnalysis = () => {
  const [zipcode, setZipcode] = useState('95814');
  const [demographics, setDemographics] = useState<DemographicData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDemographics = async () => {
    if (!zipcode || zipcode.length !== 5) {
      setError('Please enter a valid 5-digit ZIP code');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/demographics/${zipcode}`);
      const result = await response.json();

      if (result.success && result.data) {
        setDemographics(result.data);
      } else {
        setError(result.error || 'Failed to fetch demographics');
        setDemographics(null);
      }
    } catch (err) {
      setError('Network error: Unable to fetch market data');
      setDemographics(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      fetchDemographics();
    }
  };

  // Prepare income distribution data for chart
  const incomeDistributionData = demographics ? [
    { bracket: 'Under $25k', households:
      demographics.income.incomeDistribution.under_10k +
      demographics.income.incomeDistribution['10k_15k'] +
      demographics.income.incomeDistribution['15k_20k'] +
      demographics.income.incomeDistribution['20k_25k']
    },
    { bracket: '$25k-$50k', households:
      demographics.income.incomeDistribution['25k_30k'] +
      demographics.income.incomeDistribution['30k_35k'] +
      demographics.income.incomeDistribution['35k_40k'] +
      demographics.income.incomeDistribution['40k_45k'] +
      demographics.income.incomeDistribution['45k_50k']
    },
    { bracket: '$50k-$100k', households:
      demographics.income.incomeDistribution['50k_60k'] +
      demographics.income.incomeDistribution['60k_75k'] +
      demographics.income.incomeDistribution['75k_100k']
    },
    { bracket: '$100k-$200k', households:
      demographics.income.incomeDistribution['100k_125k'] +
      demographics.income.incomeDistribution['125k_150k'] +
      demographics.income.incomeDistribution['150k_200k']
    },
    { bracket: '$200k+', households: demographics.income.incomeDistribution['200k_plus'] },
  ] : [];

  // Housing tenure data for pie chart
  const tenureData = demographics ? [
    { name: 'Owner-Occupied', value: demographics.housing.ownerOccupied, color: '#3b82f6' },
    { name: 'Renter-Occupied', value: demographics.housing.renterOccupied, color: '#10b981' },
  ] : [];

  // Calculate affordability metrics
  const affordabilityMetrics = demographics ? {
    ami60MaxRent: Math.round((demographics.income.ami60Percent / 12) * 0.30),
    marketVsAffordable: ((demographics.housing.medianGrossRent / ((demographics.income.ami60Percent / 12) * 0.30)) * 100 - 100).toFixed(1),
  } : null;

  return (
    <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-semibold text-gray-800">Market Analysis</h1>
        <p className="text-sm text-gray-500 mt-1">Comprehensive demographic and market insights</p>
      </div>

      {/* Search Section */}
      <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
        <div className="max-w-2xl">
          <label className="block text-sm font-medium text-gray-700 mb-2">ZIP Code</label>
          <div className="flex gap-3">
            <input
              type="text"
              value={zipcode}
              onChange={(e) => setZipcode(e.target.value)}
              onKeyPress={handleKeyPress}
              maxLength={5}
              placeholder="Enter ZIP code (e.g., 95814)"
              className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
            />
            <button
              onClick={fetchDemographics}
              disabled={loading}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
            >
              {loading ? (
                'Loading...'
              ) : (
                <>
                  <Search size={16} />
                  Analyze Market
                </>
              )}
            </button>
          </div>
          {error && (
            <div className="flex items-center gap-2 mt-3 text-red-600 text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>

      {demographics && (
        <>
          {/* Overview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                  <Users size={20} className="text-blue-500" />
                </div>
                <span className="text-xs font-medium text-gray-600">Total Population</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">{demographics.population.totalPopulation.toLocaleString()}</span>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
                  <Home size={20} className="text-purple-500" />
                </div>
                <span className="text-xs font-medium text-gray-600">Total Households</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">{demographics.population.totalHouseholds.toLocaleString()}</span>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
                  <DollarSign size={20} className="text-green-500" />
                </div>
                <span className="text-xs font-medium text-gray-600">Median Income</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">${(demographics.income.medianHouseholdIncome / 1000).toFixed(0)}k</span>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center">
                  <TrendingUp size={20} className="text-orange-500" />
                </div>
                <span className="text-xs font-medium text-gray-600">Occupancy Rate</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">{demographics.housing.occupancyRate}%</span>
            </div>
          </div>

          {/* AMI Thresholds */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 shadow-sm mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Area Median Income (AMI) Thresholds</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <span className="text-xs text-indigo-600 font-medium block mb-1">30% AMI</span>
                <span className="text-xl font-bold text-indigo-900">${demographics.income.ami30Percent.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-indigo-600 font-medium block mb-1">50% AMI</span>
                <span className="text-xl font-bold text-indigo-900">${demographics.income.ami50Percent.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-indigo-600 font-medium block mb-1">60% AMI</span>
                <span className="text-xl font-bold text-indigo-900">${demographics.income.ami60Percent.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-indigo-600 font-medium block mb-1">80% AMI</span>
                <span className="text-xl font-bold text-indigo-900">${demographics.income.ami80Percent.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Income Distribution Chart */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Household Income Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={incomeDistributionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                  <XAxis
                    dataKey="bracket"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                  />
                  <Tooltip />
                  <Bar dataKey="households" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Housing Tenure Pie Chart */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Housing Tenure</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={tenureData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {tenureData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-xs text-gray-600">Owner-Occupied</p>
                  <p className="text-lg font-bold text-blue-600">{demographics.housing.ownerOccupied.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-600">Renter-Occupied</p>
                  <p className="text-lg font-bold text-green-600">{demographics.housing.renterOccupied.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Housing Market Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Housing Market</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600">Median Home Value</span>
                  <span className="text-lg font-bold text-gray-800">${demographics.housing.medianHomeValue.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600">Median Gross Rent</span>
                  <span className="text-lg font-bold text-gray-800">${demographics.housing.medianGrossRent.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600">Total Housing Units</span>
                  <span className="text-lg font-bold text-gray-800">{demographics.housing.totalHousingUnits.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                  <span className="text-sm text-gray-600">Vacancy Rate</span>
                  <span className="text-lg font-bold text-gray-800">
                    {((demographics.housing.vacantUnits / demographics.housing.totalHousingUnits) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Unemployment Rate</span>
                  <span className="text-lg font-bold text-gray-800">{demographics.unemploymentRate}%</span>
                </div>
              </div>
            </div>

            {/* Affordability Analysis */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Affordability Analysis</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-emerald-700 mb-1">60% AMI Max Affordable Rent</p>
                  <p className="text-2xl font-bold text-emerald-900">${affordabilityMetrics?.ami60MaxRent}/mo</p>
                  <p className="text-xs text-gray-600 mt-1">(30% of monthly income at 60% AMI)</p>
                </div>
                <div className="pt-4 border-t border-emerald-200">
                  <p className="text-xs text-emerald-700 mb-1">Market Median Rent</p>
                  <p className="text-2xl font-bold text-emerald-900">${demographics.housing.medianGrossRent}/mo</p>
                </div>
                <div className="pt-4 border-t border-emerald-200">
                  <p className="text-xs text-emerald-700 mb-1">Affordability Gap</p>
                  <p className={`text-2xl font-bold ${Number(affordabilityMetrics?.marketVsAffordable) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {affordabilityMetrics?.marketVsAffordable}%
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {Number(affordabilityMetrics?.marketVsAffordable) > 0
                      ? 'Market rent exceeds affordable limit'
                      : 'Market rent is within affordable range'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Data Source Info */}
          <div className="bg-gray-100 rounded-xl p-4 text-center">
            <p className="text-xs text-gray-600">
              Data Source: {demographics.dataYear} American Community Survey (ACS) 5-Year Estimates
              <br />
              Last Updated: {new Date(demographics.lastUpdated).toLocaleDateString()}
            </p>
          </div>
        </>
      )}

      {/* Empty State */}
      {!demographics && !loading && (
        <div className="bg-white rounded-xl p-12 shadow-sm text-center">
          <Search size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-800 mb-2">No Market Data</h3>
          <p className="text-sm text-gray-500">Enter a ZIP code above to analyze market demographics</p>
        </div>
      )}
    </div>
  );
};

export default MarketAnalysis;
