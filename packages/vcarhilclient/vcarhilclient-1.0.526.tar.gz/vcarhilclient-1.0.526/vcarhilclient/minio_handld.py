# -*- coding: utf-8 -*-
import os , sys
r=os.path.abspath(os.path.dirname(__file__))
rootpath=os.path.split(r)[0]
sys.path.append(rootpath)
from minio import Minio
from minio.error import InvalidResponseError


class MinioClient():
    def __init__(self, endpoint='192.168.5.11:9000', access_key='YB3n5q4aWaGbARM0',
                 secret_key='cbEnccQGV6Gd9D9D6EWkVq1Tzk4qAnsP', secure=False):
        self.minioClient = Minio(endpoint,
                                 access_key=access_key,
                                 secret_key=secret_key,
                                 secure=secure)

    #     上传文件，并返回文件的url
    def upload_file(self, bucket_name, file_name, file_path):
        try:
            self.minioClient.fput_object(bucket_name, file_name, file_path)
            url = self.minioClient.presigned_get_object(bucket_name, file_name)
            return url
        except InvalidResponseError as err:
            print(err)
            return None

    #     下载文件
    def download_file(self, bucket_name, file_name, file_path):
        try:
            self.minioClient.fget_object(bucket_name, file_name, file_path)
        except InvalidResponseError as err:
            print(err)
            return None

    #     删除文件
    def remove_file(self, bucket_name, file_name):
        try:
            self.minioClient.remove_object(bucket_name, file_name)
        except InvalidResponseError as err:
            print(err)
            return None

    #     列出桶中的文件
    def list_file(self, bucket_name,prefix):
        try:
            objects = self.minioClient.list_objects(bucket_name,prefix=prefix, recursive=False)
            file_list = []
            for obj in objects:
                file_list.append(obj.object_name)
                print(obj.bucket_name, obj.object_name.encode('utf-8'), obj.last_modified,
                      obj.etag, obj.size, obj.content_type)
            return file_list
        except InvalidResponseError as err:
            print(err)
            return None

    #     返回预览图片的url
    def get_preview_url(self, bucket_name, file_name):
        try:
            url = self.minioClient.presigned_get_object(bucket_name, file_name)
            return url
        except InvalidResponseError as err:
            print(err)
            return None

    def get_folder(self, bucket_name, folder_name, file_path):
        for item in self.minioClient.list_objects(bucket_name, prefix=folder_name, recursive=True):
            self.minioClient.fget_object(bucket_name, item.object_name, os.path.join(file_path, item.object_name))


# if __name__ == '__main__':
#     minioClient = MinioClient()
    # cultural-data-base
    #     删除文件
    #     minioClient.remove_file('cultural-data-base', 'data5.txt')
    #     列出桶中的文件
    #     minioClient.list_file('cultural-data-base')

    #     上传文件
    # url = minioClient.upload_file('cultural-data-base', '3.png', '3.png')
    # print(url)

#     下载文件
#     minioClient.download_file('buildsourse', 'emr/em1017.tar.gz', 'emr1/em1017.tar.gz')
#

# #     返回预览图片的url
#     url = minioClient.get_preview_url('cultural-data-base', '2.png')
#     print(url)