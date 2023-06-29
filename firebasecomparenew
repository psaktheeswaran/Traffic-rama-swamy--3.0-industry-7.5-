import firebase_admin
from firebase_admin import credentials, db

# Firebase Service Account Details
firebase_credentials = '<PATH_TO_FIREBASE_CREDENTIALS_JSON>'
firebase_node = '<FIREBASE_NODE_NAME>'

# Set up Firebase credentials
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {'databaseURL': 'https://<YOUR_FIREBASE_PROJECT_ID>.firebaseio.com/'})
firebase_db = db.reference()

# Function to write data to Firebase
def write_data_to_firebase(image_file, data):
    firebase_db.child(firebase_node).child(image_file).set(data)

# Main code
image_file = 'image1.jpg'
data = 'Data to be shared'
write_data_to_firebase(image_file, data)


import firebase_admin
from firebase_admin import credentials, db

# Firebase Service Account Details
firebase_credentials = '<PATH_TO_FIREBASE_CREDENTIALS_JSON>'
firebase_node = '<FIREBASE_NODE_NAME>'

# Set up Firebase credentials
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {'databaseURL': 'https://<YOUR_FIREBASE_PROJECT_ID>.firebaseio.com/'})
firebase_db = db.reference()

# Function to listen for data changes in Firebase
def listen_for_data_changes(event):
    if event.event_type == 'child_added':
        image_file = event.path.split('/')[-1]
        data = event.data
        print(f"New data received for image '{image_file}': {data}")

# Main code
firebase_db.child(firebase_node).listen(listen_for_data_changes)



Ensure that you replace the placeholder values (<PATH_TO_FIREBASE_CREDENTIALS_JSON>, <FIREBASE_NODE_NAME>, <YOUR_FIREBASE_PROJECT_ID>) with the appropriate values for your Firebase project.

Instance 1 is responsible for writing the data to the specified Firebase node. In this example, the data being shared is a simple string, but you can modify it to suit your needs.

Instance 2 listens for data changes in the same Firebase node and prints the new data whenever a new child is added to the node.

By running both instances simultaneously, you can establish communication between them through the Firebase Realtime Database, and any new data written by Instance 1 will be received and processed by Instance 2.

Remember to install the firebase_admin package using pip before running the code.

Feel free to modify the code as needed to fit your requirements and expand on the data structures and communication between the instances.
