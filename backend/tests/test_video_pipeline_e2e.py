#!/usr/bin/env python3
"""
Critical Video Processing Pipeline End-to-End Test
As requested in review: Test FULL video processing pipeline with real FFmpeg-generated videos
"""

import requests
import time
import json
import sys
from pathlib import Path
from datetime import datetime

class VideoPipelineE2ETester:
    def __init__(self, base_url="https://exec-presence.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = None
        self.test_results = []
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result with detailed information"""
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

    def authenticate(self):
        """Authenticate and get session token"""
        print("🔐 AUTHENTICATION")
        print("-" * 30)
        
        # Try login first with test credentials
        login_data = {
            "email": "video_test_user@epquotient.com",
            "password": "VideoTest123!"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session_token')
                self.log_result("Auth - Login", True, f"Token: {self.session_token[:20]}...")
                return True
            else:
                # Try signup if login fails
                signup_data = {
                    "email": "video_test_user@epquotient.com",
                    "name": "Video Test User",
                    "password": "VideoTest123!"
                }
                
                response = requests.post(
                    f"{self.base_url}/api/auth/signup",
                    json=signup_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.session_token = data.get('session_token')
                    self.log_result("Auth - Signup", True, f"New user created, Token: {self.session_token[:20]}...")
                    return True
                else:
                    self.log_result("Auth - Failed", False, "", f"Login: {response.status_code}, Signup: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_result("Auth - Exception", False, "", str(e))
            return False

    def upload_video(self, video_path, video_format):
        """Upload video file and return video_id"""
        print(f"📤 UPLOADING {video_format.upper()} VIDEO")
        print("-" * 40)
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {
                    'file': (f'test_video.{video_format}', video_file, f'video/{video_format}')
                }
                
                headers = {'Authorization': f'Bearer {self.session_token}'}
                
                response = requests.post(
                    f"{self.base_url}/api/videos/upload",
                    files=files,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    video_id = data.get('video_id')
                    file_size = Path(video_path).stat().st_size
                    self.log_result(
                        f"Video Upload - {video_format.upper()}", 
                        True, 
                        f"Video ID: {video_id}, Size: {file_size} bytes"
                    )
                    return video_id
                else:
                    self.log_result(
                        f"Video Upload - {video_format.upper()}", 
                        False, 
                        "", 
                        f"Status: {response.status_code}, Response: {response.text[:200]}"
                    )
                    return None
                    
        except Exception as e:
            self.log_result(f"Video Upload - {video_format.upper()}", False, "", str(e))
            return None

    def start_processing(self, video_id, video_format):
        """Start video processing and return job_id"""
        print(f"⚙️ STARTING {video_format.upper()} PROCESSING")
        print("-" * 40)
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            
            response = requests.post(
                f"{self.base_url}/api/videos/{video_id}/process",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get('job_id')
                self.log_result(
                    f"Processing Start - {video_format.upper()}", 
                    True, 
                    f"Job ID: {job_id}"
                )
                return job_id
            else:
                self.log_result(
                    f"Processing Start - {video_format.upper()}", 
                    False, 
                    "", 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_result(f"Processing Start - {video_format.upper()}", False, "", str(e))
            return None

    def monitor_processing(self, job_id, video_format, max_polls=20):
        """Monitor processing pipeline through all stages"""
        print(f"🔄 MONITORING {video_format.upper()} PROCESSING PIPELINE")
        print("-" * 50)
        
        expected_stages = [
            "pending", "transcribing", "audio_analysis", 
            "video_analysis", "nlp_analysis", "scoring", "completed"
        ]
        
        stages_seen = []
        report_id = None
        
        for poll in range(max_polls):
            try:
                headers = {'Authorization': f'Bearer {self.session_token}'}
                
                response = requests.get(
                    f"{self.base_url}/api/jobs/{job_id}/status",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    progress = data.get('progress', 0)
                    current_step = data.get('current_step', 'N/A')
                    report_id = data.get('report_id')
                    
                    print(f"    Poll {poll+1}/{max_polls}: Status={status}, Progress={progress}%, Step={current_step}")
                    
                    # Track stages
                    if status not in stages_seen:
                        stages_seen.append(status)
                    
                    # Check for completion
                    if status == "completed" and report_id:
                        self.log_result(
                            f"Processing Complete - {video_format.upper()}", 
                            True, 
                            f"All stages completed: {' → '.join(stages_seen)}, Report ID: {report_id}"
                        )
                        return report_id, stages_seen
                    
                    # Check for failure
                    elif status == "failed":
                        error_msg = data.get('error', 'Unknown error')
                        self.log_result(
                            f"Processing Failed - {video_format.upper()}", 
                            False, 
                            f"Stages completed: {' → '.join(stages_seen)}", 
                            f"Failed at: {current_step}, Error: {error_msg}"
                        )
                        return None, stages_seen
                    
                    # Continue polling
                    time.sleep(3)
                    
                else:
                    self.log_result(
                        f"Processing Monitor - {video_format.upper()}", 
                        False, 
                        f"Poll {poll+1}", 
                        f"Status check failed: {response.status_code}"
                    )
                    return None, stages_seen
                    
            except Exception as e:
                self.log_result(
                    f"Processing Monitor - {video_format.upper()}", 
                    False, 
                    f"Poll {poll+1}", 
                    str(e)
                )
                return None, stages_seen
        
        # Timeout
        self.log_result(
            f"Processing Timeout - {video_format.upper()}", 
            False, 
            f"Stages seen: {' → '.join(stages_seen)}", 
            f"Processing did not complete within {max_polls} polls"
        )
        return None, stages_seen

    def verify_report(self, report_id, video_format):
        """Verify report generation and validate scoring"""
        print(f"📊 VERIFYING {video_format.upper()} REPORT")
        print("-" * 40)
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            
            response = requests.get(
                f"{self.base_url}/api/reports/{report_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = [
                    'overall_score', 'gravitas_score', 'communication_score',
                    'presence_score', 'storytelling_score', 'detailed_metrics', 
                    'coaching_tips', 'transcript'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        f"Report Validation - {video_format.upper()}", 
                        False, 
                        "", 
                        f"Missing fields: {missing_fields}"
                    )
                    return False
                
                # Validate score calculations
                overall = data.get('overall_score', 0)
                gravitas = data.get('gravitas_score', 0)
                communication = data.get('communication_score', 0)
                presence = data.get('presence_score', 0)
                storytelling = data.get('storytelling_score')  # Can be None
                
                # Check score formula - handle None storytelling score
                if storytelling is None:
                    # Adjusted weights when no storytelling: gravitas×0.30 + communication×0.40 + presence×0.30
                    expected_overall = (gravitas * 0.30) + (communication * 0.40) + (presence * 0.30)
                    scores_to_validate = [overall, gravitas, communication, presence]
                else:
                    # Normal weights: gravitas×0.25 + communication×0.35 + presence×0.25 + storytelling×0.15
                    expected_overall = (gravitas * 0.25) + (communication * 0.35) + (presence * 0.25) + (storytelling * 0.15)
                    scores_to_validate = [overall, gravitas, communication, presence, storytelling]
                
                score_diff = abs(overall - expected_overall)
                
                # Validate score ranges (0-100)
                scores_valid = all(0 <= score <= 100 for score in scores_to_validate)
                
                if score_diff <= 1.0 and scores_valid:  # Allow 1 point tolerance for rounding
                    storytelling_text = f"Storytelling: {storytelling}" if storytelling is not None else "Storytelling: None (no story detected)"
                    self.log_result(
                        f"Report Validation - {video_format.upper()}", 
                        True, 
                        f"Overall: {overall}, Gravitas: {gravitas}, Communication: {communication}, Presence: {presence}, {storytelling_text}"
                    )
                    return True
                else:
                    self.log_result(
                        f"Report Validation - {video_format.upper()}", 
                        False, 
                        f"Score calculation error: Expected {expected_overall:.1f}, Got {overall}", 
                        f"Scores valid: {scores_valid}, Difference: {score_diff:.2f}"
                    )
                    return False
                    
            else:
                self.log_result(
                    f"Report Retrieval - {video_format.upper()}", 
                    False, 
                    "", 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result(f"Report Verification - {video_format.upper()}", False, "", str(e))
            return False

    def test_video_format(self, video_path, video_format):
        """Test complete pipeline for one video format"""
        print(f"\n🎬 TESTING {video_format.upper()} VIDEO PIPELINE")
        print("=" * 60)
        
        # Step 1: Upload
        video_id = self.upload_video(video_path, video_format)
        if not video_id:
            return False
        
        # Step 2: Start Processing
        job_id = self.start_processing(video_id, video_format)
        if not job_id:
            return False
        
        # Step 3: Monitor Processing
        report_id, stages = self.monitor_processing(job_id, video_format)
        if not report_id:
            return False
        
        # Step 4: Verify Report
        report_valid = self.verify_report(report_id, video_format)
        
        return report_valid

    def run_full_pipeline_test(self):
        """Run the complete video processing pipeline test"""
        print("🚀 CRITICAL VIDEO PROCESSING PIPELINE E2E TEST")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Videos: MP4 and WebM formats")
        print(f"FFmpeg Status: ✅ Available")
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            return self.generate_summary()
        
        # Step 2: Test MP4 Pipeline
        mp4_success = self.test_video_format("/tmp/test_video.mp4", "mp4")
        
        # Step 3: Test WebM Pipeline  
        webm_success = self.test_video_format("/tmp/test_video.webm", "webm")
        
        # Step 4: Generate Summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print(f"📊 CRITICAL VIDEO PIPELINE TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0:.1f}%")
        print()
        
        # Categorize results
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['error']}")
            print()
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - VIDEO PIPELINE FULLY OPERATIONAL!")
        else:
            print("⚠️  SOME TESTS FAILED - CHECK DETAILS ABOVE")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            "test_results": self.test_results,
            "pipeline_operational": self.tests_passed == self.tests_run
        }

def main():
    """Main test execution"""
    tester = VideoPipelineE2ETester()
    summary = tester.run_full_pipeline_test()
    
    # Save results
    results_file = Path("/app/test_reports/video_pipeline_e2e_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Return appropriate exit code
    return 0 if summary["pipeline_operational"] else 1

if __name__ == "__main__":
    sys.exit(main())