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
    if len(parts) == 4:
        travel_time = int(parts[0]) * 60 + int(parts[2])
    else:
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

def cubic_interpolate(x0, x, y):
    """ Natural cubic spline interpolate function
        This function is licenced under: Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
        https://creativecommons.org/licenses/by-sa/3.0/
        Author raphael valentin
        Date 25 Mar 2022
    """
    xdiff = np.diff(x)
    dydx = np.diff(y) / np.diff(x)

    n = size = len(x)

    w = np.empty(n-1, float)
    z = np.empty(n, float)

    w[0] = 0.
    z[0] = 0.
    for i in range(1, n-1):
        m = xdiff[i-1] * (2 - w[i-1]) + 2 * xdiff[i]
        w[i] = xdiff[i] / m
        z[i] = (6*(dydx[i] - dydx[i-1]) - xdiff[i-1]*z[i-1]) / m
    z[-1] = 0.

    for i in range(n-2, -1, -1):
        z[i] = z[i] - w[i]*z[i+1]

    # find index (it requires x0 is already sorted)
    index = np.searchsorted(x,x0)
    index = np.clip(index, 1, size-1)  # Clip index values within the range [1, size-1]    

    xi1, xi0 = x[index], x[index-1]
    yi1, yi0 = y[index], y[index-1]
    zi1, zi0 = z[index], z[index-1]
    hi1 = xi1 - xi0

    # calculate cubic
    f0 = zi0/(6*hi1)*(xi1-x0)**3 + \
        zi1/(6*hi1)*(x0-xi0)**3 + \
        (yi1/hi1 - zi1*hi1/6)*(x0-xi0) + \
        (yi0/hi1 - zi0*hi1/6)*(xi1-x0)
    return f0


# Convert timestamps to Unix timestamps (numerical values)
timestamps_unix = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp() for ts in timestamps]

# Generate x values for plotting using Unix timestamps
x_values = np.linspace(min(timestamps_unix), max(timestamps_unix), 400)

# Compute y values using the piecewise function
y_values = [cubic_interpolate(x, timestamps_unix, durations) for x in x_values]


# Plot the piecewise function
plt.plot(x_values, y_values, label='Piecewise Function')

# plt.xlim(50000, 55000)

plt.scatter(timestamps_unix, durations, color='red', label='Data Points')
plt.xlabel('Time (Unix Timestamp)')
plt.ylabel('Travel Duration (Minutes)')
plt.title('Piecewise Cubic Spline Interpolation')
plt.grid(True)
plt.legend()
plt.show()

plt.savefig('temp.png')
