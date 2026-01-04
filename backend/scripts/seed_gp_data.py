"""
Script to seed the database with sample GP (General Partner) data
Run this from the backend directory: python -m scripts.seed_gp_data
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db, GPModel, GPQuarterlyPerformanceModel, GPPortfolioSummaryModel
import json

def seed_gp_data():
    """Seed the database with sample GP data"""
    app = create_app()

    with app.app_context():
        print("Starting GP data seeding...")

        # Clear existing GP data
        print("Clearing existing GP data...")
        GPPortfolioSummaryModel.query.delete()
        GPQuarterlyPerformanceModel.query.delete()
        GPModel.query.delete()
        db.session.commit()

        # Sample GP 1: Community Impact Builders
        print("Creating GP: Community Impact Builders...")
        gp1 = GPModel(
            gp_name="Community Impact Builders",
            location="Richmond, VA",
            tier="Standard",
            performance_rating="Outstanding",
            contact_email="info@communityimpact.com",
            contact_phone="(555) 123-4567",
            website="www.communityimpact.com",
            net_irr=16.24,
            gross_irr=18.5,
            irr_trend=1.8,
            total_aum=45000000,
            deal_count=12,
            current_value=52000000,
            tags=json.dumps(["IRR Performance", "Opportunity Zones", "Green Building"])
        )
        db.session.add(gp1)
        db.session.flush()

        # Quarterly performance for GP1
        gp1_quarters = [
            {"year": 2024, "quarter": 1, "irr": 14.2},
            {"year": 2024, "quarter": 2, "irr": 15.1},
            {"year": 2024, "quarter": 3, "irr": 15.8},
            {"year": 2024, "quarter": 4, "irr": 16.24},
            {"year": 2023, "quarter": 3, "irr": 13.5},
            {"year": 2023, "quarter": 4, "irr": 14.0},
        ]
        for q in gp1_quarters:
            qp = GPQuarterlyPerformanceModel(
                gp_id=gp1.id,
                year=q["year"],
                quarter=q["quarter"],
                irr=q["irr"]
            )
            db.session.add(qp)

        # Portfolio summary for GP1
        gp1_summary = [
            {"year": 2024, "quartile": 1, "deal_count": 3, "percentage": 25.0},
            {"year": 2023, "quartile": 2, "deal_count": 5, "percentage": 41.67},
            {"year": 2022, "quartile": 3, "deal_count": 3, "percentage": 25.0},
            {"year": 2021, "quartile": 4, "deal_count": 1, "percentage": 8.33},
        ]
        for s in gp1_summary:
            ps = GPPortfolioSummaryModel(
                gp_id=gp1.id,
                year=s["year"],
                quartile=s["quartile"],
                deal_count=s["deal_count"],
                percentage=s["percentage"]
            )
            db.session.add(ps)

        # Sample GP 2: Austin Housing Partners
        print("Creating GP: Austin Housing Partners...")
        gp2 = GPModel(
            gp_name="Austin Housing Partners",
            location="Austin, TX",
            tier="Premium",
            performance_rating="Excellent",
            contact_email="contact@austinhousing.com",
            contact_phone="(512) 555-7890",
            website="www.austinhousing.com",
            net_irr=14.73,
            gross_irr=16.8,
            irr_trend=0.9,
            total_aum=68000000,
            deal_count=18,
            current_value=75000000,
            tags=json.dumps(["IRR Performance", "Multifamily", "LIHTC"])
        )
        db.session.add(gp2)
        db.session.flush()

        # Quarterly performance for GP2
        gp2_quarters = [
            {"year": 2024, "quarter": 1, "irr": 13.5},
            {"year": 2024, "quarter": 2, "irr": 14.1},
            {"year": 2024, "quarter": 3, "irr": 14.5},
            {"year": 2024, "quarter": 4, "irr": 14.73},
            {"year": 2023, "quarter": 3, "irr": 12.8},
            {"year": 2023, "quarter": 4, "irr": 13.2},
        ]
        for q in gp2_quarters:
            qp = GPQuarterlyPerformanceModel(
                gp_id=gp2.id,
                year=q["year"],
                quarter=q["quarter"],
                irr=q["irr"]
            )
            db.session.add(qp)

        # Portfolio summary for GP2
        gp2_summary = [
            {"year": 2024, "quartile": 1, "deal_count": 4, "percentage": 22.22},
            {"year": 2023, "quartile": 2, "deal_count": 7, "percentage": 38.89},
            {"year": 2022, "quartile": 3, "deal_count": 5, "percentage": 27.78},
            {"year": 2021, "quartile": 4, "deal_count": 2, "percentage": 11.11},
        ]
        for s in gp2_summary:
            ps = GPPortfolioSummaryModel(
                gp_id=gp2.id,
                year=s["year"],
                quartile=s["quartile"],
                deal_count=s["deal_count"],
                percentage=s["percentage"]
            )
            db.session.add(ps)

        # Sample GP 3: Metro Development Group
        print("Creating GP: Metro Development Group...")
        gp3 = GPModel(
            gp_name="Metro Development Group",
            location="Seattle, WA",
            tier="Standard",
            performance_rating="Excellent",
            contact_email="info@metrodev.com",
            contact_phone="(206) 555-3456",
            net_irr=18.5,
            gross_irr=20.2,
            irr_trend=2.5,
            total_aum=92000000,
            deal_count=25,
            current_value=105000000,
            tags=json.dumps(["IRR Performance", "Urban Development"])
        )
        db.session.add(gp3)
        db.session.flush()

        # Quarterly performance for GP3
        gp3_quarters = [
            {"year": 2024, "quarter": 1, "irr": 16.5},
            {"year": 2024, "quarter": 2, "irr": 17.2},
            {"year": 2024, "quarter": 3, "irr": 17.9},
            {"year": 2024, "quarter": 4, "irr": 18.5},
        ]
        for q in gp3_quarters:
            qp = GPQuarterlyPerformanceModel(
                gp_id=gp3.id,
                year=q["year"],
                quarter=q["quarter"],
                irr=q["irr"]
            )
            db.session.add(qp)

        # Sample GP 4: Coastal Realty Fund
        print("Creating GP: Coastal Realty Fund...")
        gp4 = GPModel(
            gp_name="Coastal Realty Fund",
            location="Miami, FL",
            tier="Premium",
            performance_rating="Good",
            contact_email="contact@coastalrealty.com",
            contact_phone="(305) 555-9012",
            net_irr=12.8,
            gross_irr=14.5,
            irr_trend=-0.5,
            total_aum=55000000,
            deal_count=15,
            current_value=58000000,
            tags=json.dumps(["Value-Add", "Multifamily"])
        )
        db.session.add(gp4)
        db.session.flush()

        # Quarterly performance for GP4
        gp4_quarters = [
            {"year": 2024, "quarter": 1, "irr": 13.5},
            {"year": 2024, "quarter": 2, "irr": 13.2},
            {"year": 2024, "quarter": 3, "irr": 13.0},
            {"year": 2024, "quarter": 4, "irr": 12.8},
        ]
        for q in gp4_quarters:
            qp = GPQuarterlyPerformanceModel(
                gp_id=gp4.id,
                year=q["year"],
                quarter=q["quarter"],
                irr=q["irr"]
            )
            db.session.add(qp)

        # Sample GP 5: Northeast Equity Partners
        print("Creating GP: Northeast Equity Partners...")
        gp5 = GPModel(
            gp_name="Northeast Equity Partners",
            location="Boston, MA",
            tier="Standard",
            performance_rating="Outstanding",
            contact_email="info@neequity.com",
            contact_phone="(617) 555-6789",
            net_irr=15.9,
            gross_irr=17.3,
            irr_trend=1.2,
            total_aum=78000000,
            deal_count=20,
            current_value=88000000,
            tags=json.dumps(["Core-Plus", "Mixed-Use"])
        )
        db.session.add(gp5)
        db.session.flush()

        # Quarterly performance for GP5
        gp5_quarters = [
            {"year": 2024, "quarter": 1, "irr": 14.8},
            {"year": 2024, "quarter": 2, "irr": 15.2},
            {"year": 2024, "quarter": 3, "irr": 15.6},
            {"year": 2024, "quarter": 4, "irr": 15.9},
        ]
        for q in gp5_quarters:
            qp = GPQuarterlyPerformanceModel(
                gp_id=gp5.id,
                year=q["year"],
                quarter=q["quarter"],
                irr=q["irr"]
            )
            db.session.add(qp)

        # Commit all changes
        db.session.commit()
        print("✓ Successfully seeded GP data!")
        print(f"  - Created {GPModel.query.count()} GPs")
        print(f"  - Created {GPQuarterlyPerformanceModel.query.count()} quarterly performance records")
        print(f"  - Created {GPPortfolioSummaryModel.query.count()} portfolio summary records")


if __name__ == "__main__":
    seed_gp_data()
