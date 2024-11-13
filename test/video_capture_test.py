import cv2

def main():
    # Open the camera and capture the video from the capture card
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # set the frame width and height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # set the frame rate
    cap.set(cv2.CAP_PROP_FPS, 23.98)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open the camera")
        return
    
    # print the camera properties
    print("Frame width: " + str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
    print("Frame height: " + str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print("Frame rate: " + str(cap.get(cv2.CAP_PROP_FPS)))
    
    # Loop to capture the video from the camera
    while True:
        # Capture the frame from the camera
        ret, frame = cap.read()

        # Check if the frame was captured successfully
        if not ret:
            print("Error: Could not capture the frame")
            break
        
        # Display the frame
        cv2.imshow("Camera", frame)

        # Check if the user pressed the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
