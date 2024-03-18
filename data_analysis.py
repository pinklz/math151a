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
# print(sorted_data)
# Extract x and y coordinates from the data
timestamps = [entry[0] for entry in sorted_data]
durations = [entry[1] for entry in sorted_data]

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

# ----------------------- AVERAGE DATA -----------------------
sum_at_15_minute_interval = [0] * 96
count_at_15_minute_interval = [0] * 96
average_at_15_minute_interval = [0] * 96

for i in range(0,len(durations)):
    duration = durations[i]
    sum_at_15_minute_interval[i % 96] += duration
    count_at_15_minute_interval[i % 96] += 1

for i in range(0,96):
    average_at_15_minute_interval[i] = sum_at_15_minute_interval[i] / count_at_15_minute_interval[i]

# Start time
start_time = datetime.strptime("00:00:00", "%H:%M:%S")

# End time
end_time = datetime.strptime("23:45:00", "%H:%M:%S")

# Initialize a list to store the times
times = []

# Generate times at 15-minute intervals
current_time = start_time
while current_time <= end_time:
    times.append(current_time.strftime("%H:%M:%S"))
    current_time += timedelta(minutes=15)

tick_times = []
current_time = start_time
while current_time <= end_time:
    tick_times.append(current_time.strftime("%H:%M:%S"))
    current_time += timedelta(minutes=60)

times_unix = [datetime.strptime(time_str, "%H:%M:%S").timestamp() for time_str in times]
y_values_avg = [cubic_interpolate(x, times_unix, average_at_15_minute_interval) for x in times_unix]

plt.figure(figsize=(12, 6))
plt.scatter(times, average_at_15_minute_interval, color='g')
plt.plot(times, y_values_avg, label='piecewise', color='b')
plt.xlabel('Time (PST)')
plt.ylabel('Average Travel Time (Minutes)')
plt.title('Average Travel Time from UCLA to LAX at 15-minute Intervals Over 24 Hour Period')
plt.grid(True)
plt.tight_layout()
plt.xticks(tick_times, rotation=45, ha='right')
plt.subplots_adjust(bottom=0.5)
plt.savefig('averagestuff.png')

plt.clf()



from datetime import datetime

def convert_to_unix_time(month, day, time):
    """
    Converts a given month, day, and time into Unix time.

    Args:
    - month: Integer representing the month (1-12).
    - day: Integer representing the day of the month (1-31).
    - time: String representing the time in the format "HH:MM:SS" (24-hour format).

    Returns:
    - The Unix time corresponding to the input date and time.
    """
    # Combine month, day, and time into a single string
    date_time_str = f"{month:02d}-{day:02d} {time}"

    # Parse the date and time string into a datetime object
    date_time_obj = datetime.strptime(date_time_str, "%m-%d %H:%M:%S")

    # Convert the datetime object to Unix time
    unix_time = date_time_obj.timestamp()

    return unix_time

def predict_travel_time(time_of_day):
    """
    Predicts the travel time for a given time of day using cubic spline interpolation on the average travel times.

    Args:
    - time_of_day: String representing the time of day in the format "HH:MM:SS" (24-hour format).

    Returns:
    - The predicted travel time for the given time of day.
    """
    # Convert the time of day to Unix time
    time_unix = convert_to_unix_time(1, 1, time_of_day)  # Using January 1st as a dummy date

    # Predict the travel time using cubic spline interpolation
    predicted_time = cubic_interpolate(time_unix, times_unix, y_values_avg)

    return predicted_time

# Allow input for predicted travel time, while ensuring it's in the right format
while True:
    tt = input("Input time for estimated travel time from UCLA to LAX (In the form: 'HH:MM:SS') -  ")

    time_parts = tt.split(':')  # Separate hours, minutes, + seconds
    if len(time_parts) == 3:
        hour, minute, second = time_parts
        # Check if each are integers
        if hour.isdigit() and minute.isdigit() and second.isdigit():
            # Check for valid time format
            if 0 <= int(hour) < 24 and 0 <= int(minute) < 60 and 0 <= int(second) < 60:
                break
        print("Invalid time - please enter the time in the format HH:MM:SS.")
ptt = predict_travel_time(tt)

hours = int(ptt/60)
mins = int((ptt - (60*hours))%60)
tempsecs = ((ptt -(60*hours) - mins) * 60) 
secs = int(tempsecs*10)/10

if hours > 0:
    print("Predicted travel time: ", hours, " hours, ", mins, " minutes and ", secs, " seconds")
else: 
    print("Predicted travel time: ", mins, " minutes and ", secs, " seconds")

# ----------------------- ALL DATA -----------------------

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
plt.scatter(datetime_objects, durations, color = 'r')
plt.xlabel('Time (PST)')
plt.ylabel('Travel Time UCLA to LAX')
plt.title('Data with Timestamps and Durations')
plt.subplots_adjust(bottom=0.5)
plt.xticks(ticks, [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in ticks], rotation=45, ha='right')
# Display the plot
plt.savefig('plot.png')

plt.clf()


# ----------------------- INTERPOLATED DATA -----------------------

# Function to convert Unix timestamp to datetime object in PST timezone
def unix_to_pst(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).astimezone(timezone(timedelta(hours=-8)))

# Convert timestamps to Unix timestamps (numerical values)
timestamps_unix = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp() for ts in timestamps]

# Generate x values for plotting using Unix timestamps
x_values = np.linspace(min(timestamps_unix), max(timestamps_unix), 400)

# Compute y values using the piecewise function
y_values = [cubic_interpolate(x, timestamps_unix, durations) for x in x_values]

# Convert x values (Unix timestamps) to datetime objects in PST timezone
x_values_pst = [unix_to_pst(x) for x in x_values]

# Plot the piecewise function
plt.plot(x_values_pst, y_values, label='Piecewise Function')

# Plot the data points
timestamps_pst = [unix_to_pst(ts) for ts in timestamps_unix]
plt.scatter(timestamps_pst, durations, color='red', label='Data Points')

plt.xlabel('Time (PST)')
plt.ylabel('Travel Duration (Minutes)')
plt.xticks(ticks, [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in ticks], rotation=45, ha='right')
plt.title('Piecewise Cubic Spline Interpolation')
plt.grid(True)
plt.legend()
plt.show()

plt.savefig('cubic.png')
