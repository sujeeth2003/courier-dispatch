import random
import uuid

from locust import HttpUser, between, task


class DispatchUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        resp = self.client.post("/couriers", params={"name": f"lt-{uuid.uuid4().hex[:6]}"})
        self.courier_id = resp.json()["id"]

    @task(3)
    def update_location(self):
        lat = 37.75 + random.uniform(-0.05, 0.05)
        lon = -122.42 + random.uniform(-0.05, 0.05)
        self.client.post(f"/couriers/{self.courier_id}/location", json={"lat": lat, "lon": lon})

    @task(1)
    def create_order(self):
        pickup_lat = 37.75 + random.uniform(-0.05, 0.05)
        pickup_lon = -122.42 + random.uniform(-0.05, 0.05)
        self.client.post(
            "/orders",
            json={
                "pickup_lat": pickup_lat,
                "pickup_lon": pickup_lon,
                "dropoff_lat": pickup_lat + 0.01,
                "dropoff_lon": pickup_lon + 0.01,
            },
        )
