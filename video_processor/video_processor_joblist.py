import hashlib
import cv2
import face_recognition
import threading
import os
import time
import datetime
from logger import Logger

import uuid

import urllib  # для видеопотоков c url

from joblib import Parallel, delayed


class FaceInfo():
    def __str__(self):
        return self.name

    def __init__(self):
        self.ID = 0
        self.hash = 0
        self.SourceId = 0
        self.detected_face_location = []
        self.detected_face_encoding = []  # это и есть изображение, то что мы сейчас в self.image пишем
        self.timestamp_global = 0  # глобальное время
        self.timestamp_current = 0  # Локальное время

        # и само изображение!
        self.image = []


class VideoProcessor():
    '''обработка одного кадра с любого источника'''

    def __init__(self, logger_address, path='img'):
        self.logger_address = logger_address
        self.file_counter = 1
        self.test_image_dir = ""

    def _frame_init(self, frame_in, sourceId, timestamp, distance_filename, frame_counter, frame_rate,
                    send_to_service=0, keep_on=0, debug=0):

        if frame_in is None or len(frame_in) == 0:
            return

        frame = frame_in
        small_frame = cv2.resize(frame, (0, 0), fx=0.33, fy=0.33)

        detected_facess_locations = face_recognition.face_locations(small_frame)
        # detected_facess_locations
        if (len(detected_facess_locations) > 0):
            detected_faces_encodings = face_recognition.face_encodings(small_frame, detected_facess_locations)

            face_info_list = []
            try:
                for (top, right, bottom, left), f_encoding in zip(detected_facess_locations, detected_faces_encodings):
                    face_info = FaceInfo()

                    top *= 3
                    right *= 3
                    bottom *= 3
                    left *= 3

                    face_image = frame[top:bottom, left:right]
                    # координаты заполнять
                    location_list = [top, right, bottom, left]

                    face_info.ID = uuid.uuid1()

                    face_info.detected_face_location = location_list
                    face_info.image = face_image
                    face_info.detected_face_encoding = f_encoding

                    face_info.timestamp_global = timestamp
                    face_info.SourceId = sourceId

                    face_info_list.append(face_info)

                logger = Logger(self.logger_address)

                logger.write_data_to_file(face_info_list, distance_filename, send_to_service,
                                          keep_on)  # записываем в лог


            except Exception as e:
                print('decode error:' + str(e))
                pass

    def batch_fotos_scan(self, batch_images_list, source_id, debug=0):

        for image in batch_images_list:
            self._frame_init(image, source_id, time.ctime(), debug)

    def get_samples_from_video_stream(self, video_capture, source_id, frame_rate, send_to_service=0, keep_on=0,
                                      debug=0):
        '''анализ лиц из видеопотока'''
        '''frameRate - берем только каждый n-й кадр'''
        # cv2.VideoCapture(0)
        print("start scan")
        print('logger address:' + self.logger_address)
        framecouter = 1
        while True:
            Parallel(n_jobs=4)(delayed(self._frame_init)(video_capture.read()[1], 0, time.ctime(), "noname",
                                                         i, frame_rate, send_to_service=1, keep_on=1, debug=debug)
                               for i in range(framecouter, framecouter + 4 * frame_rate))

            framecouter += 4 * frame_rate
            if debug == 1:
                print(time.ctime())
                print(framecouter)

                # вот с этим, выходит проблемы теперь

    def get_samples_from_video_file(self, file_name, frame_rate, debug=0):
        '''анализ лиц из видеофайла'''
        '''frameRate - берем только каждый n-й кадр'''
        '''distance_filename - имя файла разультатов .nmp'''

        video_capture_from_file = cv2.VideoCapture(file_name)
        framecouter = 0

        start_time = datetime.datetime.now()
        length = int(video_capture_from_file.get(cv2.CAP_PROP_FRAME_COUNT))  # video_capture_from_file.isOpened()
        if debug == 1:
            print("frames:" + str(length))

        while framecouter < length:
            video_capture_from_file.set(cv2.CAP_PROP_FPS,
                                        frame_rate);

            Parallel(n_jobs=4)(delayed(self._frame_init)(video_capture_from_file.read()[1], 0, time.ctime(), "noname",
                                                         i, frame_rate, send_to_service=0, keep_on=1, debug=debug)
                               for i in range(framecouter, framecouter + 4 * frame_rate))

            framecouter += 4 * frame_rate

        video_capture_from_file.release()

        logger = Logger(self.logger_address)
        logger.send_archive_to_service(keep_on=1)

        during = datetime.datetime.now() - start_time
