


import streamlit as st
import requests

# Set backend URL
backend_url = "http://16.171.110.123:5000" 

st.title("Facial Recognition System")
uploaded_file = st.file_uploader("Choose an image to upload for registration or verification", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display image preview
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Upload button
    if st.button("Upload and Register"):
        with st.spinner("Uploading and registering..."):
            files = {'file': uploaded_file}
            response = requests.post(f"{backend_url}/upload", files=files)

            if response.status_code == 200:
                file_name = response.json().get("file_name")
                # Register the face
                register_response = requests.post(f"{backend_url}/register-face", json={"file_name": file_name})
                if register_response.status_code == 200:
                    st.success("Face registered successfully!")
                else:
                    st.error(register_response.json().get("error", "Registration failed"))
            else:
                st.error(response.json().get("error", "Upload failed"))

    # Verify button
    if st.button("Upload and Verify"):
        with st.spinner("Uploading and verifying..."):
            files = {'file': uploaded_file}
            response = requests.post(f"{backend_url}/upload", files=files)

            if response.status_code == 200:
                file_name = response.json().get("file_name")
                # Verify the face
                verify_response = requests.post(f"{backend_url}/verify-face", json={"file_name": file_name})
                if verify_response.status_code == 200:
                    st.success("Face matched successfully!")
                elif verify_response.status_code == 404:
                    st.warning("No matching face found.")
                else:
                    st.error(verify_response.json().get("error", "Verification failed"))
            else:
                st.error(response.json().get("error", "Upload failed"))
