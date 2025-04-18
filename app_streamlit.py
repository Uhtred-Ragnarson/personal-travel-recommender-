# app_streamlit.py

import pandas as pd
import google.generativeai as genai
import csv
from datetime import datetime
import streamlit as st

# Configure your Gemini API key
genai.configure(api_key="AIzaSyCSJDe1w2liqNJVON0W_0ffRG4chhpIo7A")  # Replace with your real key

# Load the dataset
data = pd.read_csv("Updated_Expanded_Destinations.csv")



# ----------------------
# Adding Dynamic Background
# ----------------------

# CSS for dynamic background (gradient and animation)
# Add dynamic background using CSS
st.markdown("""
    <style>
    body {
        background: linear-gradient(45deg, #ff7e5f, #feb47b);
        background-size: 400% 400%;
        animation: gradientBackground 15s ease infinite;
        color: #fff;
        font-family: 'Arial', sans-serif;
        height: 100vh;
        margin: 0;
    }
    
    .css-1aumxhk {
        color: white;
    }
    
    .stButton>button {
        background-color: #ff7e5f;
        color: white;
        border-radius: 10px;
    }

    .stTextInput>div>input {
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
    }
    
    .stSelectbox>div>div>input {
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
    }
    
    .stTextArea>div>textarea {
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
    }

    @keyframes gradientBackground {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
""", unsafe_allow_html=True)


# ----------------------
# User Inputs
# ----------------------
user_weather = st.text_input("Preferred weather (e.g., cold, warm, rainy):")
travel_month = st.selectbox("Planned travel month:", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
group_size = st.number_input("Number of people traveling:", min_value=1, value=1)
interest = st.text_input("Travel interest (e.g., beaches, mountains, temples):")
additional_info = st.text_input("Any additional preference you would like to add:")

# Filter dataset based on user preferences
filtered_data = data[
    data['Weather'].str.lower().str.contains(user_weather.lower(), na=False) &
    data['BestTimeToVisit'].str.contains(travel_month, case=False, na=False) &
    data['Type'].str.lower().str.contains(interest.lower(), na=False)
]

# Load feedback CSV
feedback_df = pd.read_csv("feedback.csv")

# Split LikedDestinations into individual entries and flatten the list
liked_dest_list = feedback_df["LikedDestinations"].dropna().str.split(",").explode().str.strip().unique()

# Get matching entries from the original dataset
top_feedback_destinations = data[data["Name"].isin(liked_dest_list)][["Name", "Weather", "Type", "BestTimeToVisit"]].drop_duplicates().reset_index(drop=True)

# Fallback to sample if no match
if filtered_data.empty:
    filtered_data = data.sample(10)

# Prepare prompt for Gemini
prompt = f"""
You are a helpful travel assistant.

Your task is to recommend **minimum 3 to 5 travel destinations** in India based on the user's preferences.

1. Prioritize destinations from the main dataset below.  
2. If not enough matches, check the destinations liked by users (feedback dataset).  
3. Only if still insufficient, use your general knowledge — but do NOT mention this in your response.

---

### User Preferences:
- Group size: {group_size}
- Weather preference: {user_weather}
- Travel month: {travel_month}
- Interest: {interest}
- Additional preference: {additional_info}

---

### Main Dataset (preferred source):
Each row: Name, Weather, Type, BestTimeToVisit

{filtered_data[['Name','Weather','Type','BestTimeToVisit']].to_string(index=False)}

---

### Previously Liked Destinations (user feedback):
Each row: Name, Weather, Type, BestTimeToVisit

{top_feedback_destinations.to_string(index=False)}

---

### Instructions:
- Output a numbered list of **up to 5 destinations**
- Give 1 short reason for each
- Do not add any other explanation or note
- Keep tone direct and useful
"""

# Call Gemini
model = genai.GenerativeModel('gemini-2.0-flash')  # Use a valid model like 'gemini-pro'
response = model.generate_content(prompt)

# Show recommendations
st.subheader("Recommended Destinations:")
st.write(response.text)

# ----------------------
# Feedback Collection
# ----------------------

st.subheader("Your Feedback")

liked = st.selectbox("Did you like any of these destinations?", ["", "Yes", "No"])

liked_places = ""
if liked == "Yes":
    liked_places = st.text_input("Which destinations did you like? (Separate by comma):").strip()

if liked:  # If feedback is provided
    feedback_file = "feedback.csv"
    fields = [
        'Timestamp', 'GroupSize', 'UserWeather', 'TravelMonth',
        'Interest', 'AdditionalInfo', 'LikedDestinations'
    ]

    feedback_row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        group_size, user_weather, travel_month,
        interest, additional_info, liked_places
    ]

    try:
        with open(feedback_file, 'a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(fields)
            writer.writerow(feedback_row)
        st.success("Thank you for your feedback!")
    except Exception as e:
        st.error(f"❌ Failed to save feedback: {e}")
