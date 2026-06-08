import urllib.request
import json

def check_endpoint(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        status_code = response.getcode()
        content = response.read().decode('utf-8')
        print(f"URL: {url} -> Status: {status_code}")
        print("Response content preview:")
        print(content[:500])
        print("-" * 50)
    except Exception as e:
        print(f"URL: {url} -> FAILED: {e}")
        print("-" * 50)

print("Checking Lyra Agent Endpoints locally...")
check_endpoint("http://127.0.0.1:8000/api/agents")
check_endpoint("http://127.0.0.1:8000/api/agents/logs")
