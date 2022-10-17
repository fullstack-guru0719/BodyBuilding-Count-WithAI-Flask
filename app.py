from flask import *
import cv2
from utils import *
import mediapipe as mp
from body_part_angle import *
from types_of_exercise import TypeOfExercise

app = Flask(__name__)
app.secret_key = "abc"
# camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture("static/videos/sit-up.mp4")
camera.set(3, 800)  # width
camera.set(4, 480)
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
counter = 0
status = True
type = "sit-up"

pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def generate_frames(exer_type):
    global counter  # movement of exercise
    global status  # state of move
    counter = 0
    status = True
    while True:
        try:
            success, frame = camera.read()
            frame = cv2.resize(frame, (800, 480), interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame.flags.writeable = False
            results = pose.process(frame)
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            try:
                landmarks = results.pose_landmarks.landmark
                counter, status = TypeOfExercise(
                    landmarks).calculate_exercise(exer_type, counter, status)
            except:
                pass
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=(255, 255, 255), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(
                    color=(174, 139, 45), thickness=2, circle_radius=2),
            )
            if not success:
                break
            else:
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b'\r\n')
        except:
            break


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/sit_up")
def sit_up():
    return render_template("sit_up.html")


@app.route("/video")
def video():
    return Response(generate_frames(type), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/count", methods=["GET"])
def count():
    return jsonify(result=counter)


@app.route("/save_result")
def save_result():
    return render_template("save_result.html", result=counter)


@app.route("/pull_up")
def pull_up():
    global type
    type = "pull-up"
    return render_template("pull_up.html")


@app.route("/push_up")
def push_up():
    global type
    type = "push-up"
    return render_template("push_up.html")


@app.route("/squat")
def squat():
    global type
    type = "squat"
    return render_template("squat.html")


@app.route("/walk")
def walk():
    global type
    type = "walk"
    return render_template("walk.html")


if __name__ == "__main__":
    app.run(debug=True)
