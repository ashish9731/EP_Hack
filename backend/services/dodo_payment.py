"""
Dodo Payments Integration Service
"""
import os
from dodopayments import Dodo
from typing import Optional

# Initialize Dodo client
# Get API key from environment
DODO_API_KEY = os.getenv('DODO_API_KEY', '')

if DODO_API_KEY:
    dodo_client = Dodo(api_key=DODO_API_KEY)
else:
    dodo_client = None
    print("Warning: DODO_API_KEY not set. Payments will not work.")

PRICING_CONFIG = {
    "basic_monthly": {
        "amount": 2500,  # $25 in cents
        "currency": "USD",
        "interval": "monthly"
    },
    "basic_yearly": {
        "amount": 27500,  # $275 in cents
        "currency": "USD",
        "interval": "yearly"
    },
    "pro_monthly": {
        "amount": 8000,  # $80 in cents
        "currency": "USD",
        "interval": "monthly"
    },
    "pro_yearly": {
        "amount": 85000,  # $850 in cents
        "currency": "USD",
        "interval": "yearly"
    }
}


async def create_payment_session(tier: str, billing_cycle: str, user_email: str, user_id: str) -> Optional[dict]:
    """
    Create a Dodo payment session
    """
    if not dodo_client:
        return {"error": "Payment system not configured"}
    
    pricing_key = f"{tier}_{billing_cycle}"
    if pricing_key not in PRICING_CONFIG:
        return {"error": "Invalid pricing tier"}
    
    pricing = PRICING_CONFIG[pricing_key]
    
    try:
        # Create payment session with Dodo
        session = dodo_client.payments.create(
            amount=pricing["amount"],
            currency=pricing["currency"],
            customer_email=user_email,
            metadata={
                "user_id": user_id,
                "tier": tier,
                "billing_cycle": billing_cycle
            },
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?payment=success",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/pricing?payment=cancelled"
        )
        
        return {
            "checkout_url": session.checkout_url,
            "session_id": session.id
        }
    except Exception as e:
        print(f"Error creating payment session: {str(e)}")
        return {"error": str(e)}


async def verify_payment(session_id: str) -> dict:
    """
    Verify a payment session
    """
    if not dodo_client:
        return {"verified": False, "error": "Payment system not configured"}
    
    try:
        session = dodo_client.payments.retrieve(session_id)
        
        return {
            "verified": session.status == "paid",
            "metadata": session.metadata
        }
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return {"verified": False, "error": str(e)}
