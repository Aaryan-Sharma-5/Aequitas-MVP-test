import { useState, useEffect } from 'react';
import { Users, TrendingUp, TrendingDown, Mail, Phone, AlertTriangle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend
} from 'recharts';
import { gpApi } from '../services/gpApi';
import type { GP, GPPerformanceComparison, GPTopPerformers, GPOverview } from '../types/gp';

const GPPortfolio = () => {
  const [gps, setGps] = useState<GP[]>([]);
  const [performanceComparison, setPerformanceComparison] = useState<GPPerformanceComparison[]>([]);
  const [topPerformers, setTopPerformers] = useState<GPTopPerformers | null>(null);
  const [selectedGPOverviews, setSelectedGPOverviews] = useState<Map<number, GPOverview>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [partnerFilter, setPartnerFilter] = useState<string>('all');
  const [timeFilter, setTimeFilter] = useState<string>('5years');

  useEffect(() => {
    loadGPData();
  }, []);

  const loadGPData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all GPs and related data
      const [gpsData, comparisonData, performersData] = await Promise.all([
        gpApi.getAllGPs(),
        gpApi.getPerformanceComparison(),
        gpApi.getTopPerformers()
      ]);

      setGps(gpsData);
      setPerformanceComparison(comparisonData);
      setTopPerformers(performersData);

      // Fetch detailed overviews for first 2 GPs (for display)
      if (gpsData.length > 0) {
        const overviews = new Map<number, GPOverview>();
        const limit = Math.min(2, gpsData.length);

        for (let i = 0; i < limit; i++) {
          const gp = gpsData[i];
          if (gp.id) {
            try {
              const overview = await gpApi.getGPOverview(gp.id);
              overviews.set(gp.id, overview);
            } catch (err) {
              console.error(`Failed to load overview for GP ${gp.id}:`, err);
            }
          }
        }

        setSelectedGPOverviews(overviews);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load GP data');
      console.error('Error loading GP data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A';
    return `${value.toFixed(1)}%`;
  };

  const getTierColor = (tier: string | undefined) => {
    switch (tier?.toLowerCase()) {
      case 'premium':
        return 'bg-purple-100 text-purple-700';
      case 'standard':
        return 'bg-blue-100 text-blue-700';
      case 'excellent':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getPerformanceColor = (rating: string | undefined) => {
    switch (rating?.toLowerCase()) {
      case 'outstanding':
        return 'bg-green-100 text-green-700';
      case 'excellent':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading GP Portfolio...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">Error: {error}</p>
          <button
            onClick={loadGPData}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold text-gray-800">GP Portfolio</h1>
          <p className="text-sm text-gray-500 mt-1">General Partner relationships and performance analytics</p>
        </div>

        {/* Filters */}
        <div className="flex gap-3">
          <select
            value={partnerFilter}
            onChange={(e) => setPartnerFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Partners</option>
            <option value="10">10 Partners</option>
            <option value="5">5 Partners</option>
          </select>

          <select
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1year">Last 1 Yr</option>
            <option value="3years">Last 3 Yrs</option>
            <option value="5years">Last 5 Yrs</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {/* Performance Comparison Chart */}
      <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">IRR Performance Comparison</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={performanceComparison}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="gpName"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis
              tick={{ fontSize: 12 }}
              label={{ value: 'Net IRR (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              formatter={(value: number) => `${value.toFixed(1)}%`}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb' }}
            />
            <Bar dataKey="netIrr" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Top Portfolio IRR */}
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-gray-500 mb-1">Top Portfolio IRR</p>
              <p className="text-2xl font-bold text-gray-800">
                {topPerformers?.topPerformer?.netIrr
                  ? formatPercentage(topPerformers.topPerformer.netIrr)
                  : 'N/A'
                }
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {topPerformers?.topPerformer?.gpName || 'No data'}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
              <TrendingUp size={24} className="text-green-500" />
            </div>
          </div>
        </div>

        {/* Top Performer Recent Quarter */}
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-gray-500 mb-1">Top Performer Recent Quarter</p>
              <p className="text-2xl font-bold text-gray-800">
                {topPerformers?.topPerformer?.performanceRating || 'N/A'}
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {topPerformers?.topPerformer?.gpName || 'No data'}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
              <Users size={24} className="text-blue-500" />
            </div>
          </div>
        </div>

        {/* Needs Attention */}
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-xs text-gray-500 mb-1">Needs Attention</p>
              {topPerformers?.needsAttention && topPerformers.needsAttention.length > 0 ? (
                <div>
                  <p className="text-lg font-bold text-orange-600">
                    {topPerformers.needsAttention[0].gpName}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {topPerformers.needsAttention[0].reason}
                  </p>
                </div>
              ) : (
                <p className="text-lg font-bold text-gray-800">All on track</p>
              )}
            </div>
            <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center">
              <AlertTriangle size={24} className="text-orange-500" />
            </div>
          </div>
        </div>
      </div>

      {/* GP Cards */}
      <div className="space-y-6">
        {Array.from(selectedGPOverviews.entries()).map(([gpId, overview]) => {
          const gp = overview.gp;

          return (
            <div key={gpId} className="bg-white rounded-xl p-6 shadow-sm">
              {/* GP Header */}
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">{gp.gpName}</h3>
                  <p className="text-sm text-gray-500">{gp.location}</p>

                  {/* Contact Info */}
                  <div className="flex gap-4 mt-2">
                    {gp.contactEmail && (
                      <div className="flex items-center gap-1 text-xs text-gray-600">
                        <Mail size={14} />
                        <span>{gp.contactEmail}</span>
                      </div>
                    )}
                    {gp.contactPhone && (
                      <div className="flex items-center gap-1 text-xs text-gray-600">
                        <Phone size={14} />
                        <span>{gp.contactPhone}</span>
                      </div>
                    )}
                  </div>

                  {/* Tags */}
                  <div className="flex gap-2 mt-3">
                    {gp.tier && (
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTierColor(gp.tier)}`}>
                        {gp.tier}
                      </span>
                    )}
                    {gp.performanceRating && (
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPerformanceColor(gp.performanceRating)}`}>
                        {gp.performanceRating}
                      </span>
                    )}
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                      IRR Performance
                    </span>
                  </div>
                </div>
              </div>

              {/* Performance Metrics and Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column - Metrics */}
                <div>
                  {/* IRR Performance */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">IRR Performance</span>
                      <span className="text-lg font-semibold text-gray-800">
                        {formatPercentage(gp.netIrr)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${Math.min((gp.netIrr || 0) * 5, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Gross IRR */}
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600">Gross IRR</span>
                    <span className="text-sm font-semibold text-gray-800">
                      {formatPercentage(gp.grossIrr)}
                    </span>
                  </div>

                  {/* IRR Trend */}
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm text-gray-600">Trend</span>
                    <div className="flex items-center gap-1">
                      {(gp.irrTrend || 0) >= 0 ? (
                        <TrendingUp size={16} className="text-green-500" />
                      ) : (
                        <TrendingDown size={16} className="text-red-500" />
                      )}
                      <span className={`text-sm font-semibold ${(gp.irrTrend || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {formatPercentage(Math.abs(gp.irrTrend || 0))}
                      </span>
                    </div>
                  </div>

                  {/* Recent IRR Trend Chart */}
                  <div className="mt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Recent IRR Trend</h4>
                    <ResponsiveContainer width="100%" height={150}>
                      <LineChart data={overview.quarterlyPerformance.slice().reverse()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis
                          dataKey="quarterLabel"
                          tick={{ fontSize: 10 }}
                        />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip
                          formatter={(value: number) => `${value.toFixed(1)}%`}
                        />
                        <Line
                          type="monotone"
                          dataKey="irr"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={{ fill: '#3b82f6', r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Right Column - Portfolio Summary */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Portfolio Summary</h4>

                  {/* Recent Deal Performance */}
                  <div className="mb-4">
                    <p className="text-xs text-gray-500 mb-2">Recent Deal Performance</p>
                    <div className="space-y-2">
                      {overview.portfolioSummary.map((summary) => (
                        <div key={summary.quartile}>
                          <div className="flex justify-between items-center text-xs mb-1">
                            <span className="text-gray-600">
                              {summary.year} - {summary.quartile} asset{summary.dealCount !== 1 ? 's' : ''}
                            </span>
                            <span className="font-semibold text-gray-800">
                              {formatPercentage(summary.percentage)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Additional Metrics */}
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Total Units</p>
                      <p className="text-lg font-bold text-gray-800">{gp.dealCount || 0}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Current Value</p>
                      <p className="text-lg font-bold text-gray-800">
                        {formatCurrency(gp.currentValue)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Show message if no GPs */}
      {gps.length === 0 && (
        <div className="bg-white rounded-xl p-8 shadow-sm text-center">
          <Users size={48} className="text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No GPs found. Add your first General Partner to get started.</p>
        </div>
      )}
    </div>
  );
};

export default GPPortfolio;
