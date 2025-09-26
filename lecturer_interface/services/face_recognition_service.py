# services/face_recognition_service.py
import face_recognition
import numpy as np
import cv2
import threading
import time
from queue import Queue


class CameraRecognizer:
    """
    Runs camera on separate thread, matches faces against known encodings,
    and pushes recognized results + bounding boxes to a queue for GUI consumption.
    """
    def __init__(self, known_encodings, known_rolls, known_names,
                 tolerance=0.5, process_every_n_frames=2):
        self.known_encodings = [np.array(x, dtype=np.float64) for x in known_encodings]
        self.known_rolls = known_rolls
        self.known_names = known_names
        self.tolerance = tolerance
        self.process_every_n_frames = process_every_n_frames

        self.running = False
        self.thread = None
        self.queue = Queue()
        self.recognized_set = set()
        self.capture = None
        self.frame_count = 0

        print(f"[INIT] Loaded {len(self.known_encodings)} known encodings.")

    def start(self, webcam_index=0):
        if self.running:
            return
        self.capture = cv2.VideoCapture(webcam_index, cv2.CAP_DSHOW)
        if not (self.capture and self.capture.isOpened()):
            self.capture = cv2.VideoCapture(webcam_index)
        if not (self.capture and self.capture.isOpened()):
            self.queue.put({"error": "Cannot open webcam."})
            print("[ERROR] Cannot open webcam.")
            return

        print("[INFO] Webcam started successfully.")
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.capture:
            self.capture.release()
            self.capture = None
        print("[INFO] Camera stopped.")

    def _run(self):
        try:
            while self.running and self.capture.isOpened():
                ret, frame = self.capture.read()
                if not ret:
                    print("[WARN] Failed to read frame.")
                    time.sleep(0.02)
                    continue

                self.frame_count += 1
                if self.frame_count % self.process_every_n_frames == 0:
                    self._process_frame(frame)

                time.sleep(0.01)
        except Exception as e:
            self.queue.put({"error": str(e)})
            print(f"[ERROR] Exception in camera thread: {e}")
        finally:
            if self.capture:
                self.capture.release()
            print("[INFO] Camera thread exited.")

    def _process_frame(self, frame):
        print("[DEBUG] Processing frame...")
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small, model="hog")
        print(f"[DEBUG] Detected {len(face_locations)} faces.")

        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
        print(f"[DEBUG] Got {len(face_encodings)} encodings.")

        for (loc, enc) in zip(face_locations, face_encodings):
            label = "Unknown"
            roll, name = None, None

            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, enc)
                best_idx = int(np.argmin(distances))
                best_dist = distances[best_idx]
                print(f"[DEBUG] Best match index {best_idx} with distance {best_dist:.4f}")

                if best_dist <= self.tolerance:
                    roll = self.known_rolls[best_idx]
                    name = self.known_names[best_idx]
                    label = name
                    print(f"[MATCH] Recognized {name} (Roll: {roll})")

                    if roll not in self.recognized_set:
                        self.recognized_set.add(roll)
                        self.queue.put({"roll": roll, "name": name})
                else:
                    print("[DEBUG] No match within tolerance.")
            else:
                print("[WARN] No known encodings loaded.")

            # Always send bounding box info
            self.queue.put({
                "frame_box": {
                    "loc": loc,   # (top, right, bottom, left)
                    "label": label
                }
            })
