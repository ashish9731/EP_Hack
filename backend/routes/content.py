"""
Content routes for simulator, learning bytes, and training modules
"""
from fastapi import APIRouter, HTTPException, Header, Cookie
from typing import Optional
from services.timed_content import get_current_simulator_scenarios, get_current_training_modules, get_current_daily_tip

router = APIRouter(prefix="/api")

def get_content_routes():
    from utils.supabase_auth import get_current_user
    
    @router.get("/simulator/scenarios")
    async def get_simulator_scenarios(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        # Authenticate user
        user = await get_current_user(session_token, authorization)
        
        try:
            # Get current simulator scenarios
            scenarios_data = get_current_simulator_scenarios()
            return scenarios_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get simulator scenarios: {str(e)}")
    
    @router.get("/training/modules")
    async def get_training_modules(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        # Authenticate user
        user = await get_current_user(session_token, authorization)
        
        try:
            # Get current training modules
            modules_data = get_current_training_modules()
            return modules_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get training modules: {str(e)}")
    
    @router.get("/learning/daily-tip")
    async def get_daily_tip(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        # Authenticate user
        user = await get_current_user(session_token, authorization)
        
        try:
            # Get current daily tip
            tip_data = get_current_daily_tip()
            return tip_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get daily tip: {str(e)}")
    
    @router.get("/learning/ted-talks")
    async def get_ted_talks(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        # Authenticate user
        user = await get_current_user(session_token, authorization)
        
        try:
            # Return predefined TED talks
            ted_talks = [
                {
                    "id": "1",
                    "title": "How great leaders inspire action",
                    "speaker": "Simon Sinek",
                    "duration": "18:04",
                    "views": "52M",
                    "link": "https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action"
                },
                {
                    "id": "2",
                    "title": "The power of vulnerability",
                    "speaker": "Brené Brown",
                    "duration": "20:03",
                    "views": "60M",
                    "link": "https://www.ted.com/talks/brene_brown_the_power_of_vulnerability"
                },
                {
                    "id": "3",
                    "title": "Your body language may shape who you are",
                    "speaker": "Amy Cuddy",
                    "duration": "20:55",
                    "views": "47M",
                    "link": "https://www.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are"
                },
                {
                    "id": "4",
                    "title": "How to speak so that people want to listen",
                    "speaker": "Julian Treasure",
                    "duration": "9:59",
                    "views": "15M",
                    "link": "https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen"
                },
                {
                    "id": "5",
                    "title": "The skill of self-confidence",
                    "speaker": "Dr. Ivan Joseph",
                    "duration": "13:40",
                    "views": "6.2M",
                    "link": "https://www.ted.com/talks/ivan_joseph_the_skill_of_self_confidence"
                }
            ]
            return ted_talks
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get TED talks: {str(e)}")
    
    return router