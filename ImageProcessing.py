import cv2
import numpy as np
from ultralytics import YOLO
import time

"""
Image proccessing part of the project coded for particular intersection video.
This code cannot be used in its current state.
Variables like zones needs to be changed before using.

"""

video_path = ""

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

zones = {
    "north": [(130, 150), (220, 150), (530, 330), (300, 370)],
    "west":  [(0, 440), (280, 420), (370, 500), (0, 540)],
    "south": [(700, 520), (970, 470), (1280, 700), (910, 760)],
    "east":  [(750, 300), (1279, 280), (1279, 350), (850, 410)]
}

zone_colors = {
    "north": (0, 0, 255),       
    "south": (0, 255, 0),     
    "east":  (255, 0, 0),     
    "west":  (0, 255, 255)    
}

tracks = {}
statuses = {}
counts = {zone: {"passed": 0, "waiting": 0} for zone in zones}
id_counter = 0

waiting_ids_by_zone = {zone: set() for zone in zones}

reset_times = [31 + i * 45 for i in range(20)]
reset_index = 0
last_second = -1

def point_in_polygon(x, y, polygon):
    return cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), (x, y), False) >= 0

def get_zone(cx, cy):
    for zone_name, poly in zones.items():
        if point_in_polygon(cx, cy, poly):
            return zone_name
    return None

def is_moving_correct_direction(track, zone):
    if len(track) < 5:
        return False
    dx = track[-1][0] - track[0][0]
    dy = track[-1][1] - track[0][1]

    if zone == "west": return dx > 5
    if zone == "east": return dx < -5
    if zone == "north": return dy > 5
    if zone == "south": return dy < -5
    return False

# === ANA DÖNGÜ ===
while True:
    ret, frame = cap.read()
    if not ret:
        frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if frame_pos >= frame_count - 1:
            print("[BİLGİ] Video tamamlandı.")
            break
        else:
            print("[UYARI] Kare okunamadı ama video bitmedi.")
            continue

    current_second = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
    if reset_index < len(reset_times) and current_second != last_second:
        last_second = current_second
        reset_time = reset_times[reset_index]
        if current_second == reset_time:
            if reset_index % 2 == 0:
                for z in ["north", "south"]:
                    counts[z]["passed"] = 0
                for z in ["east", "west"]:
                    counts[z]["waiting"] = 0
                print(f"[RESET] {reset_time}.sn → N/S passed ve E/W waiting sayaçları sıfırlandı.")
            else:
                for z in ["north", "south"]:
                    counts[z]["waiting"] = 0
                for z in ["east", "west"]:
                    counts[z]["passed"] = 0
                print(f"[RESET] {reset_time}.sn → N/S waiting ve E/W passed sayaçları sıfırlandı.")
            reset_index += 1

    results = model(frame)[0]

    for zone_name, poly in zones.items():
        cv2.polylines(frame, [np.array(poly, np.int32)], True, zone_colors[zone_name], 2)

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        if label not in ['car', 'bus', 'truck', 'motorcycle']:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        zone_now = get_zone(cx, cy)
        matched = False

        for vid in list(tracks.keys()):
            last_pos = tracks[vid][-1]
            if np.linalg.norm(np.array(last_pos) - np.array([cx, cy])) < 30:
                tracks[vid].append((cx, cy))
                matched = True

                status = statuses[vid]
                assigned_zone = status["zone_assigned"]

                if not point_in_polygon(cx, cy, zones[assigned_zone]):
                    if not status["counted_pass"] and is_moving_correct_direction(tracks[vid], assigned_zone):
                        counts[assigned_zone]["passed"] += 1
                        status["counted_pass"] = True
                    del tracks[vid]
                    del statuses[vid]
                    break

                if len(tracks[vid]) >= 5:
                    recent_movements = [
                        np.linalg.norm(np.array(tracks[vid][i]) - np.array(tracks[vid][i - 1]))
                        for i in range(-1, -5, -1)
                    ]
                    if all(m < 3 for m in recent_movements):
                        if status["stationary_since"] is None:
                            status["stationary_since"] = time.time()
                        elif not status["counted_wait"] and (time.time() - status["stationary_since"] > 2):
                            counts[assigned_zone]["waiting"] += 1
                            status["counted_wait"] = True
                            waiting_ids_by_zone[assigned_zone].add(vid)
                    else:
                        status["stationary_since"] = None
                break

        if not matched and zone_now:
            tracks[id_counter] = [(cx, cy)]
            statuses[id_counter] = {
                "zone_assigned": zone_now,
                "stationary_since": None,
                "counted_wait": False,
                "counted_pass": False
            }
            id_counter += 1

        if zone_now:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, f"{label} ({zone_now})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    y_offset = 30
    for zone in counts:
        text = f"{zone.upper()} - Waiting: {counts[zone]['waiting']} | Passed: {counts[zone]['passed']}"
        cv2.putText(frame, text, (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 30

    cv2.imshow("Intersection Monitor", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
