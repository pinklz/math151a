from google.cloud import firestore
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
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

# '''
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

plt.clf()

# '''
# Function to perform cubic spline interpolation
def cubic_spline_interpolation(x, x_data, y_data):
    n = len(x_data)
    for i in range(n - 1):
        if x_data[i] <= x <= x_data[i + 1]:
            break
    h = x_data[i + 1] - x_data[i]
    a = (x_data[i + 1] - x) / h
    b = (x - x_data[i]) / h
    interpolated_value = a * y_data[i] + b * y_data[i + 1] + ((a ** 3 - a) * y_data[i + 1] ** 2 + (b ** 3 - b) * y_data[i] ** 2) * h ** 2 / 6


    # Print the polynomial function
    print(f"Piecewise function for interval [{x_data[i]}, {x_data[i+1]}]: {a} * {y_data[i]} + {b} * {y_data[i+1]} + (({a}^3 - {a}) * {y_data[i+1]}^2 + ({b}^3 - {b}) * {y_data[i]}^2) * {h}^2 / 6")
    
    return interpolated_value

# Convert timestamps to Unix timestamps (numerical values)
timestamps_unix = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp() for ts in timestamps]

# Generate x values for plotting using Unix timestamps
x_values = np.linspace(min(timestamps_unix), max(timestamps_unix), 400)

# Compute y values using the piecewise function
y_values = [cubic_spline_interpolation(x, timestamps_unix, durations) for x in x_values]


# Plot the piecewise function
plt.plot(x_values, y_values, label='Piecewise Function')
# plt.ylim(min(durations) - 10, min(y_values) + 10)  # y axis to be able to see interpolated function

# plt.ylim(min(durations) - 10, max(durations) + 10)  # y axis to be able to see data points

plt.scatter(timestamps_unix, durations, color='red', label='Data Points')
plt.xlabel('Time (Unix Timestamp)')
plt.ylabel('Travel Duration (Minutes)')
plt.title('Piecewise Cubic Spline Interpolation')
plt.grid(True)
plt.legend()
plt.show()

plt.savefig('temp.png')