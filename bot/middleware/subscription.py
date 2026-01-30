"""
Subscription middleware for access control.
Validates user subscription before allowing access to paid features.
"""
import logging
from functools import wraps
from datetime import datetime, timezone, timedelta
from typing import Callable, Optional

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.database import db

logger = logging.getLogger(__name__)

# Commands that don't require subscription
EXEMPT_COMMANDS = ['/start', '/help', '/cancel']


async def check_subscription(user_id: int) -> tuple[bool, Optional[datetime], str]:
    """
    Check user's subscription status.
    
    Returns:
        (is_active, expiry_date, status_message)
    """
    is_active, expiry_date = await db.check_subscription(user_id)
    
    if not expiry_date:
        return False, None, "no_subscription"
    
    if not is_active:
        return False, expiry_date, "expired"
    
    # Check if expiring soon (within 7 days)
    days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days
    
    if days_until_expiry <= 3:
        return True, expiry_date, "expiring_soon_3"
    elif days_until_expiry <= 7:
        return True, expiry_date, "expiring_soon_7"
    
    return True, expiry_date, "active"


def require_subscription(func: Callable):
    """
    Decorator to require active subscription for handler.
    
    Usage:
        @require_subscription
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Handler code here
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        
        if not user:
            return
        
        user_id = user.id
        
        # Check subscription
        is_active, expiry_date, status = await check_subscription(user_id)
        
        if status == "no_subscription":
            await update.message.reply_text(
                "You don't have an active subscription.\n\n"
                "Please contact the administrator to activate your account.\n"
                "Telegram: @EthioGermanSchool\n\n"
                "Sie haben kein aktives Abonnement.\n"
                "Bitte kontaktieren Sie den Administrator.",
                parse_mode='HTML'
            )
            return
        
        if status == "expired":
            expiry_str = expiry_date.strftime('%d %B %Y') if expiry_date else 'Unknown'
            await update.message.reply_text(
                f"Your subscription expired on {expiry_str}.\n\n"
                "Please renew your subscription to continue learning.\n"
                "Contact: @EthioGermanSchool\n\n"
                f"Ihr Abonnement ist am {expiry_str} abgelaufen.\n"
                "Bitte erneuern Sie Ihr Abonnement.",
                parse_mode='HTML'
            )
            return
        
        # Store subscription warning in context for handlers to use
        context.user_data['subscription_status'] = status
        context.user_data['subscription_expiry'] = expiry_date
        
        # Update last active
        await db.update_last_active(user_id)
        
        # Call the actual handler
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def require_subscription_callback(func: Callable):
    """
    Decorator for callback query handlers that require subscription.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        query = update.callback_query
        user = update.effective_user
        
        if not user:
            return
        
        user_id = user.id
        
        # Check subscription
        is_active, expiry_date, status = await check_subscription(user_id)
        
        if status in ["no_subscription", "expired"]:
            await query.answer(
                "Subscription required. Please contact @EthioGermanSchool",
                show_alert=True
            )
            return
        
        # Store subscription info
        context.user_data['subscription_status'] = status
        context.user_data['subscription_expiry'] = expiry_date
        
        # Update last active
        await db.update_last_active(user_id)
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def get_subscription_warning(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get subscription warning message if expiring soon.
    Returns empty string if not expiring soon.
    """
    status = context.user_data.get('subscription_status', '')
    expiry = context.user_data.get('subscription_expiry')
    
    if status == 'expiring_soon_3' and expiry:
        days = (expiry - datetime.now(timezone.utc)).days
        return f"\nYour subscription expires in {days} days. Please renew soon."
    elif status == 'expiring_soon_7' and expiry:
        days = (expiry - datetime.now(timezone.utc)).days
        return f"\nReminder: Subscription expires in {days} days."
    
    return ""
