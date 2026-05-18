import cv2
import dlib
import face_recognition_models
import numpy as np

# =========================
# LOAD MODEL ONLY ONE TIME
# =========================

# detector = dlib.cnn_face_detection_model_v1(
#     'models/mmod_human_face_detector.dat'
# )

detector = dlib.get_frontal_face_detector()

sp = dlib.shape_predictor(
    face_recognition_models.pose_predictor_model_location()
)

facerec = dlib.face_recognition_model_v1(
    face_recognition_models.face_recognition_model_location()
)

# =========================
# FACE DETECTION FUNCTION
# =========================

def detect_face(frame, compute_embeddings=True):

    # Convert BGR -> RGB for dlib
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Detect faces (0 upsamples for speed, use 1 or more for smaller faces)
    faces = detector(rgb, 0)

    print("Total faces :-", len(faces))

    face_embeddings = []
    face_boxes = []

    for i, face in enumerate(faces, start=1):

        if hasattr(face, "rect"):
            rect = face.rect
        else:
            rect = face
            
        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        print(f"Face corrdination:-{i}")
        print("Left Top:-",left , top)
        print("Left Bottom:-",left,bottom)
        print("Right Top:-",right,top)
        print("Right Bottom:-",right,bottom)

        face_boxes.append((left, top, right, bottom))
        
        if compute_embeddings:
            shape = sp(frame,face)  
            face_description = facerec.compute_face_descriptor(frame,shape,1) # 128 vector embedding return

            embedding = list(face_description)
            face_embeddings.append(embedding)

        # Draw rectangle
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

        # DON'T draw face label here so we can optionally draw custom ones in app.py
        # Or you can choose to draw them if no matches found. For now, we will draw custom labels
        # outside this function.
    
    h, w = frame.shape[:2]

    cv2.putText(
        frame,
        f"Total Faces: {len(faces)}",
        (20, 40),   # always visible
        cv2.FONT_HERSHEY_SIMPLEX,
        min(w, h) / 750,   # dynamic font size
        (0, 254, 255),
        2
    )


    return frame , face_embeddings, face_boxes


