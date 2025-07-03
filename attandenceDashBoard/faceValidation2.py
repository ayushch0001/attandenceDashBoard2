import os
from PIL import Image
import cv2
from deepface import DeepFace
from django.contrib.auth import get_user_model
import numpy as np
from attandenceDashBoard.models import StoreFaces ,EmployeeRegistration


User = get_user_model()

class ImageAuthenticationBackend:
 
    
    def read_uploaded_image(uploaded_file):
        # Read the file bytes
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        # Decode into an OpenCV image
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img
    
    
    def authenticate(profile_picture,empId):
        try:
            emp = EmployeeRegistration.objects.filter(empId=empId).first()
            if not emp:
                return None
            custom_threshold = 0.40
            qs = StoreFaces.objects.filter(emp=emp)
            print(qs)
            if not qs:
                return None

            stored_Results = []
            for p in qs:
                for img_path in [p.front, p.left, p.right]:  
                    print(img_path.path, profile_picture)
                    pathV = img_path.path.replace("\\", "/")
                    profile_picture = profile_picture.replace("\\", "/")
                    result = DeepFace.verify(
                        img1_path=pathV,
                        img2_path=profile_picture,
                        model_name="ArcFace",        # Use ArcFace model
                        enforce_detection=True,      # Ensure face detection is enforced for accuracy
                        align=True,                  # Keeps face alignment for better accuracy
                        normalization="base",        # Default normalization for ArcFace
                        distance_metric="cosine",    # Use cosine distance metric for ArcFace
                        threshold=0.40,              # Set ArcFace-specific threshold for better matching
                        detector_backend="mtcnn"     # Use MTCNN for more accurate face detection
                    )
                      # default is 0.68 for ArcFace

                    if result['distance'] < custom_threshold:
                        print("✅ Match (custom threshold): Faces are the same person.")
                        stored_Results.append(result['distance'])
                    else:
                        print("❌ No Match (custom threshold): Faces are different.")
                        
            print(stored_Results)
            if len(stored_Results) > 0:
                avg_distance = np.mean(stored_Results)
                if avg_distance < custom_threshold:
                    print("✅ Match (custom threshold): Faces are the same person.")
                    return emp.name
                else:
                    print("❌ No Match (custom threshold): Faces are different.")
                    return None
            
        except User.DoesNotExist:
            return None

 
        



   