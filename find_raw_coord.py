import cv2
import os

# === Step 1: Load Image ===
image_path = r"image_fix.png"  # 🔁 Change if needed

if not os.path.exists(image_path):
    print("❌ Image path not found!")
    exit()

original = cv2.imread(image_path)
if original is None:
    print("❌ Failed to load image. Format issue?")
    exit()

# === Step 2: Resize for Display ===
scale_percent = 50  # Display size (%)
width = int(original.shape[1] * scale_percent / 100)
height = int(original.shape[0] * scale_percent / 100)
display = cv2.resize(original, (width, height))
clone = display.copy()

# === Step 3: Variables ===
rectangles = []
drawing = False
ix, iy = -1, -1
question_number = 1
option_index = 0
options = ["DRILLING", "TRAVEL", "P2H", "ISI FUEL", "EVAKUASI", "SAFETY TALK", "GANTI BIT", "GANTI ROD", "WAITING AREA", "HUJAN", "WASHING", "TUNGGU PATTERN", "REST TIME", "REDRILL","BD","SERVICE"]
output_file = 'roll_coordinates.txt'

# Clear previous output
open(output_file, 'w').close()

# === Step 4: Mouse Callback ===
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, display, question_number, option_index

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(display, (ix, iy), (x, y), (0, 255, 0), 2)
        label = f'Q{question_number}{options[option_index]}'
        cv2.putText(display, label, (ix, iy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # Convert to original scale
        x1_scaled = int(ix * 100 / scale_percent)
        y1_scaled = int(iy * 100 / scale_percent)
        x2_scaled = int(x * 100 / scale_percent)
        y2_scaled = int(y * 100 / scale_percent)

        rectangles.append((label, x1_scaled, y1_scaled, x2_scaled, y2_scaled))
        print(f'{label}: ({x1_scaled}, {y1_scaled}) to ({x2_scaled}, {y2_scaled})')

        with open(output_file, 'a') as f:
            f.write(f'{label}: ({x1_scaled}, {y1_scaled}) to ({x2_scaled}, {y2_scaled})\n')

        option_index += 1
        if option_index >= 16:
            option_index = 0
            question_number += 1

# === Step 5: Show Window and Controls ===
cv2.namedWindow('OMR Sheet', cv2.WINDOW_NORMAL)
cv2.resizeWindow('OMR Sheet', 1000, 800)
cv2.setMouseCallback('OMR Sheet', draw_rectangle)

print("🖱️  Draw rectangles with mouse.")
print("🔁  Press 'r' to reset")
print("🗑️  Press 'd' to delete last rectangle")
print("✅  Press 'q' to quit and save")

while True:
    cv2.imshow('OMR Sheet', display)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        display = clone.copy()
        rectangles.clear()
        question_number = 1
        option_index = 0
        open(output_file, 'w').close()
        print("🔄 Reset complete.")

    elif key == ord('d'):
        if rectangles:
            # Remove last rectangle
            removed = rectangles.pop()
            print(f"🗑️  Removed {removed[0]}")
            # Update question/option counters
            option_index -= 1
            if option_index < 0:
                option_index = 3
                question_number -= 1
            # Redraw image
            display = clone.copy()
            for r in rectangles:
                label, x1, y1, x2, y2 = r
                # Convert to display scale
                x1_disp = int(x1 * scale_percent / 100)
                y1_disp = int(y1 * scale_percent / 100)
                x2_disp = int(x2 * scale_percent / 100)
                y2_disp = int(y2 * scale_percent / 100)
                cv2.rectangle(display, (x1_disp, y1_disp), (x2_disp, y2_disp), (0, 255, 0), 2)
                cv2.putText(display, label, (x1_disp, y1_disp - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            # Rewrite file
            with open(output_file, 'w') as f:
                for r in rectangles:
                    f.write(f'{r[0]}: ({r[1]}, {r[2]}) to ({r[3]}, {r[4]})\n')
        else:
            print("⚠️  Nothing to delete.")

    elif key == ord('q'):
        print("✅ Done. Coordinates saved to:", output_file)
        break

cv2.destroyAllWindows()
