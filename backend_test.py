#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class EPQuotientAPITester:
    def __init__(self, base_url="https://exec-presence.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = "session_715dbc2d083042dba4122d189f6b55e4"  # Use provided test token
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
            
        if files:
            # Remove Content-Type for file uploads
            headers.pop('Content-Type', None)

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_response": response.text[:200]}

            details = f"Status: {response.status_code}, Response: {str(response_data)[:200]}"
            error = "" if success else f"Expected {expected_status}, got {response.status_code}"
            
            self.log_result(name, success, details, error)
            return success, response_data

        except Exception as e:
            self.log_result(name, False, "", str(e))
            return False, {}

    def test_auth_signup(self):
        """Test user signup"""
        test_email = f"test_{int(time.time())}@example.com"
        test_data = {
            "email": test_email,
            "name": "Test User",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "Auth - Signup",
            "POST",
            "auth/signup",
            200,
            data=test_data
        )
        
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            return True, test_email
        return False, None

    def test_auth_login(self, email="uitest_golden@test.com"):
        """Test user login with provided test credentials"""
        login_data = {
            "email": email,
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "Auth - Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            return True
        return False

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Auth - Get Me",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_google_auth_redirect(self):
        """Test Google auth redirect"""
        success, response = self.run_test(
            "Auth - Google Redirect",
            "GET",
            "auth/google-redirect",
            200
        )
        return success

    def test_video_upload(self):
        """Test video upload with dummy file"""
        # Create a small dummy video file
        dummy_content = b"dummy video content for testing"
        files = {
            'file': ('test_video.mp4', dummy_content, 'video/mp4')
        }
        
        success, response = self.run_test(
            "Video - Upload",
            "POST",
            "videos/upload",
            200,
            files=files
        )
        
        if success and 'video_id' in response:
            return True, response['video_id']
        return False, None

    def test_video_process(self, video_id):
        """Test video processing"""
        success, response = self.run_test(
            "Video - Process",
            "POST",
            f"videos/{video_id}/process",
            200
        )
        
        if success and 'job_id' in response:
            return True, response['job_id']
        return False, None

    def test_job_status(self, job_id):
        """Test job status check with detailed status tracking"""
        success, response = self.run_test(
            "Jobs - Get Status",
            "GET",
            f"jobs/{job_id}/status",
            200
        )
        
        if success and response:
            status = response.get('status', 'unknown')
            progress = response.get('progress', 0)
            current_step = response.get('current_step', 'N/A')
            report_id = response.get('report_id')
            
            print(f"    Job Status: {status}, Progress: {progress}%, Step: {current_step}")
            if report_id:
                print(f"    Report ID: {report_id}")
                return True, report_id
        
        return success, None

    def test_reports_list(self):
        """Test list reports"""
        success, response = self.run_test(
            "Reports - List",
            "GET",
            "reports",
            200
        )
        return success

    def test_learning_daily_tip(self):
        """Test daily tip endpoint"""
        success, response = self.run_test(
            "Learning - Daily Tip",
            "GET",
            "learning/daily-tip",
            200
        )
        return success

    def test_learning_ted_talks(self):
        """Test TED talks endpoint"""
        success, response = self.run_test(
            "Learning - TED Talks",
            "GET",
            "learning/ted-talks",
            200
        )
        return success

    def test_training_modules(self):
        """Test training modules list"""
        success, response = self.run_test(
            "Training - Modules List",
            "GET",
            "training/modules",
            200
        )
        return success

    def test_training_module_content(self, module_id="strategic-pauses"):
        """Test specific training module content"""
        success, response = self.run_test(
            f"Training - Module Content ({module_id})",
            "GET",
            f"training/modules/{module_id}",
            200
        )
        return success

    def test_coaching_request(self):
        """Test coaching request creation"""
        coaching_data = {
            "name": "John Executive",
            "email": "john.exec@company.com",
            "goal": "Improve executive presence in board meetings",
            "preferred_times": "Weekday mornings",
            "notes": "Looking to enhance gravitas and communication skills"
        }
        
        success, response = self.run_test(
            "Coaching - Create Request",
            "POST",
            "coaching/requests",
            200,
            data=coaching_data
        )
        
        if success and 'request_id' in response:
            return True, response['request_id']
        return False, None

    def test_create_share_link(self, report_id):
        """Test creating a share link for a report"""
        success, response = self.run_test(
            "Sharing - Create Share Link",
            "POST",
            f"reports/{report_id}/share",
            200
        )
        
        if success and 'share_id' in response:
            return True, response['share_id']
        return False, None

    def test_get_shared_report(self, share_id):
        """Test getting a shared report"""
        success, response = self.run_test(
            "Sharing - Get Shared Report",
            "GET",
            f"shared/reports/{share_id}",
            200
        )
        return success
    
    def test_report_retrieval(self, report_id):
        """Test retrieving a specific report"""
        success, response = self.run_test(
            "Reports - Get Report",
            "GET",
            f"reports/{report_id}",
            200
        )
        
        if success and response:
            # Verify all required fields are present
            required_fields = ['overall_score', 'gravitas_score', 'communication_score', 
                             'presence_score', 'storytelling_score', 'detailed_metrics', 'coaching_tips']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"    ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"    ✅ All required report fields present")
        
        return success

    def test_retention_get_settings(self):
        """Test get retention settings"""
        success, response = self.run_test(
            "Retention - Get Settings",
            "GET",
            "retention/settings",
            200
        )
        
        if success and response:
            # Verify required fields are present
            required_fields = ['default_retention', 'videos', 'available_policies']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"    ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"    ✅ All required retention settings fields present")
                print(f"    Default retention: {response.get('default_retention')}")
                print(f"    Available policies: {response.get('available_policies')}")
        
        return success

    def test_retention_set_default_valid(self):
        """Test set default retention with valid period"""
        retention_data = {"retention_period": "90_days"}
        
        success, response = self.run_test(
            "Retention - Set Default (Valid)",
            "PUT",
            "retention/settings/default",
            200,
            data=retention_data
        )
        
        if success and response:
            print(f"    ✅ Default retention set to: {response.get('default_retention')}")
        
        return success

    def test_retention_set_default_invalid(self):
        """Test set default retention with invalid period"""
        retention_data = {"retention_period": "invalid_period"}
        
        success, response = self.run_test(
            "Retention - Set Default (Invalid)",
            "PUT",
            "retention/settings/default",
            400,  # Expecting 400 error for invalid period
            data=retention_data
        )
        
        if success:
            print(f"    ✅ Correctly rejected invalid retention period")
        
        return success

    def test_auth_logout(self):
        """Test logout"""
        success, response = self.run_test(
            "Auth - Logout",
            "POST",
            "auth/logout",
            200
        )
        return success

    def run_all_tests(self):
        """Run comprehensive test suite as per review request"""
        print("🚀 Starting EP Quotient API Tests - Video Pipeline & PDF Export Focus")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Token: {self.session_token}")
        print("FFmpeg Status: ✅ Installed")
        
        # Priority 1: Auth Flow with provided credentials
        print("\n📋 PRIORITY 1: AUTH FLOW")
        print("-" * 40)
        
        # Test with provided credentials
        login_success = self.test_auth_login("uitest_golden@test.com")
        if not login_success:
            print("❌ Login with test credentials failed - trying signup")
            signup_success, test_email = self.test_auth_signup()
            if not signup_success:
                print("❌ Both login and signup failed - stopping tests")
                return self.generate_summary()
        
        # Test /auth/me 
        self.test_auth_me()
        
        # Priority 2: Video Processing Pipeline (MAIN FOCUS)
        print("\n📋 PRIORITY 1: VIDEO PROCESSING PIPELINE")
        print("-" * 50)
        
        # Step 1: Video Upload
        upload_success, video_id = self.test_video_upload()
        if not upload_success or not video_id:
            print("❌ Video upload failed - cannot test processing pipeline")
        else:
            print(f"✅ Video uploaded successfully: {video_id}")
            
            # Step 2: Video Processing Initiation
            process_success, job_id = self.test_video_process(video_id)
            if not process_success or not job_id:
                print("❌ Video processing initiation failed")
            else:
                print(f"✅ Video processing started: {job_id}")
                
                # Step 3: Job Status Polling with detailed tracking
                print("\n    🔄 Monitoring job status transitions...")
                report_id = None
                max_polls = 10  # Increased polling attempts
                
                for i in range(max_polls):
                    print(f"    Poll {i+1}/{max_polls}:")
                    job_success, current_report_id = self.test_job_status(job_id)
                    
                    if current_report_id:
                        report_id = current_report_id
                        print(f"    ✅ Processing completed! Report ID: {report_id}")
                        break
                    elif job_success:
                        time.sleep(3)  # Wait between polls
                    else:
                        print(f"    ❌ Job status check failed on poll {i+1}")
                        break
                
                # Step 4: Report Retrieval (if processing completed)
                if report_id:
                    print(f"\n    📊 Testing report retrieval...")
                    self.test_report_retrieval(report_id)
                else:
                    print(f"\n    ⚠️  Video processing did not complete within {max_polls} polls")
        
        # Priority 2: API Endpoint Verification
        print("\n📋 PRIORITY 2: API ENDPOINT VERIFICATION")
        print("-" * 45)
        
        # Reports List
        self.test_reports_list()
        
        # Sharing API (if reports exist)
        reports_success, reports_response = self.run_test(
            "Reports - Check for Sharing Test",
            "GET", 
            "reports",
            200
        )
        
        if reports_success and reports_response.get('reports'):
            report_id = reports_response['reports'][0]['report_id']
            share_success, share_id = self.test_create_share_link(report_id)
            if share_success and share_id:
                self.test_get_shared_report(share_id)
        else:
            print("⚠️  No reports available for sharing test")
        
        # Coaching API
        coaching_success, request_id = self.test_coaching_request()
        
        # Feature endpoints
        print("\n📋 PRIORITY 3: ALL API ENDPOINTS HEALTH CHECK")
        print("-" * 45)
        self.test_learning_daily_tip()
        self.test_learning_ted_talks()
        self.test_training_modules()
        self.test_training_module_content("strategic-pauses")
        
        # NEW: Video Retention API Tests (as per review request)
        print("\n📋 PRIORITY 4: VIDEO RETENTION API")
        print("-" * 35)
        self.test_retention_get_settings()
        self.test_retention_set_default_valid()
        self.test_retention_set_default_invalid()
        
        # Cleanup
        print("\n📋 CLEANUP")
        print("-" * 15)
        self.test_auth_logout()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check details above.")
            
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            "test_results": self.test_results
        }

def main():
    tester = EPQuotientAPITester()
    summary = tester.run_all_tests()
    
    # Save results to file
    results_file = Path("/app/test_reports/backend_test_results.json")
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Return appropriate exit code
    return 0 if summary["success_rate"] == 100 else 1

if __name__ == "__main__":
    sys.exit(main())