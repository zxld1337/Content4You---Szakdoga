from locust import HttpUser, task, between


# python -m locust -f performance_test.py --host=http://127.0.0.1:5000
class RecommenderTester(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post("/api/auth/login", json={
            "username": "testuser", 
            "password": "testpassword123"
        })

    @task
    def get_recommendations(self):
        self.client.get("/api/posts/recommendations")