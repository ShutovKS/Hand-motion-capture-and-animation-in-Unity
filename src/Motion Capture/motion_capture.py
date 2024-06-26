# motion_capture.py
import cv2
from cvzone.HandTrackingModule import HandDetector


class MotionCapture:
    def __init__(self):
        self.detector = HandDetector()
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 1280)
        self.cam.set(4, 720)
        self.detector = HandDetector(detectionCon=0.8, maxHands=2)

        success, img = self.cam.read()
        self.h, self.w, _ = img.shape

        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.is_visible_current_handler_image_on_screen = config.get('Server', 'host')

    def webcam_capture(self):
        # Стриминг видео с вебкамеры
        success, img = self.cam.read()
        if not success:
            print("Не удалось прочитать кадр. Проверьте подключение веб-камеры.")
            return None

        return self.__handler(img)

    def video_file_capture(self, video_path):
        # Обработка локального видео
        self.cam = cv2.VideoCapture(video_path)
        while True:
            success, img = self.cam.read()
            if not success:
                self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            pose_data = self.__handler(img)
            if pose_data is not None:
                yield pose_data

        self.cam.release()
        cv2.destroyAllWindows()

    def image_file_capture(self, image_path):
        # Обработка локального изображения
        img = cv2.imread(image_path)
        if img is None:
            print(f"Не удалось прочитать изображение из файла {image_path}. Проверьте путь к файлу.")
            return None

        return self.__handler(img)

    def ip_camera_capture(self, ip_address):
        # Использование камеры с IP-адресом
        self.cam = cv2.VideoCapture(f"rtsp://{ip_address}")
        success, img = self.cam.read()
        if not success:
            print(f"Не удалось прочитать кадр с камеры IP {ip_address}. Проверьте IP-адрес.")
            return None

        return self.__handler(img)

    def rtsp_stream_capture(self, rtsp_url):
        # Обработка видео с RTSP-потока
        self.cam = cv2.VideoCapture(rtsp_url)
        success, img = self.cam.read()
        if not success:
            print(f"Не удалось прочитать кадр из RTSP потока {rtsp_url}. Проверьте URL.")
            return None

        return self.__handler(img)

    def usb_camera_capture(self, device_index=0):
        # Использование камеры с поддержкой USB
        self.cam = cv2.VideoCapture(device_index)
        success, img = self.cam.read()
        if not success:
            print(f"Не удалось прочитать кадр с USB камеры. Проверьте подключение камеры.")
            return None

        return self.__handler(img)

    def __handler(self, img):
        try:
            hands, img = self.detector.findHands(img)
            data = []

            if hands:
                hand = hands[0]
                lmList = hand["lmList"]
                for lm in lmList:
                    data.extend([lm[0], self.h - lm[1], lm[2]])

            if self.is_visible_current_handler_image_on_screen:
                self.__print_current_image_on_screen(img)

            return data
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            return None

    def __print_current_image_on_screen(self, img):
        cv2.imshow("Image", img)
        cv2.waitKey(1)
