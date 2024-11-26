import streamlit as st
import requests
import base64
import pandas as pd

# Set backend URL
backend_url = "http://13.40.154.15:5000"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

# Functions to switch pages
def go_home():
    st.session_state['page'] = 'home'

def go_register():
    st.session_state['page'] = 'register'

def go_verify():
    st.session_state['page'] = 'verify'

# Main app logic
if st.session_state['page'] == 'home':
    st.title("Face Verification")
    st.write("Please select an option below:")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Register a Person", on_click=go_register, key='register_button')
    with col2:
        st.button("Verify/Search Face", on_click=go_verify, key='verify_button')

elif st.session_state['page'] == 'register':
    st.title("Register a Person")
    st.button("Home", on_click=go_home, key='register_home_button')
    uploaded_file = st.file_uploader("Choose an image to upload for registration", type=["jpg", "jpeg", "png"], key='register_upload')

    if uploaded_file:
        # Display image preview
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Collect additional details
    first_name = st.text_input("Enter the first name", "", key='register_first_name')
    last_name = st.text_input("Enter the last name", "", key='register_last_name')
    occupation = st.text_input("Enter the occupation", "", key='register_occupation')
    title = st.text_input("Enter the title", "", key='register_title')
    age = st.number_input("Enter the age", min_value=0, max_value=120, step=1, key='register_age')

    # Registration Button
    if st.button("Upload and Register", key='upload_register_button'):
        if not uploaded_file:
            st.error("Please upload an image before registering.")
        elif not first_name.strip():
            st.error("Please enter first name.")
        elif not last_name.strip():
            st.error("Please enter last name.")
        elif not occupation.strip():
            st.error("Please enter occupation.")
        elif not title.strip():
            st.error("Please enter title.")
        elif age <= 0:
            st.error("Please enter a valid age.")
        else:
            with st.spinner("Uploading and registering..."):
                files = {'file': uploaded_file}
                response = requests.post(f"{backend_url}/upload", files=files)

                if response.status_code == 200:
                    file_name = response.json().get("file_name")
                    # Register the face
                    register_payload = {
                        "file_name": file_name,
                        "first_name": first_name,
                        "last_name": last_name,
                        "occupation": occupation,
                        "title": title,
                        "age": age
                    }
                    register_response = requests.post(f"{backend_url}/register-face", json=register_payload)
                    if register_response.status_code == 200:
                        st.success("Face registered successfully!")
                    else:
                        st.error(register_response.json().get("error", "Registration failed"))
                else:
                    st.error(response.json().get("error", "Upload failed"))

elif st.session_state['page'] == 'verify':
    st.title("Verify/Search Face")
    st.button("Home", on_click=go_home, key='verify_home_button')
    uploaded_file = st.file_uploader("Choose an image to upload for verification", type=["jpg", "jpeg", "png"], key='verify_upload')

    if uploaded_file:
        # Display image preview
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Verification Button
    if st.button("Verify Face", key='verify_face_button'):
        if not uploaded_file:
            st.error("Please upload an image before verification.")
        else:
            with st.spinner("Verifying..."):
                # Read image bytes
                image_bytes = uploaded_file.read()
                # Encode image bytes to base64 to send in JSON
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')

                verify_payload = {"image_bytes": encoded_image}
                verify_response = requests.post(f"{backend_url}/verify-face-bytes", json=verify_payload)

                if verify_response.status_code == 200:
                    data = verify_response.json()
                    first_name = data.get("first_name", "")
                    last_name = data.get("last_name", "")
                    occupation = data.get("occupation", "")
                    title = data.get("title", "")
                    age = data.get("age", "")

                    st.success("Face matched successfully!")
                    # Display the details in a table
                    data_dict = {
                        "First Name": [first_name],
                        "Last Name": [last_name],
                        "Occupation": [occupation],
                        "Title": [title],
                        "Age": [age]
                    }
                    df = pd.DataFrame(data_dict)
                    st.table(df)
                elif verify_response.status_code == 404:
                    st.warning("No matching face found.")
                else:
                    st.error(verify_response.json().get("error", "Verification failed"))
