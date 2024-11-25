from flask import Flask, request, jsonify
import boto3
import os
import uuid
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)  

AWS_REGION = "eu-west-2"
BUCKET_NAME = "face-verificationx1"
COLLECTION_ID = "face-collection2"  

# Initialize AWS clients
s3 = boto3.client('s3', region_name=AWS_REGION)
rekognition = boto3.client('rekognition', region_name=AWS_REGION)
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

# Create the face collection if it does not exist
try:
    rekognition.create_collection(CollectionId=COLLECTION_ID)
    print(f"Collection '{COLLECTION_ID}' created successfully.")
except rekognition.exceptions.ResourceAlreadyExistsException:
    print(f"Collection '{COLLECTION_ID}' already exists.")
except Exception as e:
    print(f"Error creating collection: {e}")

def update_index(tableName, faceId, first_name, last_name, occupation, title, age):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FirstName': {'S': first_name},
            'LastName': {'S': last_name},
            'Occupation': {'S': occupation},
            'Title': {'S': title},
            'Age': {'N': str(age)}
        }
    )

def upload_to_s3(file, bucket_name, file_name):
    try:
        s3.upload_fileobj(file, bucket_name, file_name)
        return f"s3://{bucket_name}/{file_name}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

# Flask route to upload images
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.endswith(('.jpg', '.jpeg', '.png')):
        return jsonify({"error": "Invalid file format. Only .jpg, .jpeg, and .png are allowed"}), 400

    try:
        file_name = f"{uuid.uuid4()}.jpg"

        # Upload to S3
        s3_url = upload_to_s3(file, BUCKET_NAME, file_name)
        if not s3_url:
            return jsonify({"error": "Failed to upload image to S3"}), 500

        return jsonify({"message": "File uploaded successfully", "s3_url": s3_url, "file_name": file_name}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500

# Flask route to register a face
@app.route('/register-face', methods=['POST'])
def register_face():
    required_fields = ['file_name', 'first_name', 'last_name', 'occupation', 'title', 'age']
    if not all(field in request.json for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    file_name = request.json['file_name']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    occupation = request.json['occupation']
    title = request.json['title']
    age = request.json['age']

    try:
        response = rekognition.index_faces(
            CollectionId=COLLECTION_ID,
            Image={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': file_name
                }
            },
            DetectionAttributes=['ALL']
        )

        if response['FaceRecords']:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            update_index('face_collection', faceId, first_name, last_name, occupation, title, age)
            return jsonify({"message": "Face registered successfully", "face_id": faceId}), 200
        else:
            return jsonify({"error": "No faces detected in the image"}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while registering the face"}), 500

@app.route('/verify-face-bytes', methods=['POST'])
def verify_face_bytes():
    if 'image_bytes' not in request.json:
        return jsonify({"error": "Image bytes not provided"}), 400

    try:
        # Decode the base64 image bytes
        image_data = base64.b64decode(request.json['image_bytes'])

        response = rekognition.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={
                'Bytes': image_data
            },
            MaxFaces=1,
            FaceMatchThreshold=95 
        )

        if response['FaceMatches']:
            face_id = response['FaceMatches'][0]['Face']['FaceId']
            face = dynamodb.get_item(
                TableName='face_collection',  
                Key={'RekognitionId': {'S': face_id}}
            )
            if 'Item' in face:
                item = face['Item']
                first_name = item.get('FirstName', {}).get('S', '')
                last_name = item.get('LastName', {}).get('S', '')
                occupation = item.get('Occupation', {}).get('S', '')
                title = item.get('Title', {}).get('S', '')
                age = item.get('Age', {}).get('N', '')

                return jsonify({
                    "message": "Face matched",
                    "first_name": first_name,
                    "last_name": last_name,
                    "occupation": occupation,
                    "title": title,
                    "age": age
                }), 200
            else:
                return jsonify({"error": "Face ID not found in database"}), 404
        else:
            return jsonify({"message": "No matching face found"}), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while verifying the face"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
