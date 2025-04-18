import pandas as pd

# Load your original CSV
df = pd.read_csv("Expanded_Destinations.csv")

# Define type-to-weather mapping
type_to_weather = {
    'Beach': 'Warm',
    'Hill Station': 'Cold',
    'Snow': 'Cold',
    'Historical': 'Hot',
    'Adventure': 'Cool',
    'Nature': 'Cool',
    'Religious': 'Moderate',
    'Wildlife': 'Warm',
    'Desert': 'Hot',
    'Backwater': 'Warm',
    'Island': 'Warm',
    'Lake': 'Cool',
    'Cultural': 'Moderate',
    'Urban': 'Hot',
    'Forest': 'Cool',
    'Mountain': 'Cold',
    'Himalayan': 'Cold',
}

# Add the 'Weather' column
df['Weather'] = df['Type'].map(type_to_weather).fillna('Moderate')

# Save to a new CSV file
df.to_csv("Updated_Expanded_Destinations.csv", index=False)

print("✅ Dataset updated and saved successfully!")
