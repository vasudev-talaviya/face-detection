import cv2
from PIL import Image
import numpy as np

import matplotlib
matplotlib.use('TkAgg')

import os

import matplotlib.pyplot as plt


from modules.pipeline.face_detect import detect_face
from modules.command.CLI import cmd

# database
from database.operation.basic_oper import get_all_face_data
from database.operation.image_store import insert_new_user



if __name__ == '__main__':

    try:
        DEFAULT_TEST, IMAGE_PATH = cmd()
    except SystemExit:
        # argparse throws SystemExit on -h/--help or invalid args
        # But if we just run it without args, it works and returns None, None
        pass

    # If no CLI arguments provided, launch the GUI
    if DEFAULT_TEST is None:
        print("[*] No CLI arguments provided, launching GUI...")
        from src.gui.app import main as run_gui
        run_gui()
        exit()

    if DEFAULT_TEST == 2 and not IMAGE_PATH:
        print("Please provide image path using --image")
        exit()

    match DEFAULT_TEST:

        # =========================
        # WEBCAM TEST
        # =========================
        case 1:

            cap = cv2.VideoCapture(0)  # Changed from hardcoded "walk.mp4" to standard 0

            if not cap.isOpened():
                print("Cannot access camera")
                exit()

            # Create a resizable window and set its display size.
            cv2.namedWindow("Live Face Detection", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Live Face Detection", 800, 600)

            while cap.isOpened():

                ret, frame = cap.read()

                if not ret:
                    break

                output, face_embeddings, face_boxes = detect_face(frame, compute_embeddings=True)

                for embedding, box in zip(face_embeddings, face_boxes):
                    left, top, right, bottom = box
                    is_new_face, matched_name, confidence = get_all_face_data([embedding])
                    
                    if is_new_face:
                        continue # Do not show 'Unknown' text in video mode
                    else:
                        text = f"{matched_name} ({confidence:.1f}%)"
                        color = (0, 255, 0)
                    
                    y = max(top - 10, 20)
                    (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)
                    cv2.rectangle(output, (left, y - text_h - 5), (left + text_w + 5, y + baseline + 5), (0, 0, 0), -1)
                    cv2.putText(output, text, (left + 2, y), cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 1)

                # Show image
                cv2.imshow(
                    "Live Face Detection",
                    output
                )

                # Press q to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        # =========================
        # IMAGE TEST
        # =========================
        case 2:

            # Read image using PIL
            image_path = Image.open(IMAGE_PATH)

            # Convert PIL -> OpenCV BGR
            image_np = cv2.cvtColor(
                np.array(image_path),
                cv2.COLOR_RGB2BGR
            )

            # Detect face
            frame , embeddings, face_boxes = detect_face(image_np)
           
            if len(embeddings) == 0:
                print("Face not detect")
                exit()

            # ═══════════════════════════════════════════
            # EARLY CHECKPOINT: Check if face already exists in DB
            # ═══════════════════════════════════════════
            print("\n[*] Checking faces against database...")
            
            all_known = True
            first_unknown_embedding = None

            for embedding, box in zip(embeddings, face_boxes):
                is_new_face, matched_name, confidence = get_all_face_data([embedding])
                left, top, right, bottom = box

                if is_new_face:
                    all_known = False
                    if first_unknown_embedding is None:
                        first_unknown_embedding = embedding
                    text = "Unknown"
                    color = (0, 0, 255)
                else:
                    text = f"{matched_name} ({confidence:.1f}%)"
                    color = (0, 255, 0)
                    
                y = max(top - 10, 20)
                (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)
                cv2.rectangle(frame, (left, y - text_h - 5), (left + text_w + 5, y + baseline + 5), (0, 0, 0), -1)
                cv2.putText(frame, text, (left + 2, y), cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 1)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            if all_known:
                print(f"\n[!] All faces are already registered.")
                plt.figure(figsize=(8, 5))
                plt.imshow(frame_rgb)
                plt.axis("off")
                plt.title("All Faces Verified")
                plt.show()
                print("No need to register again. Exiting...")
                exit()
                
            if len(embeddings) > 1:
                print("\n[!] Unknown faces detected in a multi-face image.")
                print("For registration, a single face photo is mandatory.")
                plt.figure(figsize=(8, 5))
                plt.imshow(frame_rgb)
                plt.axis("off")
                plt.title("Multiple Faces (Registration Blocked)")
                plt.show()
                exit()

            print("[+] New face detected! Proceeding with registration...\n")

            import os
            os.makedirs('src/detected_image', exist_ok=True)
            STORE_PATH = 'src/detected_image/detect.jpg'

            # Store a image in device.
            cv2.imwrite(
                STORE_PATH,
                frame
            )

            print("Image saved as detect.jpg")

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            plt.figure(figsize=(8, 5))
            plt.imshow(frame_rgb)
            plt.axis("off")
            plt.title("Detected Face")
            plt.show()

            print("Your face detect if yes 1 press if not 0 press carefully press")

            option = int(input("Press key either 1 or 0:- "))

            if option in [0,1]:
                if option == 0:
                    print("Could you please good quilty image upload")
                elif option == 1:
                    
                    name = input("Great.. Please entering your name to identify :- ")

                    if not name:
                        print("Please enter the name if not enter the name next process not work")
                        exit()
                    
                    # Face already verified as new — directly insert using first_unknown_embedding
                    insert_result = insert_new_user([first_unknown_embedding], name)
                    
                    if insert_result:
                        exit()

            else:
                print("Again try because you wrong option enter")