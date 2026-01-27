import requests
import sys

URL = "https://anirudh903-report-generator-streamlit-app-5dgufz.streamlit.app/"

def wake_app():
    try:
        response = requests.get(URL, timeout=30)
        if response.status_code == 200:
            print(f"Successfully pinged app at {URL}. Status: 200 OK")
        else:
            print(f"App returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error pinging app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    wake_app()
