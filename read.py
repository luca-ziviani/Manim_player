import cv2
import time
import numpy as np

NAME_VIDEO = 'ShowWrite.mp4'

WAITING_KEY = 10 # Time in milliseconds to wait for a key press
NAME_WINDOW = 'Manim player'
TARGET_WIDTH, TARGET_HEIGHT = 800, 600
PAUSE_TIMES = [0, 1.5, 3, 4.5, 6] 

# Codes for arrows. WARNING: Codes for arrows can change for different OS
ARROW_LEFT = 37
ARROW_UP = 38
ARROW_RIGHT = 39
ARROW_DOWN = 40

# TODO: Implement a good video with Manim and define the list of pauses to import here.

def video_player(video_path):

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: video not found.")
        return
    cv2.namedWindow(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN)
    cv2.resizeWindow(NAME_WINDOW, TARGET_WIDTH, TARGET_HEIGHT)

    QUIT = False
    FULL_SCREEN = False

    pause_ms = [t * 1000 for t in PAUSE_TIMES]
    current_pause_index = 0

    while cap.isOpened() & (not QUIT):        
        # Read the current frame. If frame is read correctly, ret is True.
        ret, frame = cap.read()

        if ret:
            # Get the position of the frame in video in milliseconds.
            current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

            # Check if we are at one of the checkpoints
            if current_pause_index < len(pause_ms) and current_time_ms >= pause_ms[current_pause_index]:
                print('Manim player: paused...')

                A = cv2.waitKey(WAITING_KEY) 
                while A != 13: # 13 is the code for ENTER_KEY
                    if A == ord('q'):
                        print("Sono entrato in Q")
                        QUIT = True
                        break
                    if A == ord('f'):
                        # Mode full screen
                        print("Sono entrato in Full screen")
                        if FULL_SCREEN:
                            cv2.resizeWindow(NAME_WINDOW, TARGET_WIDTH, TARGET_HEIGHT)
                            #cv2.setWindowProperty(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                            FULL_SCREEN = False
                        else:
                            cv2.setWindowProperty(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                            FULL_SCREEN = True
                    if A & 0xFF == ARROW_RIGHT:
                        # skip animation
                        current_pause_index = np.min([len(pause_ms)-1, current_pause_index+1]) 
                        cap.set(cv2.CAP_PROP_POS_MSEC, pause_ms[current_pause_index]-2)
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow(NAME_WINDOW, frame)
                    if A & 0xFF == ARROW_LEFT:
                        # previous animation
                        current_pause_index = np.max([0, current_pause_index-1]) 
                        cap.set(cv2.CAP_PROP_POS_MSEC, pause_ms[current_pause_index]-2)
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow(NAME_WINDOW, frame)

                    print(f'You pressed {A}, you have to press ENTER to continue')
                    A = cv2.waitKey(0)
                    cv2.imshow(NAME_WINDOW, frame)
                
                print('Manim player: resuming...')
                current_pause_index += 1
            
            A = cv2.waitKey(WAITING_KEY)
            if A & 0xFF == ord('q'):
                break
            if A & 0xFF == ord('f'):
                # Mode full screen
                if FULL_SCREEN:
                    cv2.setWindowProperty(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    FULL_SCREEN = False
                else:
                    cv2.setWindowProperty(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    FULL_SCREEN = True
            if A & 0xFF == ARROW_RIGHT:
                # skip animation
                current_pause_index = np.min([len(pause_ms)-1, current_pause_index+1]) 
                cap.set(cv2.CAP_PROP_POS_MSEC, pause_ms[current_pause_index]-2)
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(NAME_WINDOW, frame)
            if A & 0xFF == ARROW_LEFT:
                # previous animation
                current_pause_index = np.max([0, current_pause_index-1]) 
                cap.set(cv2.CAP_PROP_POS_MSEC, pause_ms[current_pause_index]-2)
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(NAME_WINDOW, frame)

            cv2.imshow(NAME_WINDOW, frame)
            
        else:
            # We reach the end of the video, we close the window only if 'q' is pressed
            # We still give the possibility to the user to go back and forth of resize the screen
            A = cv2.waitKey(0)
            if A & 0xFF == ord('q'):
                break
            if A & 0xFF == ord('f'):
                # Mode full screen
                if FULL_SCREEN:
                    cv2.setWindowProperty(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    FULL_SCREEN = False
                else:
                    cv2.setWindowProperty(NAME_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    FULL_SCREEN = True
            if A & 0xFF == ARROW_RIGHT:
                # skip animation
                current_pause_index = np.min([len(pause_ms)-1, current_pause_index+1]) 
                cap.set(cv2.CAP_PROP_POS_MSEC, pause_ms[current_pause_index]-2)
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(NAME_WINDOW, frame)
            if A & 0xFF == ARROW_LEFT:
                # previous animation
                current_pause_index = np.max([0, current_pause_index-1]) 
                cap.set(cv2.CAP_PROP_POS_MSEC, pause_ms[current_pause_index]-2)
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(NAME_WINDOW, frame)
 
    # Deallocate structures
    cap.release()
    cv2.destroyAllWindows()

# Call the function on the video:
video_player(NAME_VIDEO)