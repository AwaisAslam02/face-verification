import streamlit as st
import requests

# Set backend URL
backend_url = "http://13.40.154.15:5000"  # Replace with your backend URL if different

st.title("Facial Recognition System")

# File uploader allows users to upload an image file
uploaded_file = st.file_uploader(
    "Choose an image to upload for registration or verification", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Prepare the file for sending
    files = {'file': uploaded_file}

    # Button to upload and register the face
    if st.button("Upload and Register"):
        with st.spinner("Uploading and registering..."):
            # Send POST request to /register-face endpoint with the image file
            response = requests.post(f"{backend_url}/register-face", files=files)

            if response.status_code == 200:
                st.success("Face registered successfully!")
            else:
                # Display error message from the backend if available
                st.error(response.json().get("error", "Registration failed"))

    # Button to upload and verify the face
    if st.button("Upload and Verify"):
        with st.spinner("Uploading and verifying..."):
            # Send POST request to /verify-face endpoint with the image file
            response = requests.post(f"{backend_url}/verify-face", files=files)

            if response.status_code == 200:
                st.success("Face matched successfully!")
            elif response.status_code == 404:
                st.warning("No matching face found.")
            else:
                # Display error message from the backend if available
                st.error(response.json().get("error", "Verification failed"))
