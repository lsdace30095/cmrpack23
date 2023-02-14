import os

import cv2

from core import settings


def uploaded_file(file, upload_to_dir):
    # baseurl = "{0}://{1}".format(request.scheme, request.get_host())

    dir_name = '{}/files/{}/'.format(settings.MEDIA_ROOT, upload_to_dir)
    os.makedirs(dir_name, exist_ok=True)
    file_pth = dir_name + file.name

    with open(file_pth, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return 'files/{}/{}'.format(upload_to_dir, file.name)  # .replace(' ', '%20')


def generate_thumbnails(url, file_name, link=False):
    # baseurl = "{0}://{1}".format(request.scheme, request.get_host())
    dir_name = '{}/files/thumbnails/'.format(settings.MEDIA_ROOT)
    os.makedirs(dir_name, exist_ok=True)
    file_name = os.path.splitext(file_name)[0] + ".jpg"
    file_pth = dir_name + file_name

    if not link:
        url = os.path.join(settings.MEDIA_ROOT, url)

    try:
        cap = cv2.VideoCapture(url)
        success, frame = cap.read()
        while success:
            success, frame = cap.read()
            if frame.mean() > 60:
                success, frame = cap.read()
                break
        cv2.imwrite(file_pth, frame)
    except Exception as e:
        print(e)

    return '{}files/thumbnails/{}'.format(settings.MEDIA_URL, file_name)
