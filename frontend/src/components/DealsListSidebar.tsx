import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, Trash2, Calendar } from 'lucide-react';
import type { Deal, DealStatus } from '../types/deal';
import { DEAL_STATUS_LABELS, DEAL_STATUS_COLORS } from '../types/deal';
import { dealApi } from '../services/dealApi';

interface DealsListSidebarProps {
  onSelectDeal: (deal: Deal) => void;
  activeDealId?: number;
  onDealsUpdate?: () => void;
}

const DealsListSidebar = ({ onSelectDeal, activeDealId, onDealsUpdate }: DealsListSidebarProps) => {
  const [deals, setDeals] = useState<Record<DealStatus, Deal[]>>({
    potential: [],
    ongoing: [],
    completed: [],
    rejected: []
  });
  const [expandedSections, setExpandedSections] = useState<Record<DealStatus, boolean>>({
    potential: true,
    ongoing: true,
    completed: false,
    rejected: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch all deals grouped by status
   */
  const fetchDeals = async () => {
    setLoading(true);
    setError(null);

    try {
      const grouped = await dealApi.getDealsGrouped();
      setDeals(grouped);
    } catch (err) {
      console.error('Error fetching deals:', err);
      setError('Failed to load deals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeals();
  }, []);

  /**
   * Toggle section expansion
   */
  const toggleSection = (status: DealStatus) => {
    setExpandedSections(prev => ({
      ...prev,
      [status]: !prev[status]
    }));
  };

  /**
   * Handle deal selection
   */
  const handleSelectDeal = (deal: Deal) => {
    onSelectDeal(deal);
  };

  /**
   * Handle deal deletion
   */
  const handleDeleteDeal = async (dealId: number, e: React.MouseEvent) => {
    e.stopPropagation();

    if (!confirm('Are you sure you want to delete this deal?')) {
      return;
    }

    try {
      await dealApi.deleteDeal(dealId);
      await fetchDeals();

      if (onDealsUpdate) {
        onDealsUpdate();
      }
    } catch (err) {
      console.error('Error deleting deal:', err);
      alert('Failed to delete deal. Please try again.');
    }
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  /**
   * Calculate total deals count
   */
  const totalDeals = Object.values(deals).reduce((sum, dealList) => sum + dealList.length, 0);

  if (loading) {
    return (
      <div className="p-6 bg-white shadow-sm rounded-xl">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Saved Deals</h3>
        <div className="flex items-center justify-center py-8">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-white shadow-sm rounded-xl">
        <h3 className="mb-4 text-lg font-semibold text-gray-800">Saved Deals</h3>
        <div className="p-4 text-sm text-red-800 bg-red-100 border border-red-200 rounded-lg">
          {error}
        </div>
        <button
          onClick={fetchDeals}
          className="w-full px-4 py-2 mt-3 text-sm font-medium text-blue-600 transition-colors bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="overflow-hidden bg-white shadow-sm rounded-xl">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800">Saved Deals</h3>
          <span className="px-2 py-1 text-xs font-medium text-blue-600 rounded-full bg-blue-50">
            {totalDeals}
          </span>
        </div>
      </div>

      {/* Deals List */}
      <div className="max-h-[600px] overflow-y-auto">
        {totalDeals === 0 ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-500">
              No saved deals yet. Create a deal from the map to get started.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {(Object.keys(deals) as DealStatus[]).map(status => {
              const statusDeals = deals[status];
              const isExpanded = expandedSections[status];
              const colors = DEAL_STATUS_COLORS[status];

              if (statusDeals.length === 0) return null;

              return (
                <div key={status} className="p-3">
                  {/* Section Header */}
                  <button
                    onClick={() => toggleSection(status)}
                    className="flex items-center justify-between w-full p-2 transition-colors rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-2">
                      {isExpanded ? (
                        <ChevronDown size={16} className="text-gray-600" />
                      ) : (
                        <ChevronRight size={16} className="text-gray-600" />
                      )}
                      <span className={`px-2 py-1 text-xs font-medium rounded-full border ${colors.bg} ${colors.text} ${colors.border}`}>
                        {DEAL_STATUS_LABELS[status]}
                      </span>
                      <span className="text-sm text-gray-600">({statusDeals.length})</span>
                    </div>
                  </button>

                  {/* Deals in Section */}
                  {isExpanded && (
                    <div className="mt-2 space-y-2">
                      {statusDeals.map(deal => {
                        const isActive = deal.id === activeDealId;

                        return (
                          <div
                            key={deal.id}
                            onClick={() => handleSelectDeal(deal)}
                            className={`p-3 rounded-lg cursor-pointer transition-all border ${
                              isActive
                                ? 'bg-blue-50 border-blue-300 ring-2 ring-blue-200'
                                : 'bg-gray-50 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <h4 className={`text-sm font-semibold truncate ${
                                  isActive ? 'text-blue-900' : 'text-gray-800'
                                }`}>
                                  {deal.dealName}
                                </h4>
                                <p className="mt-1 text-xs text-gray-600 truncate">
                                  {deal.location}
                                </p>
                                {deal.propertyAddress && (
                                  <p className="mt-0.5 text-xs text-gray-500 truncate">
                                    {deal.propertyAddress}
                                  </p>
                                )}
                                <div className="flex items-center gap-1 mt-2">
                                  <Calendar size={12} className="text-gray-400" />
                                  <span className="text-xs text-gray-500">
                                    {formatDate(deal.updatedAt)}
                                  </span>
                                </div>
                              </div>

                              {/* Delete Button */}
                              <button
                                onClick={(e) => handleDeleteDeal(deal.id!, e)}
                                className="p-1 text-gray-400 transition-colors rounded hover:text-red-600 hover:bg-red-50"
                                aria-label="Delete deal"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>

                            {/* Financial Preview */}
                            {deal.monthlyCashFlow !== undefined && deal.monthlyCashFlow !== null && (
                              <div className="flex items-center justify-between pt-2 mt-2 border-t border-gray-200">
                                <span className="text-xs text-gray-600">Cash Flow:</span>
                                <span className={`text-xs font-semibold ${
                                  deal.monthlyCashFlow > 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  ${deal.monthlyCashFlow.toFixed(0)}/mo
                                </span>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Refresh Button */}
      {totalDeals > 0 && (
        <div className="p-3 border-t border-gray-200">
          <button
            onClick={fetchDeals}
            className="w-full px-4 py-2 text-sm font-medium text-gray-700 transition-colors bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Refresh Deals
          </button>
        </div>
      )}
    </div>
  );
};

export default DealsListSidebar;
