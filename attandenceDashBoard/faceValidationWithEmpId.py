# from django.contrib.auth import get_user_model
# import numpy as np
# # import face_recognition as fr

# from attandenceDashBoard.models import StoreFaces, EmployeeRegistration

# class FaceAuthentication:
#     @staticmethod
#     def get_encoded_faces1(empId):
#         """
#         This function loads all user profile images (front, left, right)
#         and encodes their faces.
#         """
#         try:
#             emp = EmployeeRegistration.objects.filter(empId=empId).first()
#             if not emp:
#                 return None

#             qs = StoreFaces.objects.filter(emp=emp).first()
#             if not qs:
#                 return None

#             encoded = {}  # Dictionary to store multiple encodings per person
#             encodings = []  # List to store multiple encodings for a person

#             for img_path in [qs.front, qs.left, qs.right]:
#                 if img_path:  # Ensure the path is not None
#                     try:
#                         face = fr.load_image_file(img_path)
#                         face_encodings = fr.face_encodings(face)

#                         if face_encodings:
#                             encodings.append(face_encodings[0])  # Store the encoding
#                         else:
#                             print(f"No face found in image: {img_path}")
#                     except Exception as e:
#                         print(f"Error loading image {img_path}: {e}")

#             if encodings:  # Only store if we have at least one encoding
#                 encoded[qs.emp.empId] = encodings

#             return encoded
#         except Exception as e:
#             print(f"Unexpected error in get_encoded_faces1: {e}")
#             return None

#     @staticmethod
#     def classify_face3(img, empId):
#         """
#         This function takes an image as input, compares it to stored encodings,
#         and returns the person with the highest match percentage.
#         """
#         try:
#             faces = FaceAuthentication.get_encoded_faces1(empId)
#             if not faces:
#                 return None

#             known_faces = list(faces.keys())  # List of names
#             faces_encoded = list(faces.values())  # List of encoded faces (each is a list)

#             img = fr.load_image_file(img)
#             face_locations = fr.face_locations(img)
#             unknown_face_encodings = fr.face_encodings(img, face_locations)

#             best_match_name = None
#             best_match_score = 0  # Initialize match percentage

#             match_results = []

#             for face_encoding in unknown_face_encodings:
#                 for i, known_encodings in enumerate(faces_encoded):
#                     matches = fr.compare_faces(known_encodings, face_encoding)
#                     face_distances = fr.face_distance(known_encodings, face_encoding)

#                     if any(matches):  # If there's at least one match
#                         min_distance = min(face_distances)
#                         match_score = (1 - min_distance) * 100  # Convert to percentage

#                         try:
#                             employee = EmployeeRegistration.objects.get(empId=known_faces[i])
#                             match_results.append({
#                                 "empId": known_faces[i],
#                                 "name": employee.name,
#                                 "match_percentage": round(match_score, 2)
#                             })
#                         except EmployeeRegistration.DoesNotExist:
#                             print(f"Employee with empId {known_faces[i]} not found.")

#             if match_results:
#                 best_match = max(match_results, key=lambda x: x["match_percentage"])
#                 best_match_name = best_match["name"]
#                 best_match_score = best_match["match_percentage"]
#                 best_match_empId = best_match["empId"]

#             print(match_results)
#             if best_match_score >= 60:
#                 return {"name": best_match_name, "match_percentage": best_match_score, 'empId':best_match_empId}
#             else :
#                 return None
        
#         except Exception as e:
#             print(f"Unexpected error in classify_face3: {e}")
#             return {"name": None, "match_percentage": 0, "all_matches": []}