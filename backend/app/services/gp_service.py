"""
GP service layer for General Partner data operations
Handles business logic for GP portfolio management
"""
from typing import List, Optional, Dict
from app.database import (
    db,
    GPModel,
    GPQuarterlyPerformanceModel,
    GPPortfolioSummaryModel
)


class GPService:
    """Service class for managing General Partners"""

    @staticmethod
    def get_gp(gp_id: int) -> Optional[Dict]:
        """
        Get a GP by ID

        Args:
            gp_id: ID of the GP to retrieve

        Returns:
            GP dictionary if found, None otherwise
        """
        gp_model = GPModel.query.get(gp_id)
        if not gp_model:
            return None

        return gp_model.to_dict()

    @staticmethod
    def get_all_gps() -> List[Dict]:
        """
        Get all GPs

        Returns:
            List of GP dictionaries
        """
        gps = GPModel.query.all()
        return [gp.to_dict() for gp in gps]

    @staticmethod
    def get_gp_overview(gp_id: int) -> Optional[Dict]:
        """
        Get complete GP overview with all related data

        Args:
            gp_id: ID of the GP

        Returns:
            Dictionary containing all GP data, or None if GP not found
        """
        # Get GP basic info
        gp = GPService.get_gp(gp_id)
        if not gp:
            return None

        # Get quarterly performance (last 8 quarters)
        quarterly_performance = GPService.get_quarterly_performance(gp_id, limit=8)

        # Get portfolio summary
        portfolio_summary = GPService.get_portfolio_summary(gp_id)

        # Aggregate everything into one response
        return {
            'gp': gp,
            'quarterlyPerformance': quarterly_performance,
            'portfolioSummary': portfolio_summary
        }

    @staticmethod
    def get_quarterly_performance(gp_id: int, limit: int = 8) -> List[Dict]:
        """
        Get GP quarterly performance data

        Args:
            gp_id: ID of the GP
            limit: Number of recent quarters to retrieve

        Returns:
            List of quarterly performance dictionaries
        """
        performances = GPQuarterlyPerformanceModel.query.filter_by(
            gp_id=gp_id
        ).order_by(
            GPQuarterlyPerformanceModel.year.desc(),
            GPQuarterlyPerformanceModel.quarter.desc()
        ).limit(limit).all()

        return [perf.to_dict() for perf in performances]

    @staticmethod
    def get_portfolio_summary(gp_id: int, year: int = None) -> List[Dict]:
        """
        Get GP portfolio summary by quartile

        Args:
            gp_id: ID of the GP
            year: Specific year to filter by (optional, defaults to latest year)

        Returns:
            List of portfolio summary dictionaries
        """
        query = GPPortfolioSummaryModel.query.filter_by(gp_id=gp_id)

        if year:
            query = query.filter_by(year=year)
        else:
            # Get the latest year
            latest = GPPortfolioSummaryModel.query.filter_by(
                gp_id=gp_id
            ).order_by(GPPortfolioSummaryModel.year.desc()).first()
            if latest:
                query = query.filter_by(year=latest.year)

        summaries = query.order_by(GPPortfolioSummaryModel.quartile).all()
        return [summary.to_dict() for summary in summaries]

    @staticmethod
    def get_gp_performance_comparison() -> List[Dict]:
        """
        Get performance comparison data for all GPs
        Returns GP names and their net IRR for comparison chart

        Returns:
            List of dictionaries with GP name and IRR
        """
        gps = GPModel.query.filter(GPModel.net_irr.isnot(None)).all()
        return [
            {
                'gpName': gp.gp_name,
                'netIrr': gp.net_irr,
                'gpId': gp.id
            }
            for gp in gps
        ]

    @staticmethod
    def get_top_performers() -> Dict:
        """
        Get top performing GPs and those needing attention

        Returns:
            Dictionary with top performers and attention items
        """
        # Get top portfolio by IRR
        top_gp = GPModel.query.filter(
            GPModel.net_irr.isnot(None)
        ).order_by(GPModel.net_irr.desc()).first()

        # Get GPs needing attention (negative trend or low IRR)
        attention_gps = GPModel.query.filter(
            db.or_(
                GPModel.irr_trend < 0,
                GPModel.net_irr < 10
            )
        ).all()

        return {
            'topPerformer': {
                'gpName': top_gp.gp_name,
                'netIrr': top_gp.net_irr,
                'performanceRating': top_gp.performance_rating
            } if top_gp else None,
            'needsAttention': [
                {
                    'gpName': gp.gp_name,
                    'netIrr': gp.net_irr,
                    'irrTrend': gp.irr_trend,
                    'reason': 'Negative Trend' if gp.irr_trend < 0 else 'Low Performance'
                }
                for gp in attention_gps
            ]
        }

    @staticmethod
    def create_gp(gp_data: Dict) -> Dict:
        """
        Create a new GP

        Args:
            gp_data: Dictionary containing GP information

        Returns:
            Created GP dictionary
        """
        gp = GPModel.from_dict(gp_data)
        db.session.add(gp)
        db.session.commit()
        return gp.to_dict()

    @staticmethod
    def update_gp(gp_id: int, gp_data: Dict) -> Optional[Dict]:
        """
        Update an existing GP

        Args:
            gp_id: ID of the GP to update
            gp_data: Dictionary containing updated GP information

        Returns:
            Updated GP dictionary if found, None otherwise
        """
        gp = GPModel.query.get(gp_id)
        if not gp:
            return None

        gp.update_from_dict(gp_data)
        db.session.commit()
        return gp.to_dict()

    @staticmethod
    def delete_gp(gp_id: int) -> bool:
        """
        Delete a GP

        Args:
            gp_id: ID of the GP to delete

        Returns:
            True if deleted, False if not found
        """
        gp = GPModel.query.get(gp_id)
        if not gp:
            return False

        db.session.delete(gp)
        db.session.commit()
        return True
