"""
Deal service layer for CRUD operations
Handles business logic for deal management
"""
from typing import List, Optional
from app.database import db, DealModel
from app.models.deal_models import Deal


class DealService:
    """Service class for managing real estate deals"""

    @staticmethod
    def create_deal(deal_data: dict) -> Deal:
        """
        Create a new deal

        Args:
            deal_data: Dictionary containing deal information

        Returns:
            Created Deal object

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if not deal_data.get('dealName'):
            raise ValueError('Deal name is required')
        if not deal_data.get('location'):
            raise ValueError('Location is required')

        # Create DealModel from dictionary
        deal_model = DealModel.from_dict(deal_data)

        # Save to database
        db.session.add(deal_model)
        db.session.commit()

        # Convert to Deal dataclass and return
        return Deal.from_dict(deal_model.to_dict())

    @staticmethod
    def get_deal(deal_id: int) -> Optional[Deal]:
        """
        Get a deal by ID

        Args:
            deal_id: ID of the deal to retrieve

        Returns:
            Deal object if found, None otherwise
        """
        deal_model = DealModel.query.get(deal_id)
        if not deal_model:
            return None

        return Deal.from_dict(deal_model.to_dict())

    @staticmethod
    def get_all_deals(status: Optional[str] = None, limit: int = 100) -> List[Deal]:
        """
        Get all deals, optionally filtered by status

        Args:
            status: Optional status filter ('potential', 'ongoing', 'completed', 'rejected')
            limit: Maximum number of deals to return (default 100)

        Returns:
            List of Deal objects
        """
        query = DealModel.query

        # Apply status filter if provided
        if status:
            query = query.filter(DealModel.status == status)

        # Order by updated_at descending (most recent first)
        query = query.order_by(DealModel.updated_at.desc())

        # Limit results
        query = query.limit(limit)

        # Execute query and convert to Deal objects
        deal_models = query.all()
        return [Deal.from_dict(dm.to_dict()) for dm in deal_models]

    @staticmethod
    def update_deal(deal_id: int, deal_data: dict) -> Optional[Deal]:
        """
        Update an existing deal

        Args:
            deal_id: ID of the deal to update
            deal_data: Dictionary containing updated deal information

        Returns:
            Updated Deal object if found, None otherwise
        """
        deal_model = DealModel.query.get(deal_id)
        if not deal_model:
            return None

        # Update fields from dictionary
        deal_model.update_from_dict(deal_data)

        # Commit changes
        db.session.commit()

        # Return updated Deal
        return Deal.from_dict(deal_model.to_dict())

    @staticmethod
    def delete_deal(deal_id: int) -> bool:
        """
        Delete a deal

        Args:
            deal_id: ID of the deal to delete

        Returns:
            True if deleted, False if not found
        """
        deal_model = DealModel.query.get(deal_id)
        if not deal_model:
            return False

        db.session.delete(deal_model)
        db.session.commit()
        return True

    @staticmethod
    def get_deals_by_status_grouped() -> dict:
        """
        Get deals grouped by status

        Returns:
            Dictionary with status as keys and lists of deals as values
        """
        deals = DealService.get_all_deals()

        grouped = {
            'potential': [],
            'ongoing': [],
            'completed': [],
            'rejected': []
        }

        for deal in deals:
            status = deal.status or 'potential'
            if status in grouped:
                grouped[status].append(deal)
            else:
                grouped['potential'].append(deal)

        return grouped

    @staticmethod
    def get_deal_model(deal_id: int) -> Optional[DealModel]:
        """
        Get the SQLAlchemy DealModel directly (for Excel export service)

        Args:
            deal_id: ID of the deal

        Returns:
            DealModel if found, None otherwise
        """
        return DealModel.query.get(deal_id)
