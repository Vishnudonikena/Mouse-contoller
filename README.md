# 👁️ Eye-Blink Mouse Controller

Tired of using a traditional mouse? This project allows you to control your computer's mouse cursor and perform clicks simply by tracking your eyes and detecting blinks through your webcam. It offers a hands-free way to interact with your PC, perfect for situations where a mouse is unavailable or for users exploring new accessibility tools.

---

## ✨ Core Features

* **Cursor Control:** Move the cursor around the screen by moving your head.
* **Left Click:** Perform a left-click by blinking your **left eye**.
* **Right Click:** Perform a right-click by blinking your **right eye**.
* **Real-time Feedback:** An overlay on the video feed shows the eye detection points.

---

## ⚙️ Requirements & Installation

This project is built with Python and relies on computer vision libraries.

### Prerequisites

* Python 3.7+
* A webcam connected to your computer

### Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Vishnudonukena/Mouse-contoller.git](https://github.com/Vishnudonukena/Mouse-contoller.git)
    cd Mouse-contoller
    ```

2.  **Install Required Libraries**
    It's recommended to use a virtual environment. All dependencies are listed in `requirements.txt`.
    ```bash
    # Install all the necessary packages
    pip install opencv-python mediapipe pyautogui
    ```
    *(You can also create a `requirements.txt` file with `opencv-python`, `mediapipe`, and `pyautogui` listed inside and then run `pip install -r requirements.txt`)*

---

## 🚀 How to Use

Once the installation is complete, you can run the application with a single command.

1.  **Run the Script**
    Open your terminal or command prompt, navigate to the project directory, and execute:
    ```bash
    python main.py
    ```
    *(Note: Replace `main.py` with the actual name of your main script if it's different.)*

2.  **Operation**
    * A window will appear showing your webcam feed.
    * Position your face so that it is clearly visible. The program will automatically start tracking your face and eyes.
    * Move your head to guide the mouse cursor across the screen.
    * Blink your left or right eye to perform clicks.

---

## 🔧 How It Works

The application uses the **OpenCV** library to capture video from the webcam and the **MediaPipe** library for highly accurate face mesh and landmark detection. It calculates the Eye Aspect Ratio (EAR) for both eyes in real-time. A sudden drop in the EAR value below a certain threshold is registered as a blink, which then triggers a mouse click event via the **PyAutoGUI** library.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
