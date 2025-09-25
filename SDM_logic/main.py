import subprocess
import os

# Run app.py in the background
app_process = subprocess.Popen(['python3', 'app.py'])

# Run streamlit dashboard
streamlit_process = subprocess.Popen(['streamlit', 'run', 'dashboard.py'])

# Wait for both processes
app_process.wait()
streamlit_process.wait()
