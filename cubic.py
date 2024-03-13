from firebase_admin import credentials, firestore, initialize_app
import numpy as np
import matplotlib.pyplot as plt

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/serviceAccountKey.json")
initialize_app(cred)

# Initialize Firestore database
db = firestore.client()

# Function to retrieve traffic data from Firestore
def retrieve_traffic_data():
    traffic_data = []
    # Assuming 'traffic_collection' is the name of the collection in Firestore
    docs = db.collection('traffic_collection').stream()
    for doc in docs:
        data = doc.to_dict()
        traffic_data.append((data['time'], data['travel_duration']))
    return traffic_data

# Retrieve traffic data from Firestore
traffic_data = retrieve_traffic_data()

# Sort the data points by time
traffic_data.sort(key=lambda x: x[0])

# Extract time and travel duration from the sorted data
times = [data[0] for data in traffic_data]
travel_durations = [data[1] for data in traffic_data]

# Convert time and travel duration to numpy arrays for interpolation
times_np = np.array(times)
travel_durations_np = np.array(travel_durations)

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
    return interpolated_value

# Generate x values for plotting
x_values = np.linspace(min(times), max(times), 400)

# Compute y values using the piecewise function
y_values = [cubic_spline_interpolation(x, times_np, travel_durations_np) for x in x_values]

# Plot the piecewise function
plt.plot(x_values, y_values, label='Piecewise Function')
plt.scatter(times, travel_durations, color='red', label='Data Points')
plt.xlabel('Time')
plt.ylabel('Travel Duration')
plt.title('Piecewise Cubic Spline Interpolation')
plt.grid(True)
plt.legend()
plt.show()
