import streamlit as st
import os
from PIL import Image
import time
import plotly.graph_objects as go
from datetime import datetime
import base64

# Set page config
st.set_page_config(page_title="GREEN GUARDIAN",
                   page_icon="🌏", layout="wide")

# Custom styling
st.markdown(
    """
    <style>
    body {
        background-color: #e0f2f7;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 30px;
    }
    .header {
        font-size: 24px;
        color: #2c3e50;
        font-weight: bold;
        text-align: center;
    }
    /* Center align all text elements */
    .stMarkdown, .stText, div {
        text-align: center !important;
    }
    /* Center align plotly charts */
    .js-plotly-plot {
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Ensure sidebar alerts are centered */
    .stAlert {
        text-align: center;
    }
    /* Center the refresh button */
    .stButton {
        text-align: center;
    }
    .pie-section {
        margin-top: 30px;
        margin-bottom: 30px;
        padding: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_base64_encoded_image(image_path):
    """Encodes image to Base64 for proper embedding in HTML"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def parse_line(line):
    """Parse a line from data_base.txt into a dictionary"""
    data = {}
    current_key = None
    current_value = []
    parts = line.split(', ')

    for part in parts:
        if ': ' in part:
            # If we have a stored key and value, save it
            if current_key:
                data[current_key] = ', '.join(current_value)
                current_value = []

            # Split new key-value pair
            key, value = part.split(': ', 1)
            current_key = key
            current_value.append(value)
        else:
            # This is a continuation of the previous value
            current_value.append(part)

    # Save the last key-value pair
    if current_key:
        data[current_key] = ', '.join(current_value)

    return data


def get_sensor_data():
    """Read sensor data from data_base.txt"""
    try:
        # print("Attempting to read data_base.txt")  # Debug print

        if not os.path.exists('data_base.txt'):
            print("data_base.txt does not exist")  # Debug print
            raise FileNotFoundError("data_base.txt not found")

        with open('data_base.txt', 'r') as f:
            lines = f.readlines()
            # print(f"Number of lines read: {len(lines)}")  # Debug print
            if lines:
                # print(f"First line: {lines[0]}")  # Debug print
                latest_data = parse_line(lines[0])
                # print(f"Parsed data: {latest_data}")  # Debug print
                return {
                    'code': latest_data['Dustbin Code'],
                    'location': latest_data['Dustbin Location'],
                    'BR': float(latest_data['BR']),
                    'BNR': float(latest_data['BNR']),
                    'NBR': float(latest_data['NBR']),
                    'NBNR': float(latest_data['NBNR']),
                    'last_used': latest_data['Last used'],
                    'recycle_tips': latest_data['Recyclable tips'],
                    'bio_facts': latest_data['Bio degradable facts'],
                    'last_item': latest_data.get('Item', 'Unknown'),
                    'last_category': latest_data.get('Category', 'Unknown')
                }
            else:
                print("File is empty")  # Debug print
                raise ValueError("data_base.txt is empty")
    except Exception as e:
        print(f"Error in get_sensor_data: {e}")  # Debug print
        st.error(f"Error reading data: {e}")
        return {
            'code': 'Unknown', 'location': 'Unknown',
            'BR': 0, 'BNR': 0, 'NBR': 0, 'NBNR': 0,
            'last_used': 'Unknown',
            'recycle_tips': '', 'bio_facts': '',
            'last_item': 'Unknown',
            'last_category': 'Unknown'
        }


def get_type_description(type_code):
    """Convert type code to full description"""
    type_mapping = {
        'BR': 'Bio-degradable & Recyclable',
        'BNR': 'Bio-degradable & Non-Recyclable',
        'NBR': 'Non Bio-degradable & Recyclable',
        'NBNR': 'Non Bio-degradable & Non-Recyclable'
    }
    return type_mapping.get(type_code, type_code)


# Title first
st.markdown("<div class='title'>🌏 GREEN GUARDIAN</div>",
            unsafe_allow_html=True)

# Get sensor data
sensor_data = get_sensor_data()

# Display bin info below title
st.markdown(f"""
    <div class='header' style='text-align: center;'>📍 Location: {sensor_data['location']} (Bin: {sensor_data['code']})</div>
    <div style='font-size: 18px; margin: 10px 0; text-align: center;'>
        <p>🕒 <strong>Last Used:</strong> {sensor_data['last_used']}</p>
        <p>📦 <strong>Last Item Received:</strong> {sensor_data['last_item']}</p>
        <p>🗑️ <strong>Waste Type:</strong> {get_type_description(sensor_data['last_category'])}</p>
    </div>
""", unsafe_allow_html=True)

# Add spacing before Bin Levels section
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Bin Levels Section
st.markdown("""
    <div class='header'>📊 Bin Levels</div>
    <div style='margin-top: 40px; margin-bottom: 40px;'></div>
""", unsafe_allow_html=True)

colors = ['#2ecc71', '#e74c3c', '#3498db', '#f1c40f']

# Add vertical spacing between pie charts and their descriptions
st.markdown("""
    <style>
    .pie-section {
        margin-top: 30px;
        margin-bottom: 30px;
        padding: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

bins = ['BR', 'BNR', 'NBR', 'NBNR']
labels = ["Bio & Recyclable", "Bio & Non-Recyclable",
          "Non-Bio & Recyclable", "Non-Bio & Non-Recyclable"]
pie_cols = st.columns(4)

for i, col in enumerate(pie_cols):
    with col:
        fig = go.Figure(data=[go.Pie(
            labels=["Filled", "Empty"],
            values=[sensor_data[bins[i]], 100 - sensor_data[bins[i]]],
            marker_colors=[colors[i], "#ecf0f1"],
            hole=.3
        )])
        fig.update_layout(
            title={
                'text': labels[i],
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.95,
                'pad': {'b': 20}
            },
            width=180,
            height=180,
            margin=dict(t=40, b=20, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<div style='text-align: center;'><b>{
                    sensor_data[bins[i]]}%</b> filled</div>", unsafe_allow_html=True)

        # Add waste type description
        waste_descriptions = {
            'BR': 'Bio-degradable & Recyclable waste like paper, cardboard',
            'BNR': 'Bio-degradable & Non-Recyclable waste like food waste',
            'NBR': 'Non Bio-degradable & Recyclable waste like plastic, glass',
            'NBNR': 'Non Bio-degradable & Non-Recyclable waste like medical waste'
        }
        st.markdown(f"""
            <div style='text-align: center; font-size: 14px; color: #666; margin-top: 5px;'>
                {waste_descriptions[bins[i]]}
            </div>
        """, unsafe_allow_html=True)

# Add spacing after pie charts
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Last Item and Map Section
st.markdown("<div class='header'>📸 Last Item Detected & 📍 Bin Location</div>",
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Create two columns for image and map
img_col, map_col = st.columns(2)

with img_col:
    image_path = 'last_item.png'
    if os.path.exists(image_path):
        encoded_image = get_base64_encoded_image(
            image_path)  # Convert to Base64

        # Center-align the image with proper Base64 embedding
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; padding-right: 10px;padding-bottom: 10px; padding-top: 10px;padding-left: 10px;">
                <img src="data:image/png;base64,{encoded_image}" style="width: 1000px; max-width: 103%; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No item detected yet")


with map_col:
    # Embed Google Maps iframe with marker, dark mode, and satellite view
    map_html = f"""
    <div style="width: 100%; height: 400px; margin: 0; padding: 0;">
        <iframe
            width="100%"
            height="100%"
            frameborder="0"
            scrolling="no"
            marginheight="0"
            marginwidth="0"
            src="https://maps.google.com/maps?q={sensor_data['location']}&t=k&z=15&ie=UTF8&iwloc=B&output=embed&mode=dark"
            style="border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); align-items: center;">
        </iframe>
    </div>
    <div style="margin-top: 0px; align-items: center;">
        📍 {sensor_data['location']} (Bin: {sensor_data['code']})
    </div>
    """
    st.markdown(map_html, unsafe_allow_html=True)

# Add spacing before Tips and Facts section
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Tips and Facts Section
st.markdown("<div class='header'>💡 Tips & Facts</div>", unsafe_allow_html=True)

tip_col1, tip_col2 = st.columns(2)

with tip_col1:
    st.markdown("""
        <div class="tips-section">
            <div class="tip-title">
                ♻️ Recycling Tip of the Day
            </div>
            <div class="tip-content">
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'>{
                sensor_data['recycle_tips']}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

with tip_col2:
    st.markdown("""
        <div class="tips-section">
            <div class="tip-title">
                🌱 Bio Degradable Fact of the Day
            </div>
            <div class="fact-content">
    """, unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align: center;'>{sensor_data['bio_facts']}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# Add spacing after section
st.markdown("<br>", unsafe_allow_html=True)

# Sidebar alerts
with st.sidebar:
    st.markdown("<div class='header'>🚨 Alerts</div>", unsafe_allow_html=True)
    alerts = [f"⚠️ {label} bin is {sensor_data[b]}% full" for b,
              label in zip(bins, labels) if sensor_data[b] > 80]
    for alert in alerts:
        st.warning(alert)
    if not alerts:
        st.success("All bins are at safe levels")

# Refresh Button
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 Refresh Data"):
        st.rerun()
# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
