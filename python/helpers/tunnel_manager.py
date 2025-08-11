from flaredantic import FlareTunnel, FlareConfig, ServeoConfig, ServeoTunnel
import threading
import time
from urllib.request import urlopen, Request
from urllib.error import URLError


# Singleton to manage the tunnel instance
class TunnelManager:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self.tunnel = None
        self.tunnel_url = None
        self.is_running = False
        self.provider = None
        self.port = None
        self._start_event = threading.Event()
        self._monitor_thread = None

    def start_tunnel(self, port=80, provider="serveo"):
        """Start a new tunnel or return the existing one's URL"""
        if self.is_running and self.tunnel_url:
            return self.tunnel_url

        self.provider = provider
        self.port = port
        self._start_event = threading.Event()

        try:
            # Start tunnel in a separate thread to avoid blocking
            def run_tunnel():
                try:
                    if self.provider == "cloudflared":
                        config = FlareConfig(port=self.port, verbose=True)
                        self.tunnel = FlareTunnel(config)
                    else:  # Default to serveo
                        config = ServeoConfig(port=self.port)  # type: ignore
                        self.tunnel = ServeoTunnel(config)

                    self.tunnel.start()
                    self.tunnel_url = self.tunnel.tunnel_url
                    self.is_running = True
                except Exception as e:
                    print(f"Error in tunnel thread: {str(e)}")
                finally:
                    self._start_event.set()

            tunnel_thread = threading.Thread(target=run_tunnel, daemon=True)
            tunnel_thread.start()

            # Wait for tunnel to start (max 15 seconds)
            started = self._start_event.wait(timeout=15)
            if not started or not self.tunnel_url:
                return None

            self._start_monitor()
            return self.tunnel_url
        except Exception as e:
            print(f"Error starting tunnel: {str(e)}")
            return None

    def stop_tunnel(self):
        """Stop the running tunnel"""
        if self.tunnel and self.is_running:
            try:
                self.tunnel.stop()
                self.is_running = False
                self.tunnel_url = None
                self.provider = None
                self.port = None
                return True
            except Exception:
                return False
        return False

    def get_tunnel_url(self):
        """Get the current tunnel URL if available"""
        return self.tunnel_url if self.is_running else None

    def _start_monitor(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._monitor_thread = threading.Thread(target=self._monitor_tunnel, daemon=True)
        self._monitor_thread.start()

    def _monitor_tunnel(self):
        backoff = 1
        while self.is_running:
            if not self.tunnel_url:
                time.sleep(backoff)
                continue

            try:
                req = Request(self.tunnel_url, method="HEAD")
                with urlopen(req, timeout=5):
                    pass
                backoff = 1
            except URLError as e:
                print(f"Tunnel ping failed: {e}")
                if not self.is_running:
                    break
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                try:
                    self.stop_tunnel()
                finally:
                    # clear monitor reference and attempt restart
                    self._monitor_thread = None
                    self.start_tunnel(self.port or 80, self.provider or "serveo")
                    return
            except Exception as e:
                print(f"Unexpected tunnel monitor error: {e}")

            time.sleep(30)
