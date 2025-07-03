import numpy as np
from .models import StoreFaces
import face_recognition as fr
import cv2 as cv
class serv:
    
    target_image = None
    target_encoding = None
    def getallFaces():
        listOfFaces = StoreFaces.objects.all()
        encoded = {}
        for faces in listOfFaces:
            imgload = fr.load_image_file(faces.front)
            face_encodings = fr.face_encodings(imgload)
            encoding = None  # Initialize encoding to None
            if face_encodings:
                encoding = face_encodings[0]
            else:
                print("No face found in the image")
            if encoding is not None:
                encoded[faces.emp.name] = encoding

#----------------------------------------------------------------2nd time 
            imgload = fr.load_image_file(faces.left)
            face_encodings = fr.face_encodings(imgload)
            encoding = None  # Initialize encoding to None
            if face_encodings:
                encoding = face_encodings[0]
            else:
                print("No face found in the image")
            if encoding is not None:
                encoded[faces.emp.name] = encoding

#----------------------------------------------------------------3nd time 
            imgload = fr.load_image_file(faces.right)
            face_encodings = fr.face_encodings(imgload)
            encoding = None  # Initialize encoding to None
            if face_encodings:
                encoding = face_encodings[0]
            else:
                print("No face found in the image")
            if encoding is not None:
                encoded[faces.emp.name] = encoding
        
        return encoded  # Dedent this line



    def classify_face(img):
        image = fr.load_image_file(img)

        face_location = fr.face_locations(image)
        serv.target_encoding = fr.face_encodings(image,face_location) 
        faces = serv.getallFaces()
        faces_encoded = list(faces.values())
        known_face = list(faces.keys())
        names=[]
        
        for encoding in serv.target_encoding:
                # Compare the encoding of the current face to the encodings of all known faces
                matches = fr.compare_faces(encoding, faces_encoded)

                # Find the known face with the closest encoding to the current face
                face_distances = fr.face_distance(encoding, faces_encoded)
                best_match_index = np.argmin(face_distances)

                # If the closest known face is a match for the current face, label the face with the known name
                if matches[best_match_index]:
                    names.append( known_face[best_match_index])
                    
                else: 
                     names.append(None)    
        return names
              
            
            
           
    