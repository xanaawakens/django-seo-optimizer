"""
Performance tests using Locust
Created by avixiii (https://avixiii.com)
"""
from locust import HttpUser, task, between
import random


class SEOUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup before tests"""
        pass
    
    @task(3)
    def get_metadata(self):
        """Test metadata retrieval"""
        self.client.get("/api/metadata/")
    
    @task(2)
    def check_redirects(self):
        """Test redirect checking"""
        paths = [
            "/old-page",
            "/product/123",
            "/blog/2023/12/post"
        ]
        self.client.get(f"/api/redirects/check{random.choice(paths)}")
    
    @task
    def mobile_check(self):
        """Test mobile compatibility check"""
        self.client.get("/api/mobile/check/")
    
    @task
    def generate_amp(self):
        """Test AMP generation"""
        self.client.get("/api/amp/generate/")
