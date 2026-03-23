"""
Roku External Control Protocol (ECP) client.
Roku must be on the same WiFi network and in developer mode.
"""
import requests
import time

class RokuECP:
    def __init__(self, ip: str):
        self.base = f"http://{ip}:8060"

    def device_info(self) -> dict:
        r = requests.get(f"{self.base}/query/device-info", timeout=5)
        r.raise_for_status()
        return {"status": r.status_code, "body": r.text}

    def keypress(self, key: str):
        """Send a key press. Keys: Home, Up, Down, Left, Right, Select, Back, Play, etc."""
        r = requests.post(f"{self.base}/keypress/{key}", timeout=5)
        r.raise_for_status()
        return r.status_code

    def launch_channel(self, channel_id: str):
        """Launch a channel by its Roku channel ID."""
        r = requests.post(f"{self.base}/launch/{channel_id}", timeout=5)
        r.raise_for_status()

    def active_app(self) -> str:
        r = requests.get(f"{self.base}/query/active-app", timeout=5)
        r.raise_for_status()
        return r.text

    def navigate_to_screensaver_settings(self):
        """Navigate to screensaver timeout settings via Roku menu."""
        self.keypress("Home")
        time.sleep(1.5)
        # Navigate to Settings
        for _ in range(5):
            self.keypress("Up")
            time.sleep(0.3)
        self.keypress("Right")
        time.sleep(0.5)
        # Down to Settings
        for _ in range(5):
            self.keypress("Down")
            time.sleep(0.3)
        self.keypress("Select")
        time.sleep(1)

    def ping(self) -> bool:
        """Check if Roku is reachable."""
        try:
            r = requests.get(f"{self.base}/query/device-info", timeout=3)
            return r.status_code == 200
        except Exception:
            return False
