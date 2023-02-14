import copy
import time
from time import perf_counter
from analytics.common.performance_metrics import PerformanceMetrics

import cv2

from analytics.object.detector import Box, ObjectTranslator
from analytics.tracker.centroidtracker import CentroidTracker
from apps.home.models import Process


def counter(tracker, objects, prev_count):
    try:
        if objects is not None:
            trackable = tracker.update(objects)
            if trackable is not None:
                count = next(reversed(trackable))
                if count >= prev_count:
                    return count
    except:
        pass
    return prev_count


def process(capture, channel, proc_id, detector, model_config, collision_config):
    boxes_tracker, person_tracker, vehicle_tracker, bike_tracker = CentroidTracker(), CentroidTracker(), \
                                                                   CentroidTracker(), CentroidTracker()
    metrics = PerformanceMetrics()

    vehicles_count = 0
    bikes_count = 0
    person_count = 0
    near_misses = set()
    collisions = set()

    while True:
        cap = capture.read()

        fresh_frame = copy.copy(cap)
        frame = copy.copy(cap)

        if frame is None:
            time.sleep(1)
            # processed_dict.pop(proc_data.proc_id)
            if proc_id is not None:
                Process.objects.filter(id=proc_id, current=True).update(
                    current=False
                )
            break

        start_time = perf_counter()

        # detect objects from frame
        boxes, person, vehicle, bike = detector.detect(frame)

        # count tracked objects
        vehicles_count = counter(vehicle_tracker, vehicle, vehicles_count)
        bikes_count = counter(bike_tracker, bike, bikes_count)
        person_count = counter(person_tracker, person, person_count)

        # track all objects
        if boxes is not None:
            objects = boxes_tracker.update(boxes)
            items = list(objects.items())
            for i, (ID, centroid) in enumerate(objects.items()):
                obj_translator = ObjectTranslator((ID, centroid))
                Box.take_screenshot(obj=obj_translator, frame=fresh_frame, channel=channel)
                Box.draw_tracker(obj=obj_translator, frame=frame, model_config=model_config)

            for i in range(len(items) - 1):
                for j in range(i + 1, len(items)):
                    obj1 = ObjectTranslator(items[i])
                    obj2 = ObjectTranslator(items[j])

                    if obj1.is_near_missed(obj2):
                        frame = Box.draw_near_miss(obj=obj1, frame=frame, label=collision_config.near_miss_event_text,
                                                   color=collision_config.near_miss_box_color)
                        frame = Box.draw_near_miss(obj=obj2, frame=frame, label=collision_config.near_miss_event_text,
                                                   color=collision_config.near_miss_box_color)
                        near_misses.add(obj1.id)

                    if obj1.is_collided(obj2):
                        frame = Box.draw_collision(obj=obj1, frame=frame, label=collision_config.collision_event_text,
                                                   color=collision_config.collision_box_color)
                        frame = Box.draw_collision(obj=obj2, frame=frame, label=collision_config.collision_event_text,
                                                   color=collision_config.collision_box_color)
                        collisions.add(obj1.id)

        if proc_id is not None:
            Process.objects.filter(id=proc_id).update(
                collisions=len(collisions), near_misses=len(near_misses), vehicles=vehicles_count, bikes=bikes_count,
                persons=person_count
            )

        metrics.update(start_time, None)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

