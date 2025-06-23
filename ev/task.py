from celery import shared_task
from django.utils import timezone
from decimal import Decimal
from .models import ChargingSession, UserProfile
import time

@shared_task
def handle_charging_session(session_id):
    try:
        session = ChargingSession.objects.get(id=session_id)
        charging_rate = Decimal('7.2')  # 7.2kW charging rate
        cost_per_kwh = Decimal('0.15')  # $0.15 per kWh
        
        while True:
            # Check if session should be stopped
            session.refresh_from_db()
            if session.status != 'in_progress':
                break
                
            # Calculate current duration and costs
            current_duration = (timezone.now() - session.start_time)
            hours = current_duration.total_seconds() / 3600
            energy_consumed = Decimal(str(hours * charging_rate))
            current_cost = energy_consumed * cost_per_kwh
            
            # Update session
            session.energy_consumed = energy_consumed
            session.cost = current_cost
            session.save()
            
            # Check user balance
            if session.user.profile.account_balance < current_cost:
                stop_charging_session.delay(session_id)
                break
                
            time.sleep(60)  # Update every minute
            
    except ChargingSession.DoesNotExist:
        return False

@shared_task
def stop_charging_session(session_id):
    try:
        session = ChargingSession.objects.get(id=session_id)
        session.end_time = timezone.now()
        session.status = 'completed'
        session.save()
        
        # Update station availability
        session.station.is_available = True
        session.station.save()
        
        # Update user profile
        profile = session.user.profile
        profile.account_balance -= session.cost
        profile.total_sessions += 1
        profile.total_energy_consumed += session.energy_consumed
        profile.total_amount_spent += session.cost
        profile.save()
        
        return True
    except ChargingSession.DoesNotExist:
        return False