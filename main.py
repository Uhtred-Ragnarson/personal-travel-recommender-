
# main.py

import pandas as pd
import google.generativeai as genai
import csv
from datetime import datetime

# Configure your Gemini API key
genai.configure(api_key="AIzaSyCSJDe1w2liqNJVON0W_0ffRG4chhpIo7A")  # Replace with your real key

# Load the dataset
data = pd.read_csv("Updated_Expanded_Destinations.csv")

# Show available columns
print("Dataset columns:", data.columns)

# Get user inputs
user_weather = input("Preferred weather (e.g., cold, warm, rainy): ").lower()
travel_month = input("Planned travel month (e.g., October): ").capitalize()
group_size = input("Number of people traveling: ")
interest = input("Travel interest (e.g., beaches, mountains, temples): ").lower()
additional_info = input("Any additional preference you would like to add: ")

# Filter dataset
filtered_data = data[
    data['Weather'].str.lower().str.contains(user_weather, na=False) &
    data['BestTimeToVisit'].str.contains(travel_month, case=False, na=False) &
    data['Type'].str.lower().str.contains(interest, na=False)
]
#feedbck load
# Load feedback CSV
feedback_df = pd.read_csv("feedback.csv")

# Split LikedDestinations into individual entries and flatten the list
liked_dest_list = feedback_df["LikedDestinations"].dropna().str.split(",").explode().str.strip().unique()

# Get matching entries from the original dataset
top_feedback_destinations = data[data["Name"].isin(liked_dest_list)][["Name", "Weather", "Type", "BestTimeToVisit"]].drop_duplicates().reset_index(drop=True)

# Fallback to sample if no match
if filtered_data.empty:
    filtered_data = data.sample(10)

# Prepare prompt
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

# Show output
print("\nHere are the recommendations based on your preferences:\n")
print(response.text)

# --------------------------
# Collect and store feedback
# --------------------------

liked = input("\nDid you like any of these destinations? (yes/no): ").strip().lower()

liked_places = ""
if liked == "yes":
    liked_places = input("Which destinations did you like? (Separate by comma): ").strip()

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
    print(" Thank you for your Feedback.")
except Exception as e:
    print(f"❌ Failed to save feedback: {e}")
