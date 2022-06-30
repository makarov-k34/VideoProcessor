import pickle
import numpy as np
import json
import zipfile
import time
import requests
import os

from PIL import Image


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


# @singleton
class Logger():

    def __init__(self, service_address, path='img', tech_log_dir="TechLog"):
        self.input_data = []
        self.service_address = service_address

        self.images_count = 0
        self.test_image_dir = path
        self.tech_log_dir = tech_log_dir

        if os.path.exists(self.test_image_dir) == False:
            os.mkdir(self.test_image_dir)

        if os.path.exists(self.tech_log_dir) == False:
            os.mkdir(self.tech_log_dir)

    def write_data_to_file(self, obj_list, distance_filename='dist', send_to_service=0, keep_on=0, debug=0):

        if send_to_service == 1:
            arc_date_name = str(time.time()) + 'archive_pic.zip'
            request_zip = zipfile.ZipFile(os.path.join(self.test_image_dir, arc_date_name), 'w')

        file_time_stamp = str(time.time())

        with open(os.path.join(self.test_image_dir, file_time_stamp + 'data.pickle'), 'wb') as f:
            for obj in obj_list:
                pil_image = Image.fromarray(obj.image)

                file_name = os.path.join(self.test_image_dir, str(obj.ID) + ".jpg")

                pil_image.save(file_name, "JPEG")

                dict_obj = {}
                dict_obj["ID"] = obj.ID
                dict_obj["SourceId"] = obj.SourceId
                dict_obj["detected_face_location"] = obj.detected_face_location
                dict_obj["detected_face_encoding"] = obj.detected_face_encoding.tolist()
                dict_obj["timestamp_global"] = obj.timestamp_global
                dict_obj["timestamp_current"] = obj.timestamp_current

                pickle.dump(dict_obj, f)

                if send_to_service == 1:
                    request_zip.write(file_name, str(obj.ID) + ".jpg", compress_type=zipfile.ZIP_DEFLATED)

        request_zip.write(os.path.join(self.test_image_dir, file_time_stamp + 'data.pickle'), 'data.pickle',
                          compress_type=zipfile.ZIP_DEFLATED)

        request_zip.close()

        if send_to_service == 1:
            self.send_file_to_service(os.path.join(self.test_image_dir, arc_date_name), keep_on)

    # остается непроработанным один момент, если слать по одиночке данные, то и  лог тоже?
    def send_file_to_service(self, file_name, keep_on=0):

        print('SENDING FILES.....')

        with open(file_name, 'rb') as files:
            r = requests.post(self.service_address, data=files)
        # self.write_tech_log_to_file(time.ctime(), r.text)

        # зачистить папку
        if keep_on == 0:
            os.remove(os.path.join(self.test_image_dir, file_name))

    def send_archive_to_service(self, keep_on=0):
        '''сжамает изображения и лог в один массив и отправляет на указанный сервис'''
        # отсылку возможно в другом потоку надо делать оч процессс тормозит
        print('SENDING FILES.....')

        arc_date_name = str(time.time()) + 'archive_pic.zip'
        request_zip = zipfile.ZipFile(os.path.join(self.test_image_dir, arc_date_name), 'w')

        for file in os.listdir(self.test_image_dir):
            if file != arc_date_name:
                request_zip.write(os.path.join(self.test_image_dir, file), file, compress_type=zipfile.ZIP_DEFLATED)

        request_zip.close()

        # если есть, где в архив загоняем

        with open(os.path.join(self.test_image_dir, arc_date_name), 'rb') as files:
            r = requests.post(self.service_address, files={'report': files})
            # self.write_tech_log_to_file(time.ctime(), r.text)

        # зачистить папку
        if keep_on == 0:
            for f in os.listdir(self.test_image_dir):
                rm_file = os.path.join(self.test_image_dir, f)
                if os.path.isfile(rm_file) == True:
                    os.remove(os.path.join(self.test_image_dir, f))

        # архив в любом случае удаляем
        os.remove(os.path.join(self.test_image_dir, arc_date_name))

    # запись в технический лог файл
    def write_tech_log_to_file(self, time, responce):
        with open(os.path.join(self.tech_log_dir, 'data.pickle'), 'wb') as f:
            pickle.dump(responce, f)
