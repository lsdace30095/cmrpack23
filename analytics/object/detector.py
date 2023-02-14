import os

import cv2
from PIL import ImageColor

from apps.home.models import Output

colors = [(255, 255, 23),  # Person
          (0, 255, 249),  # Vehicle
          (255, 0, 0),  # Bike
          (0, 0, 255),  # Collision
          (0, 0, 0)]  # Black


# (55, 104, 138)
# (138, 104, 55)


class Box:
    def __init__(self, box_obj, frame, img_h=0.0, img_w=0.0):
        self.frame = frame
        self.image_id = box_obj[0]
        self.label = box_obj[1]
        self.conf = box_obj[2]
        self.x_min = int(img_w * box_obj[3])
        self.y_min = int(img_h * box_obj[4])
        self.x_max = int(img_w * box_obj[5])
        self.y_max = int(img_h * box_obj[6])
        self.w_box = self.x_max - self.x_min
        self.h_box = self.y_max - self.y_min
        # self._draw_box()

    def detections(self):
        return self.image_id, self.label, self.conf, self.x_min, self.y_min, self.x_max, self.y_max

    def _draw_box(self):
        cv2.rectangle(self.frame, (self.x_min, self.y_min - 20), (self.x_max, self.y_min),
                      colors[int(self.label)], 1)
        cv2.rectangle(self.frame, (self.x_min, self.y_min), (self.x_max, self.y_max), colors[int(self.label)], 1)
        cv2.rectangle(self.frame, (self.x_min, self.y_max - 20), (self.x_max, self.y_max),
                      colors[int(self.label)], 1)

    @staticmethod
    def take_screenshot(obj, frame, channel):
        try:
            label = ("Person", "Vehicle", "Bike")[int(obj.label) - 1]
            crop_img = frame[obj.y_min - 20:obj.y_max + 20, obj.x_min - 20:obj.x_max + 20]
            if len(crop_img) != 0:

                # secure channel title as directory name
                try:
                    output = Output.objects.get(channel=channel)
                    dir_name = output.dir_name
                except:
                    dir_name = "".join(
                        [c for c in channel.camera_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                    Output.objects.update_or_create(channel=channel, defaults={
                        'channel': channel, 'dir_name': dir_name
                    })

                # create dir
                if not os.path.isdir('media/screenshots/{}'.format(dir_name)):
                    os.makedirs('media/screenshots/{}'.format(dir_name))
                filename = 'media/screenshots/{}/{}_{}.jpg'.format(dir_name, obj.id + 1, label)

                #  Write image
                cv2.imwrite(filename, crop_img)
        except:
            pass

    @staticmethod
    def draw_tracker(obj, frame, model_config):

        if model_config.model.vehicle_label == int(obj.label):
            class_label = "Vehicle"
            color = model_config.vehicle_object_color
        elif model_config.model.bike_label == int(obj.label):
            class_label = "Bike"
            color = model_config.bike_object_color
        elif model_config.model.person_label == int(obj.label):
            class_label = "Person"
            color = model_config.person_object_color
        else:
            class_label = "Unknown"
            color = (0, 0, 0)

        # label_text = 'ID: {} Class: {}'.format(obj.id + 1, class_label)
        label_text = '#{}: {}: {}%'.format(obj.id + 1, class_label, obj.confidence)
        color = ImageColor.getrgb(color)
        color = color[::-1]  # BRG

        cv2.putText(frame, label_text, (obj.x_min + 5, obj.y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.circle(frame, (obj.cX, obj.cY), 2, color, 2)
        cv2.rectangle(frame, (obj.x_min, obj.y_min - 20), (obj.x_max, obj.y_min), color, 1)
        cv2.rectangle(frame, (obj.x_min, obj.y_min), (obj.x_max, obj.y_max), color, 1)
        cv2.rectangle(frame, (obj.x_min, obj.y_max - 20), (obj.x_max, obj.y_max), color, 1)

    @staticmethod
    def draw_near_miss(obj, frame, label, color):
        # Count object and print
        class_label = ("Person", "Vehicle", "Bike")[int(obj.label) - 1]
        label_text = '{}% {}'.format(obj.confidence, label)

        color = ImageColor.getrgb(color)
        color = color[::-1]  # BRG
        text_color = (255, 255, 255)

        cv2.circle(frame, (obj.cX, obj.cY), 2, color, 2)
        cv2.rectangle(frame, (obj.x_min, obj.y_min - 20), (obj.x_max, obj.y_min), color, -1)
        cv2.rectangle(frame, (obj.x_min, obj.y_min), (obj.x_max, obj.y_max), color, 1)
        cv2.rectangle(frame, (obj.x_min, obj.y_max - 20), (obj.x_max, obj.y_max), color, 1)
        cv2.putText(frame, label_text, (obj.x_min + 5, obj.y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        return frame

    @staticmethod
    def draw_collision(obj, frame, label, color):
        # Count object and print
        class_label = ("Person", "Vehicle", "Bike")[int(obj.label) - 1]
        label_text = '{}% {}'.format(obj.confidence, label)

        color = ImageColor.getrgb(color)
        color = color[::-1]  # BRG
        text_color = (255, 255, 255)

        cv2.circle(frame, (obj.cX, obj.cY), 2, color, 2)
        cv2.rectangle(frame, (obj.x_min, obj.y_min - 20), (obj.x_max, obj.y_min), color, -1)
        cv2.rectangle(frame, (obj.x_min, obj.y_min), (obj.x_max, obj.y_max), color, 1)
        cv2.rectangle(frame, (obj.x_min, obj.y_max - 20), (obj.x_max, obj.y_max), color, 1)
        cv2.putText(frame, label_text, (obj.x_min + 5, obj.y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        return frame

    @staticmethod
    def draw_metrics(metrics, objects_counter, frame):
        total_latency, total_fps = metrics.get_total()
        person, vehicle, bike = objects_counter

        # Print metrics
        metrics_text = 'Latency: {:.1f} ms\nFPS: {:.1f}\nPerson: {}\nVehicle: {}\nBike: {}\nTotal Count: {}'.format(
            total_latency * 1e3, total_fps, person, vehicle, bike, person + vehicle + bike)
        # Splitting new line
        y0, dy = 50, 30
        for i, line in enumerate(metrics_text.split('\n')):
            y = y0 + (i * dy)
            cv2.putText(frame, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 3)
            cv2.putText(frame, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 10, 10), 2)


class Detector:
    def __init__(self, core, config):

        # get all configuration
        self.config = config
        self.model = core.read_model(config.model.model_xml.path)

        if len(self.model.inputs) != 1:
            raise RuntimeError("Detector supports only models with 1 input layer")
        if len(self.model.outputs) != 1:
            raise RuntimeError("Detector supports only models with 1 output layer")

        input_shape = self.model.inputs[0].shape
        self.nchw_layout = input_shape[1] == 3

        OUTPUT_SIZE = 7
        output_shape = self.model.outputs[0].shape
        if len(output_shape) != 4 or output_shape[3] != OUTPUT_SIZE:
            print(output_shape)
            raise RuntimeError("Expected model output shape with {} outputs".format(OUTPUT_SIZE))

        compiled_model = core.compile_model(self.model, config.model.device)
        self.output_tensor = compiled_model.outputs[0]
        self.infer_request = compiled_model.create_infer_request()
        self.input_tensor_name = self.model.inputs[0].get_any_name()
        if self.nchw_layout:
            _, _, self.input_h, self.input_w = input_shape
        else:
            _, self.input_h, self.input_w, _ = input_shape

    def _preprocess(self, img):
        self._h, self._w, _ = img.shape
        if self._h != self.input_h or self._w != self.input_w:
            img = cv2.resize(img, dsize=(self.input_w, self.input_h), fy=self._h / self.input_h,
                             fx=self._h / self.input_h)
        if self.nchw_layout:
            img = img.transpose(2, 0, 1)
        return img[None]

    def _infer(self, prep_img):
        input_data = {self.input_tensor_name: prep_img}
        output = self.infer_request.infer(input_data)[self.output_tensor]
        return output[0][0]

    def _postprocess(self, detections, frame):

        # Filter obj by labels and threshold
        person = [Box(box, frame, self._h, self._w).detections() for box in detections if
                  int(box[1]) == self.config.model.person_label and box[2] > self.config.person_threshold]

        vehicle = [Box(box, frame, self._h, self._w).detections() for box in detections if
                   int(box[1]) == self.config.model.vehicle_label and box[2] > self.config.vehicle_threshold]

        bike = [Box(box, frame, self._h, self._w).detections() for box in detections if
                int(box[1]) == self.config.model.bike_label and box[2] > self.config.bike_threshold]

        boxes = person + vehicle + bike

        return boxes, person, vehicle, bike

    def detect(self, frame):
        preprocessed_frame = self._preprocess(frame)
        output = self._infer(preprocessed_frame)
        return self._postprocess(output, frame)


class ObjectTranslator:
    def __init__(self, obj):
        self.obj = obj
        self.id = None
        self.centroid = None
        self.cX = None
        self.cY = None
        self.image_id = None
        self.label = None
        self.confidence = None
        self.y_max = None
        self.y_min = None
        self.x_max = None
        self.x_min = None
        self.width = None
        self.height = None
        self.mod_x_min = None
        self.mod_x_max = None
        self.mod_y_min = None
        self.mod_y_max = None
        self.mod_width = None
        self.mod_height = None
        self.translate()

    def translate(self):
        self.id, self.centroid = self.obj

        self.cX, self.cY, self.image_id, self.label, self.confidence, self.x_min, self.y_min, self.x_max, self.y_max = \
            int(self.centroid[0]), int(self.centroid[1]), int(self.centroid[2]), int(self.centroid[3]), int(
                float(self.centroid[4]) * 100), int(self.centroid[5]), int(self.centroid[6]), int(
                self.centroid[7]), int(self.centroid[8])

        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min

        self.mod_x_min = self.x_min + (self.width / 4)
        self.mod_y_min = self.y_min + (self.height / 4)
        self.mod_x_max = self.mod_x_min + (self.width / 2)
        self.mod_y_max = self.mod_y_min + (self.height / 2)

        self.mod_width = self.mod_x_max - self.mod_x_min
        self.mod_height = self.mod_y_max - self.mod_y_min

    def is_collided(self, obj):
        return self.mod_x_min + self.mod_width >= obj.mod_x_min and \
            self.mod_x_min <= obj.mod_x_min + obj.mod_width and \
            self.mod_y_min + self.mod_height >= obj.mod_y_min and \
            self.mod_y_min <= obj.mod_y_min + obj.mod_height

    def is_near_missed(self, obj):
        return self.x_min + self.width >= obj.x_min and \
            self.x_min <= obj.x_min + obj.width and \
            self.y_min + self.height >= obj.y_min and \
            self.y_min <= obj.y_min + obj.height
