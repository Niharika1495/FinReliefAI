from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.loan import Loan, LoanStatus
from app.models.user import User
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.services.settlement_service import SettlementService
from app.services.dashboard_service import DashboardService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("finrelief_ai")

scheduler = BackgroundScheduler()

def check_upcoming_emis():
    """
    Scans active loans to alert users of upcoming EMIs due within 3 days.
    """
    logger.info("[Scheduler] Running check_upcoming_emis job...")
    db: Session = SessionLocal()
    try:
        today = datetime.now()
        target_date = today + timedelta(days=3)
        target_day = target_date.day

        # Find active loans
        loans = db.query(Loan).filter(Loan.is_active == True, Loan.loan_status == LoanStatus.ACTIVE).all()
        for loan in loans:
            # Deterministic due day calculation
            due_day = (loan.id % 28) + 1
            if due_day == target_day:
                existing = db.query(Notification).filter(
                    Notification.user_id == loan.user_id,
                    Notification.title == "Upcoming EMI Reminder",
                    Notification.created_at >= (today - timedelta(days=20))
                ).first()
                
                if not existing:
                    NotificationService.create_notification(
                        db=db,
                        user_id=loan.user_id,
                        title="Upcoming EMI Reminder",
                        message=f"Your EMI of ${loan.emi:,.2f} for loan with {loan.lender_name} is due in 3 days (on {target_date.strftime('%B %d, %Y')}).",
                        type="REMINDER"
                    )
    except Exception as e:
        logger.error(f"Error in check_upcoming_emis: {str(e)}", exc_info=True)
    finally:
        db.close()

def check_overdue_payments():
    """
    Scans active loans with overdue months and alerts users.
    """
    logger.info("[Scheduler] Running check_overdue_payments job...")
    db: Session = SessionLocal()
    try:
        loans = db.query(Loan).filter(Loan.is_active == True, Loan.overdue_months > 0).all()
        for loan in loans:
            NotificationService.create_notification(
                db=db,
                user_id=loan.user_id,
                title="Overdue Payment Alert",
                message=f"Your loan with {loan.lender_name} is overdue by {loan.overdue_months} month(s). Outstanding EMI amount is ${loan.emi * loan.overdue_months:,.2f}.",
                type="ALERT"
            )
    except Exception as e:
        logger.error(f"Error in check_overdue_payments: {str(e)}", exc_info=True)
    finally:
        db.close()

def check_settlement_options():
    """
    Scans users to alert them about debt settlement strategies.
    """
    logger.info("[Scheduler] Running check_settlement_options job...")
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            summary = SettlementService.generate_summary(db, user)
            if summary["eligible_loans"] > 0:
                NotificationService.create_notification(
                    db=db,
                    user_id=user.id,
                    title="Settlement Strategy Available",
                    message=f"You have {summary['eligible_loans']} loan(s) eligible for settlement. You could save up to ${summary['total_savings']:,.2f}.",
                    type="REMINDER"
                )
    except Exception as e:
        logger.error(f"Error in check_settlement_options: {str(e)}", exc_info=True)
    finally:
        db.close()

def send_weekly_summaries():
    """
    Sends weekly digest financial summaries to users.
    """
    logger.info("[Scheduler] Running send_weekly_summaries job...")
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            overview = DashboardService.get_overview(db, user)
            NotificationService.create_notification(
                db=db,
                user_id=user.id,
                title="Weekly Financial Summary",
                message=f"Here is your weekly summary. Active Loans: {overview['total_active_loans']}. Outstanding Debt: ${overview['total_outstanding_amount']:,.2f}. Health Score: {overview['financial_health_score']}.",
                type="SUMMARY"
            )
    except Exception as e:
        logger.error(f"Error in send_weekly_summaries: {str(e)}", exc_info=True)
    finally:
        db.close()

def start_scheduler():
    """
    Starts the APScheduler background tasks.
    """
    if not scheduler.running:
        logger.info("Initializing APScheduler background jobs...")
        scheduler.add_job(check_upcoming_emis, 'interval', hours=1, id='check_upcoming_emis')
        scheduler.add_job(check_overdue_payments, 'interval', hours=1, id='check_overdue_payments')
        scheduler.add_job(check_settlement_options, 'interval', hours=12, id='check_settlement_options')
        scheduler.add_job(send_weekly_summaries, 'interval', weeks=1, id='send_weekly_summaries')
        scheduler.start()
        logger.info("APScheduler started successfully.")

def shutdown_scheduler():
    """
    Shuts down the scheduler cleanly.
    """
    if scheduler.running:
        logger.info("Shutting down APScheduler...")
        scheduler.shutdown()
        logger.info("APScheduler shut down successfully.")
