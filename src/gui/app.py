import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import threading
from PIL import Image
import numpy as np
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from modules.pipeline.face_detect import detect_face
from database.operation.basic_oper import get_all_face_data
from database.operation.image_store import insert_new_user


class FaceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection & Registration System")
        self.root.geometry("600x400")
        self.root.configure(bg="#f4f4f4")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.source_type = tk.StringVar(value="CAMERA")
        self.file_path = tk.StringVar(value="")
        self.is_running = False
        
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(
            self.root, 
            text="Face Detection System", 
            font=("Helvetica", 18, "bold"),
            bg="#f4f4f4"
        )
        title.pack(pady=20)
        
        # Options Frame
        opt_frame = ttk.LabelFrame(self.root, text="Input Source Options")
        opt_frame.pack(fill="x", padx=40, pady=10)
        
        cam_rb = ttk.Radiobutton(
            opt_frame, 
            text="Camera (Webcam)", 
            variable=self.source_type, 
            value="CAMERA",
            command=self.toggle_file_btn
        )
        cam_rb.pack(anchor="w", padx=20, pady=5)
        
        vid_rb = ttk.Radiobutton(
            opt_frame, 
            text="Video Upload", 
            variable=self.source_type, 
            value="VIDEO",
            command=self.toggle_file_btn
        )
        vid_rb.pack(anchor="w", padx=20, pady=5)
        
        img_rb = ttk.Radiobutton(
            opt_frame, 
            text="Image Upload (Registration)", 
            variable=self.source_type, 
            value="IMAGE",
            command=self.toggle_file_btn
        )
        img_rb.pack(anchor="w", padx=20, pady=5)

        # File selection frame
        self.file_frame = tk.Frame(self.root, bg="#f4f4f4")
        self.file_frame.pack(fill="x", padx=40, pady=10)
        
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, state='readonly', width=45)
        self.file_entry.pack(side="left", padx=(0,10))
        
        self.browse_btn = ttk.Button(self.file_frame, text="Browse", command=self.browse_file, state=tk.DISABLED)
        self.browse_btn.pack(side="left")
        
        # Action Frame
        action_frame = tk.Frame(self.root, bg="#f4f4f4")
        action_frame.pack(fill="x", padx=40, pady=20)
        
        self.start_btn = ttk.Button(action_frame, text="Start Detection", command=self.start_process)
        self.start_btn.pack(side="right", padx=10)
        
        self.status_label = tk.Label(self.root, text="Ready", bg="#f4f4f4", fg="#555")
        self.status_label.pack(side="bottom", pady=10)

    def toggle_file_btn(self):
        if self.source_type.get() in ["VIDEO", "IMAGE"]:
            self.browse_btn.config(state=tk.NORMAL)
        else:
            self.browse_btn.config(state=tk.DISABLED)
            self.file_path.set("")

    def browse_file(self):
        filetypes = []
        if self.source_type.get() == "VIDEO":
            filetypes = [("Video Files", "*.mp4 *.avi *.mkv *.mov")]
        elif self.source_type.get() == "IMAGE":
            filetypes = [("Image Files", "*.jpg *.jpeg *.png")]
            
        path = filedialog.askopenfilename(title="Select File", filetypes=filetypes)
        if path:
            self.file_path.set(path)

    def start_process(self):
        if self.is_running:
            return
            
        src = self.source_type.get()
        path = self.file_path.get()
        
        if src in ["VIDEO", "IMAGE"] and not path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Running...")
        
        # Run logic in separate thread to prevent GUI freezing
        threading.Thread(target=self.run_detection, args=(src, path), daemon=True).start()

    def run_detection(self, src_type, path):
        try:
            if src_type == "CAMERA":
                self.process_video(0)
            elif src_type == "VIDEO":
                self.process_video(path)
            elif src_type == "IMAGE":
                self.process_image(path)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.is_running = False
            self.root.after(0, self.start_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.status_label.config, {"text": "Ready"})

    def process_video(self, source):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            self.root.after(0, messagebox.showerror, "Error", "Cannot access video source.")
            return

        cv2.namedWindow("Live Face Detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Live Face Detection", 800, 600)

        while cap.isOpened() and self.is_running:
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

            cv2.imshow("Live Face Detection", output)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def process_image(self, image_path):
        try:
            img_pil = Image.open(image_path)
            image_np = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Failed to load image: {e}")
            return
            
        frame, embeddings, face_boxes = detect_face(image_np)
        
        if len(embeddings) == 0:
            self.root.after(0, messagebox.showinfo, "Result", "No face detected in the image.")
            return
            
        self.root.after(0, self.status_label.config, {"text": "Checking Database..."})
        
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
            self.root.after(0, self.status_label.config, {"text": "All Faces Verified"})
            self.root.after(0, self.show_registered_face, frame_rgb, "All Faces Verified")
            return
            
        if len(embeddings) > 1:
            self.root.after(0, self.show_registered_face, frame_rgb, "Unknown Faces Found")
            self.root.after(0, messagebox.showwarning, "Registration Blocked", "Multiple faces detected. For a new registration, please upload a photo with exactly ONE face.")
            return

        # If new single face, process registration
        os.makedirs("src/detected_image", exist_ok=True)
        cv2.imwrite("src/detected_image/detect.jpg", frame)
        
        self.root.after(0, self.prompt_registration, frame, first_unknown_embedding)

    def prompt_registration(self, frame, embedding):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Display via matplotlib like before or custom top level
        plt.figure(figsize=(8, 5))
        plt.imshow(frame_rgb)
        plt.axis("off")
        plt.title("Detected Face - New User")
        plt.show(block=False)
        
        # Ask user right away
        res = messagebox.askyesno("Register", "Face detected. Is the quality good enough to register?")
        plt.close()
        
        if res:
            name = tk.simpledialog.askstring("Name", "Enter user name to register:", parent=self.root)
            if name:
                insert_result = insert_new_user([embedding], name)
                if insert_result:
                    messagebox.showinfo("Success", f"User '{name}' registered successfully.")
                else:
                    messagebox.showerror("Error", "Failed to register user.")
            else:
                messagebox.showwarning("Cancelled", "Registration cancelled (no name provided).")
        else:
            messagebox.showinfo("Info", "Please upload a better quality image.")

    def show_registered_face(self, frame_rgb, matched_name):
        plt.figure(figsize=(8, 5))
        plt.imshow(frame_rgb)
        plt.axis("off")
        plt.title(f"Already Registered: {matched_name}")
        plt.show(block=False)
        messagebox.showinfo("Match Found", f"This face is already registered as '{matched_name}'.")

def main():
    root = tk.Tk()
    app = FaceDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
