import streamlit as st
import requests
import base64

# Set backend URL
backend_url = "http://13.40.154.15:5000" 

st.title("Facial Recognition System")
uploaded_file = st.file_uploader("Choose an image to upload for registration or verification", type=["jpg", "jpeg", "png"])


if uploaded_file:
    # Display image preview
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    name = st.text_input("Enter the name of the person to register", "")
    
    # Registration Button
    if st.button("Upload and Register"):
        if not name.strip():  # Check if the name field is empty
            st.error("Please enter a name before registering.")
        else:
            with st.spinner("Uploading and registering..."):
                files = {'file': uploaded_file}
                response = requests.post(f"{backend_url}/upload", files=files)

                if response.status_code == 200:
                    file_name = response.json().get("file_name")
                    # Register the face
                    register_payload = {"file_name": file_name, "name": name}
                    register_response = requests.post(f"{backend_url}/register-face", json=register_payload)
                    if register_response.status_code == 200:
                        st.success("Face registered successfully!")
                    else:
                        st.error(register_response.json().get("error", "Registration failed"))
                else:
                    st.error(response.json().get("error", "Upload failed"))
    
    # Verification Button
    if st.button("Verify Face"):
        with st.spinner("Verifying..."):
            # Read image bytes
            image_bytes = uploaded_file.read()
            # Encode image bytes to base64 to send in JSON
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            
            verify_payload = {"image_bytes": encoded_image}
            verify_response = requests.post(f"{backend_url}/verify-face-bytes", json=verify_payload)

            if verify_response.status_code == 200:
                matched_name = verify_response.json().get("face_id", "Unknown")
                st.success(f"Face matched successfully! Name: {matched_name}")
            elif verify_response.status_code == 404:
                st.warning("No matching face found.")
            else:
                st.error(verify_response.json().get("error", "Verification failed"))
