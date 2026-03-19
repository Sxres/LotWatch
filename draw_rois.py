import cv2
import json
import numpy as np 

VIDEO_PATH = "ParkingLot.mp4"
OUTPUT_FILE = "ParkingSpots.json"

parking_spots = []   # list of 4-point polygons [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
current_points = []  # points for the spot being drawn

cap = cv2.VideoCapture(VIDEO_PATH)
ret, frame = cap.read()
cap.release()
clone = frame.copy()

def draw(event, x, y):
    global current_points

    if event == cv2.EVENT_LBUTTONDOWN:
        current_points.append([x, y])

def render(frame):
    vis = frame.copy()

    # Draw completed spots
    for i, poly in enumerate(parking_spots):
        pts = np.array(poly, np.int32).reshape((-1, 1, 2))
        cv2.polylines(vis, [pts], True, (0, 255, 255), 2)
        cx = int(np.mean([p[0] for p in poly]))
        cy = int(np.mean([p[1] for p in poly]))
        cv2.putText(vis, str(i + 1), (cx - 8, cy + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Draw in-progress spot
    for pt in current_points:
        cv2.circle(vis, tuple(pt), 4, (0, 165, 255), -1)
    if len(current_points) > 1:
        for i in range(len(current_points) - 1):
            cv2.line(vis, tuple(current_points[i]), tuple(current_points[i+1]), (0, 165, 255), 1)
    if len(current_points) == 4:
        cv2.line(vis, tuple(current_points[3]), tuple(current_points[0]), (0, 165, 255), 1)

    hint = f"Spots: {len(parking_spots)} | Click 4 corners per spot | ENTER=confirm U=undo S=save Q=quit"
    cv2.putText(vis, hint, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    return vis

cv2.namedWindow("Draw ROIs")
cv2.setMouseCallback("Draw ROIs", draw)

while True:
    cv2.imshow("Draw ROIs", render(clone))
    key = cv2.waitKey(1) & 0xFF

    if key == 13:  # ENTER — confirm current polygon
        if len(current_points) == 4:
            parking_spots.append(current_points.copy())
            print(f"Spot {len(parking_spots)} saved: {current_points}")
            current_points = []
        else:
            print(f"Need 4 points, currently have {len(current_points)}")

    elif key == ord('u'):  # undo
        if current_points:
            current_points.pop()
        elif parking_spots:
            parking_spots.pop()
            print(f"Removed last spot. {len(parking_spots)} remaining.")

    elif key == ord('s'):  # save
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(parking_spots, f)
        print(f" Saved {len(parking_spots)} polygon spots to {OUTPUT_FILE}")
        break

    elif key == ord('q'):
        break

cv2.destroyAllWindows()