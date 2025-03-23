from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.models.schemas import AnalyticsRequest, AnalyticsResponse
from src.data.db_manager import get_db
from src.analytics.visualizer import generate_analytics_report
from src.analytics.revenue import get_revenue_trends, get_revenue_by_hotel_type
from src.analytics.cancellation import get_cancellation_rate, get_cancellation_by_country, get_cancellation_by_month
from src.analytics.geographic import get_geographic_distribution
from src.analytics.lead_time import get_lead_time_distribution, get_lead_time_vs_cancellation

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=AnalyticsResponse)
async def get_analytics(request: AnalyticsRequest, db: Session = Depends(get_db)):

    try:
        if request.report_type == "full":
            report_data = generate_analytics_report(db)
            
            plots = {
                "revenue_trends": report_data["revenue"]["trends"]["plot"],
                "revenue_by_hotel": report_data["revenue"]["by_hotel_type"]["plot"],
                "cancellation_rate": report_data["cancellation"]["overall_rate"]["plot"],
                "cancellation_by_country": report_data["cancellation"]["by_country"]["plot"],
                "cancellation_by_month": report_data["cancellation"]["by_month"]["plot"],
                "geographic_bar": report_data["geography"]["distribution"]["bar_plot"],
                "geographic_pie": report_data["geography"]["distribution"]["pie_plot"],
                "lead_time_histogram": report_data["lead_time"]["distribution"]["histogram"],
                "lead_time_boxplot": report_data["lead_time"]["distribution"]["boxplot"],
                "lead_time_vs_cancellation": report_data["lead_time"]["vs_cancellation"]["plot"]
            }
            
            data = {
                "revenue": {
                    "trends": report_data["revenue"]["trends"]["data"],
                    "by_hotel_type": report_data["revenue"]["by_hotel_type"]["data"]
                },
                "cancellation": {
                    "overall_rate": report_data["cancellation"]["overall_rate"]["data"],
                    "by_country": report_data["cancellation"]["by_country"]["data"],
                    "by_month": report_data["cancellation"]["by_month"]["data"]
                },
                "geography": {
                    "distribution": report_data["geography"]["distribution"]["data"]
                },
                "lead_time": {
                    "distribution": report_data["lead_time"]["distribution"]["stats"],
                    "vs_cancellation": report_data["lead_time"]["vs_cancellation"]["data"]
                }
            }
            
        elif request.report_type == "revenue":
            trends = get_revenue_trends(db, request.period)
            by_hotel = get_revenue_by_hotel_type(db)
            
            data = {
                "trends": trends["data"],
                "by_hotel_type": by_hotel["data"]
            }
            
            plots = {
                "trends": trends["plot"],
                "by_hotel_type": by_hotel["plot"]
            }
            
        elif request.report_type == "cancellation":
            overall = get_cancellation_rate(db)
            by_country = get_cancellation_by_country(db)
            by_month = get_cancellation_by_month(db)
            
            data = {
                "overall_rate": overall["data"],
                "by_country": by_country["data"],
                "by_month": by_month["data"]
            }
            
            plots = {
                "overall_rate": overall["plot"],
                "by_country": by_country["plot"],
                "by_month": by_month["plot"]
            }
            
        elif request.report_type == "geography":
            distribution = get_geographic_distribution(db)
            
            data = {
                "distribution": distribution["data"]
            }
            
            plots = {
                "bar_plot": distribution["bar_plot"],
                "pie_plot": distribution["pie_plot"]
            }
            
        elif request.report_type == "lead_time":
            distribution = get_lead_time_distribution(db)
            vs_cancellation = get_lead_time_vs_cancellation(db)
            
            data = {
                "distribution": distribution["stats"],
                "vs_cancellation": vs_cancellation["data"]
            }
            
            plots = {
                "histogram": distribution["histogram"],
                "boxplot": distribution["boxplot"],
                "vs_cancellation": vs_cancellation["plot"]
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {request.report_type}")
        
        return AnalyticsResponse(
            report_type=request.report_type,
            data=data,
            plots=plots
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))