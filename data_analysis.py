from google.cloud import firestore
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pytz

# Initialize Firestore client
db = firestore.Client(project = 'math-151a-final-project')

# Reference to the Firestore collection
collection_ref = db.collection('traffic_time_UCLA_to_LAX')

# Query the collection for documents
docs = collection_ref.stream()

all_data = []

# Iterate over the documents and print data
for doc in docs:

    # Convert the string to a datetime object
    unix_timestamp = doc.to_dict()['current_time']
    travel_time = doc.to_dict()['duration']
    parts = travel_time.split()
    travel_time = int(parts[0])
    data = [unix_timestamp, travel_time]
    all_data.append(data)
sorted_data = sorted(all_data, key=lambda x: x[0])
print(sorted_data)
# Extract x and y coordinates from the data
timestamps = [entry[0] for entry in sorted_data]
durations = [entry[1] for entry in sorted_data]

# Convert timestamps to datetime objects
datetime_objects_utc = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]

timezone_utc = pytz.utc
timezone_pst = pytz.timezone('America/Los_Angeles')  # PST (Pacific Standard Time)
datetime_objects = [dt.replace(tzinfo=timezone_utc).astimezone(timezone_pst) for dt in datetime_objects_utc]


start_time = min(datetime_objects)
end_time = max(datetime_objects)

# Generate ticks for every hour
ticks = []
current_time = start_time.replace(minute=0, second=0, microsecond=0)
while current_time <= end_time:
    ticks.append(current_time)
    current_time += timedelta(hours=4)
# Plotting
plt.figure(figsize=(18, 6))  # Adjust figure size to make x-axis longer
plt.plot(datetime_objects, durations)
plt.xlabel('Time')
plt.ylabel('Duration')
plt.title('Data with Timestamps and Durations')
plt.subplots_adjust(bottom=0.5)
plt.xticks(ticks, [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in ticks], rotation=45, ha='right')
# Display the plot
plt.savefig('plot.png')