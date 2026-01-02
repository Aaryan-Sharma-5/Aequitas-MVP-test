import { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, ArrowUp, PieChart, Activity } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  Line,
  ComposedChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';
import { fundApi } from '../services/fundApi';
import type { FundOverview } from '../types/fund';

const FundReturns = () => {
  const [fundData, setFundData] = useState<FundOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fundApi.getFundOverview(1); // Fund ID 1
        setFundData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load fund data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Format currency in millions
  const formatCurrency = (value: number): string => {
    const millions = value / 1000000;
    return `$${millions.toFixed(1)}M`;
  };

  // Format percent
  const formatPercent = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  // Format multiplier
  const formatMultiplier = (value: number): string => {
    return `${value.toFixed(1)}x`;
  };

  // Status badge colors
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800';
      case 'In Progress':
        return 'bg-blue-100 text-blue-800';
      case 'Scheduled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading fund data...</div>
      </div>
    );
  }

  if (error || !fundData || !fundData.metrics) {
    return (
      <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen flex items-center justify-center">
        <div className="text-red-600">Error: {error || 'No fund data available'}</div>
      </div>
    );
  }

  const { fund, metrics, quarterlyPerformance, strategies, cashFlows, cashFlowSummary, benchmarks, recentActivities } = fundData;

  // Calculate deployment percentage
  const deploymentPercent = (metrics.deployedCapital / fund.fundSize) * 100;

  return (
    <div className="p-4 md:p-6 lg:p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-semibold text-gray-800">{fund.fundName}</h1>
        <p className="text-sm text-gray-500 mt-1">Track and analyze fund performance</p>
      </div>

      {/* Top 6 Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        {/* Fund Size */}
        <div className="bg-white rounded-xl p-5 shadow-sm flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 mb-2">Fund Size</span>
            <span className="text-2xl md:text-3xl font-bold text-gray-800">{formatCurrency(fund.fundSize)}</span>
          </div>
          <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
            <DollarSign size={24} className="text-blue-500" />
          </div>
        </div>

        {/* Deployed */}
        <div className="bg-white rounded-xl p-5 shadow-sm flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 mb-2">Deployed</span>
            <span className="text-2xl md:text-3xl font-bold text-gray-800">{formatCurrency(metrics.deployedCapital)}</span>
            <span className="text-xs font-medium text-green-500">{formatPercent(deploymentPercent)} of commitments</span>
          </div>
          <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
            <TrendingUp size={24} className="text-green-500" />
          </div>
        </div>

        {/* Net IRR */}
        <div className="bg-white rounded-xl p-5 shadow-sm flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 mb-2">Net IRR</span>
            <span className="text-2xl md:text-3xl font-bold text-gray-800">{formatPercent(metrics.netIrr)}</span>
            <span className="text-xs font-medium text-green-500">vs {formatPercent(benchmarks.find(b => b.metricName === 'Net IRR')?.industryBenchmark || 0)} industry</span>
          </div>
          <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center">
            <ArrowUp size={24} className="text-purple-500" />
          </div>
        </div>

        {/* TVPI */}
        <div className="bg-white rounded-xl p-5 shadow-sm flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 mb-2">TVPI</span>
            <span className="text-2xl md:text-3xl font-bold text-gray-800">{formatMultiplier(metrics.tvpi)}</span>
            <span className="text-xs font-medium text-gray-500">{formatCurrency(metrics.totalValue)} distributed</span>
          </div>
          <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center">
            <PieChart size={24} className="text-indigo-500" />
          </div>
        </div>

        {/* DPI */}
        <div className="bg-white rounded-xl p-5 shadow-sm flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 mb-2">DPI</span>
            <span className="text-2xl md:text-3xl font-bold text-gray-800">{formatMultiplier(metrics.dpi)}</span>
            <span className="text-xs font-medium text-green-500">vs {formatMultiplier(benchmarks.find(b => b.metricName === 'DPI')?.industryBenchmark || 0)} industry</span>
          </div>
          <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center">
            <Activity size={24} className="text-orange-500" />
          </div>
        </div>

        {/* Total Value */}
        <div className="bg-white rounded-xl p-5 shadow-sm flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-xs text-gray-500 mb-2">Total Value</span>
            <span className="text-2xl md:text-3xl font-bold text-gray-800">{formatCurrency(metrics.totalValue)}</span>
            <span className="text-xs font-medium text-gray-500">{formatCurrency(fund.fundSize)} committed</span>
          </div>
          <div className="w-12 h-12 bg-teal-50 rounded-xl flex items-center justify-center">
            <DollarSign size={24} className="text-teal-500" />
          </div>
        </div>
      </div>

      {/* Fund Deployment Progress */}
      <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Fund Deployment Progress</h3>
        <div className="space-y-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Capital Deployed: {formatCurrency(metrics.deployedCapital)} / {formatCurrency(fund.fundSize)}</span>
            <span>Remaining Capital: {formatCurrency(metrics.remainingCapital)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-blue-500 h-4 rounded-full transition-all duration-500"
              style={{ width: `${deploymentPercent}%` }}
            />
          </div>
          <p className="text-sm text-gray-500">Investment Period: 2.5 years remaining</p>
        </div>
      </div>

      {/* Two Column Grid: IRR Chart & Strategies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Net IRR Performance Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Net IRR Performance Trends</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={quarterlyPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="quarterLabel" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} label={{ value: 'IRR (%)', angle: -90, position: 'insideLeft', fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="irr" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Investment Strategies */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Investment Strategy Performance</h3>
          <div className="space-y-4">
            {strategies.map((strategy) => {
              const percentOfTotal = (strategy.deployedCapital / metrics.deployedCapital) * 100;
              return (
                <div key={strategy.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="font-semibold text-gray-800">{strategy.strategyName}</h4>
                    <span className="text-sm text-gray-500">{formatPercent(strategy.allocationPercent)} allocation</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Deployed Capital</span>
                      <p className="font-semibold text-gray-800">{formatCurrency(strategy.deployedCapital)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Current Value</span>
                      <p className="font-semibold text-gray-800">{formatCurrency(strategy.currentValue)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">% of Total</span>
                      <p className="font-semibold text-gray-800">{formatPercent(percentOfTotal)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">IRR</span>
                      <p className="font-semibold text-green-600">{formatPercent(strategy.irr)}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Quarterly Cash Flow Analysis */}
      <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quarterly Cash Flow Analysis</h3>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={cashFlows}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="quarterLabel" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} label={{ value: 'Amount ($M)', angle: -90, position: 'insideLeft', fontSize: 12 }} />
            <Tooltip
              formatter={(value: number) => formatCurrency(value)}
            />
            <Legend />
            <Bar dataKey="capitalCalls" fill="#ef4444" name="Capital Calls (Outflows)" />
            <Bar dataKey="distributions" fill="#22c55e" name="Distributions (Inflows)" />
            <Line type="monotone" dataKey="netCashFlow" stroke="#3b82f6" strokeWidth={2} name="Net Cash Flow" dot={{ r: 4 }} />
          </ComposedChart>
        </ResponsiveContainer>

        {/* Summary Metrics */}
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">Total Capital Calls</p>
            <p className="text-xl font-bold text-red-600">{formatCurrency(cashFlowSummary.totalCapitalCalls)}</p>
            <p className="text-xs text-gray-500 mt-1">({formatPercent((cashFlowSummary.totalCapitalCalls / fund.fundSize) * 100)} of fund)</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">Total Distributions</p>
            <p className="text-xl font-bold text-green-600">{formatCurrency(cashFlowSummary.totalDistributions)}</p>
            <p className="text-xs text-gray-500 mt-1">({formatPercent((cashFlowSummary.totalDistributions / metrics.deployedCapital) * 100)} of deployed)</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">Cumulative Net Cash</p>
            <p className="text-xl font-bold text-gray-800">{formatCurrency(cashFlowSummary.cumulativeNetCash)}</p>
            <p className="text-xs text-gray-500 mt-1">(Distributions - Calls)</p>
          </div>
        </div>
      </div>

      {/* Benchmark Comparison Table */}
      <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Benchmark Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Metric</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-600">Fund Performance</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-600">Industry Benchmark</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-600">Outperformance</th>
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((benchmark) => (
                <tr key={benchmark.id} className="border-b border-gray-100">
                  <td className="py-3 px-4 text-sm text-gray-800">{benchmark.metricName}</td>
                  <td className="py-3 px-4 text-sm font-semibold text-right text-gray-800">
                    {benchmark.metricName.includes('IRR') ? formatPercent(benchmark.fundValue) : formatMultiplier(benchmark.fundValue)}
                  </td>
                  <td className="py-3 px-4 text-sm text-right text-gray-600">
                    {benchmark.metricName.includes('IRR') ? formatPercent(benchmark.industryBenchmark) : formatMultiplier(benchmark.industryBenchmark)}
                  </td>
                  <td className={`py-3 px-4 text-sm font-semibold text-right ${benchmark.outperformance > 0 ? 'text-green-600' : benchmark.outperformance < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                    {benchmark.outperformance > 0 ? '+' : ''}{benchmark.metricName.includes('IRR') ? formatPercent(benchmark.outperformance) : formatMultiplier(benchmark.outperformance)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Fund Activity */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Fund Activity</h3>
        <div className="space-y-3">
          {recentActivities.map((activity) => (
            <div key={activity.id} className="flex justify-between items-center py-3 border-b border-gray-100 last:border-b-0">
              <div className="flex-1">
                <p className="font-medium text-gray-800">{activity.description}</p>
                <p className="text-sm text-gray-500 mt-1">{new Date(activity.activityDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
              </div>
              <div className="text-right ml-4">
                <p className="font-semibold text-gray-800">{formatCurrency(activity.amount)}</p>
                <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full mt-1 ${getStatusColor(activity.status)}`}>
                  {activity.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FundReturns;
