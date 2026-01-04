import { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle, Clock, FileText } from 'lucide-react';
import type { Market, Regulation, RegulatoryChange, RegulationStatus } from '../types/regulation';

// Mock data - replace with API calls later
const mockMarkets: Market[] = [
  { id: '1', name: 'Austin, TX', state: 'TX', riskScore: 7.5 },
  { id: '2', name: 'Phoenix, AZ', state: 'AZ', riskScore: 6.8 },
];

const mockRegulations: Regulation[] = [
  {
    id: '1',
    title: 'Affordable Housing Density Bonus',
    description: 'Incentive allowing increased building density for projects with 30%+ affordable units',
    status: 'compliant',
    effectiveDate: '2022-01-01',
  },
  {
    id: '2',
    title: 'Inclusionary Zoning Updates Requirements',
    description: 'New developments >50 units must include 15% affordable housing',
    status: 'needed',
    effectiveDate: '2025-01-31',
    sunset: '2030-12-31',
  },
  {
    id: '3',
    title: 'Construction Impact Fees',
    description: 'Additional fees for projects impacting infrastructure',
    status: 'negotiation',
    effectiveDate: '2023-06-01',
  },
];

const mockUpcomingChanges: RegulatoryChange[] = [
  {
    id: '1',
    title: 'Rent Control Amendment - SB 91',
    description: '5% annual cap on rent increases for properties near public transportation',
    status: 'proposed',
    proposedDate: '2024-11-15',
  },
  {
    id: '2',
    title: 'State Legislative Session - Oct 2024',
    description: 'Potential changes to tax credit programs',
    status: 'proposed',
    proposedDate: '2024-10-01',
  },
  {
    id: '3',
    title: 'Transit Oriented Update - Nov 2024',
    description: 'Increased density allowances near transit',
    status: 'enacted',
    enactedDate: '2024-11-20',
    effectiveDate: '2025-01-01',
  },
];

const getStatusColor = (status: RegulationStatus): { bg: string; text: string; border: string } => {
  switch (status) {
    case 'compliant':
    case 'active':
      return { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' };
    case 'concerning':
      return { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' };
    case 'negotiation':
      return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' };
    case 'proposed':
      return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' };
    case 'needed':
      return { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' };
    default:
      return { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200' };
  }
};

const getStatusLabel = (status: RegulationStatus): string => {
  switch (status) {
    case 'compliant':
      return 'Compliant';
    case 'concerning':
      return 'Concerning';
    case 'negotiation':
      return 'Negotiation';
    case 'active':
      return 'Active';
    case 'proposed':
      return 'Proposed';
    case 'needed':
      return 'Needed';
    default:
      return status;
  }
};

const Regulations = () => {
  const [selectedMarket, setSelectedMarket] = useState<Market>(mockMarkets[0]);
  const [expandedRegulations, setExpandedRegulations] = useState<Set<string>>(new Set());
  const [expandedChanges, setExpandedChanges] = useState<Set<string>>(new Set());

  const toggleRegulation = (id: string) => {
    const newExpanded = new Set(expandedRegulations);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRegulations(newExpanded);
  };

  const toggleChange = (id: string) => {
    const newExpanded = new Set(expandedChanges);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedChanges(newExpanded);
  };

  const compliantCount = mockRegulations.filter(r => r.status === 'compliant').length;
  const concerningCount = mockRegulations.filter(r => r.status === 'concerning' || r.status === 'negotiation').length;
  const proposedChangesCount = mockUpcomingChanges.filter(c => c.status === 'proposed').length;

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Markets Sidebar */}
      <div className="w-48 bg-white border-r border-gray-200 p-4">
        <h3 className="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wide">Markets</h3>
        <div className="space-y-1">
          {mockMarkets.map((market) => (
            <div
              key={market.id}
              onClick={() => setSelectedMarket(market)}
              className={`p-2.5 rounded-lg cursor-pointer transition-colors ${
                selectedMarket.id === market.id
                  ? 'bg-blue-50 border border-blue-200'
                  : 'hover:bg-gray-50'
              }`}
            >
              <div className="text-sm font-medium text-gray-800">{market.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">Risk Score: {market.riskScore}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-4 md:p-6 lg:p-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-semibold text-gray-800">Regulatory Monitor</h1>
          <p className="text-sm text-gray-500 mt-1">Track local regulations affecting affordable housing development</p>
        </div>

        {/* Location Selector */}
        <div className="mb-6 flex items-center justify-between bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
              <span className="text-sm font-medium text-gray-800">{selectedMarket.name}</span>
              <ChevronDown size={16} className="text-gray-500" />
            </div>
            <span className="text-xs text-gray-500">Last checked: 2025-01-22</span>
          </div>
          <div className="text-sm text-gray-600">
            <span className="font-medium">P-REIT Risk Score</span>
            <span className="ml-2 px-2.5 py-1 bg-orange-50 text-orange-700 border border-orange-200 rounded-full font-semibold">
              {selectedMarket.riskScore.toFixed(1)}
            </span>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-5 border border-green-200">
            <div className="flex items-start justify-between mb-2">
              <span className="text-sm font-medium text-green-700">Compliant Regulations</span>
              <CheckCircle size={20} className="text-green-600" />
            </div>
            <div className="text-3xl font-bold text-green-800">{compliantCount}</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl p-5 border border-yellow-200">
            <div className="flex items-start justify-between mb-2">
              <span className="text-sm font-medium text-yellow-700">Concerning Regulations</span>
              <AlertCircle size={20} className="text-yellow-600" />
            </div>
            <div className="text-3xl font-bold text-yellow-800">{concerningCount}</div>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-5 border border-orange-200">
            <div className="flex items-start justify-between mb-2">
              <span className="text-sm font-medium text-orange-700">Proposed Changes</span>
              <Clock size={20} className="text-orange-600" />
            </div>
            <div className="text-3xl font-bold text-orange-800">{proposedChangesCount}</div>
          </div>
        </div>

        {/* Current Regulations */}
        <div className="bg-white rounded-xl shadow-sm mb-6">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">Current Regulations</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {mockRegulations.map((regulation) => {
              const isExpanded = expandedRegulations.has(regulation.id);
              const colors = getStatusColor(regulation.status);

              return (
                <div key={regulation.id} className="p-5 hover:bg-gray-50 transition-colors">
                  <div
                    className="flex items-start justify-between cursor-pointer"
                    onClick={() => toggleRegulation(regulation.id)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <FileText size={18} className="text-gray-400 flex-shrink-0" />
                        <h3 className="font-medium text-gray-800">{regulation.title}</h3>
                      </div>
                      {isExpanded && (
                        <div className="ml-9 mt-3 space-y-2">
                          <p className="text-sm text-gray-600">{regulation.description}</p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>Effective: {regulation.effectiveDate}</span>
                            {regulation.sunset && <span>Sunset: {regulation.sunset}</span>}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-3 ml-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border}`}>
                        {getStatusLabel(regulation.status)}
                      </span>
                      {isExpanded ? (
                        <ChevronUp size={20} className="text-gray-400" />
                      ) : (
                        <ChevronDown size={20} className="text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Upcoming Regulatory Changes */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">Upcoming Regulatory Changes</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {mockUpcomingChanges.map((change) => {
              const isExpanded = expandedChanges.has(change.id);
              const colors = change.status === 'proposed'
                ? { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' }
                : { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' };

              return (
                <div key={change.id} className="p-5 hover:bg-gray-50 transition-colors">
                  <div
                    className="flex items-start justify-between cursor-pointer"
                    onClick={() => toggleChange(change.id)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Clock size={18} className="text-gray-400 flex-shrink-0" />
                        <h3 className="font-medium text-gray-800">{change.title}</h3>
                      </div>
                      {isExpanded && (
                        <div className="ml-9 mt-3 space-y-2">
                          <p className="text-sm text-gray-600">{change.description}</p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            {change.proposedDate && <span>Proposed: {change.proposedDate}</span>}
                            {change.enactedDate && <span>Enacted: {change.enactedDate}</span>}
                            {change.effectiveDate && <span>Effective: {change.effectiveDate}</span>}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-3 ml-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border capitalize ${colors.bg} ${colors.text} ${colors.border}`}>
                        {change.status}
                      </span>
                      {isExpanded ? (
                        <ChevronUp size={20} className="text-gray-400" />
                      ) : (
                        <ChevronDown size={20} className="text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Regulations;
