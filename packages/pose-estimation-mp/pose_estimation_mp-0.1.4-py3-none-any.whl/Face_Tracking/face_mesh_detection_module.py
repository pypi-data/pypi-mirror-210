import os
import time
import argparse
import cv2 as cv
import mediapipe as mp

class FaceDetect:
    def __init__(self, static_image=False, max_faces=1, refine=False, detect_conf=0.5, track_conf=0.5):
        self.draw_utils = mp.solutions.drawing_utils
        self.draw_spec = self.draw_utils.DrawingSpec(color=[0, 255, 0], thickness=1, circle_radius=2)
        self.mp_face_track = mp.solutions.face_mesh
        self.face_track = self.mp_face_track.FaceMesh(static_image, max_faces, refine, detect_conf, track_conf)
    
    def detect_mesh(self, img, disp=True):
        results = self.face_track.process(img)
        detected_landmarks = results.multi_face_landmarks

        if detected_landmarks:
            if disp:
                for f_landmarks in detected_landmarks:
                    self.draw_utils.draw_landmarks(img, f_landmarks, self.mp_face_track.FACEMESH_CONTOURS, self.draw_spec, self.draw_spec)
            
        return detected_landmarks, img
    
    def get_info(self, detected_landmarks, img_dims):
        landmarks_info = []
        img_height, img_width = img_dims
        for _, face in enumerate(detected_landmarks):
            mesh_info = []
            for id, landmarks in enumerate(face.landmark):
                x, y = int(landmarks.x * img_width), int(landmarks.y * img_height)
                mesh_info.append((id, x, y))
            landmarks_info.append(mesh_info)

        return landmarks_info

def main(path, is_image=True):
    print(path)
    if is_image:
        detector = FaceDetect()
        ori_img = cv.imread(path)
        img = ori_img.copy()
        landmarks, output = detector.detect_mesh(img)
        if landmarks:
            mesh_info = detector.get_info(landmarks, img.shape[:2])
            # print(mesh_info)

        cv.imshow("Result", output)
        cv.waitKey(0)

    else:
        detector = FaceDetect(static_image=False)
        cap = cv.VideoCapture(path)
        curr_time = 0
        prev_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Video Over")
                break

            img = frame.copy()
            landmarks, output = detector.detect_mesh(img)
            if landmarks:
                mesh_info = detector.get_info(landmarks, img.shape[:2])
                # print(len(mesh_info))

            curr_time = time.time()
            fps = 1/(curr_time - prev_time)
            prev_time = curr_time
            cv.putText(output, f'FPS: {str(int(fps))}', (10, 70), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 50, 170), 2)

            cv.imshow("Result", output)
            if cv.waitKey(20) & 0xFF == ord('q'):
                break

        cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Type of media and path to it")
    parser.add_argument("-p", "--path", default="Data\\Images\\human_3.jpg", help="Path to media from current working directory")
    parser.add_argument("-v", "--video", action="store_false", help="Tells the program that media is video")

    args = parser.parse_args()
    is_image = args.video
    media_path = args.path

    if os.path.exists(os.path.join(os.getcwd(), media_path)):
        main(media_path, is_image)
    else:
        print("Invalid Path")
