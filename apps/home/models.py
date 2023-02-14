# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os

from django.core.files.storage import FileSystemStorage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import IntegerField, DecimalField

from core import settings


class Channel(models.Model):
    source = models.CharField(max_length=150)
    camera_name = models.CharField(max_length=150)
    camera_id = models.CharField(max_length=150, blank=True, null=True)
    apple_hls = models.CharField(max_length=150, blank=True, null=True)
    jpeg_url = models.CharField(max_length=150, blank=True, null=True)
    latitude = models.CharField(max_length=150, blank=True, null=True)
    longitude = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.camera_name)


class ChannelGroup(models.Model):
    title = models.CharField(max_length=150, default="Default Channel Group")

    slot1 = models.ForeignKey(Channel, related_name='slot1', on_delete=models.CASCADE, blank=True, null=True)
    slot2 = models.ForeignKey(Channel, related_name='slot2', on_delete=models.CASCADE, blank=True, null=True)
    slot3 = models.ForeignKey(Channel, related_name='slot3', on_delete=models.CASCADE, blank=True, null=True)
    slot4 = models.ForeignKey(Channel, related_name='slot4', on_delete=models.CASCADE, blank=True, null=True)
    slot5 = models.ForeignKey(Channel, related_name='slot5', on_delete=models.CASCADE, blank=True, null=True)
    slot6 = models.ForeignKey(Channel, related_name='slot6', on_delete=models.CASCADE, blank=True, null=True)

    active = models.BooleanField(default=False)

    def __str__(self):
        return "[SELECTED] {}".format(self.title) if self.active else "{}".format(self.title)


class AIModel(models.Model):
    title = models.CharField(max_length=150)

    model_bin = models.FileField(storage=FileSystemStorage(location=settings.MEDIA_ROOT), upload_to='models/')

    model_xml = models.FileField(storage=FileSystemStorage(location=settings.MEDIA_ROOT), upload_to='models/')

    floating_point_precision = models.CharField(
        max_length=9,
        default=("FP16", "FP16"),
        choices=(
            ("FP16", "FP16"),
            ("FP16-INT8", "FP16-INT8"),
            ("FP32", "FP32"),
            ("FP64", "FP64"),
        ), blank=False)

    device = models.CharField(
        max_length=9,
        default=("CPU", "CPU"), choices=(
            ("CPU", "CPU"),
            ("GPU", "GPU"),
            ("HDDL", "HDDL"),
            ("MYRIAD", "MYRIAD"),
        ), blank=False)

    person_label = IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(0)], blank=False)
    vehicle_label = IntegerField(default=2, validators=[MaxValueValidator(5), MinValueValidator(0)], blank=False)
    bike_label = IntegerField(default=3, validators=[MaxValueValidator(5), MinValueValidator(0)], blank=False)

    threshold = DecimalField(default=0.5, max_digits=2, decimal_places=2, validators=[MaxValueValidator(1),
                                                                                      MinValueValidator(0)])

    output_size = IntegerField(default=7, validators=[MaxValueValidator(7), MinValueValidator(7)], blank=False)

    def __str__(self):
        return "{}".format(self.title)


class ConfigChannel(models.Model):
    channel = models.ForeignKey(Channel, db_column='channel', on_delete=models.CASCADE)
    model = models.ForeignKey(AIModel, db_column='model', on_delete=models.CASCADE)

    vehicle_object_color = models.CharField(default="#5eb5ef", max_length=150, blank=True, null=True)
    vehicle_threshold = DecimalField(default=0.5, max_digits=1, decimal_places=1, validators=[MaxValueValidator(1),
                                                                                              MinValueValidator(0)])

    bike_object_color = models.CharField(default="#ffd878", max_length=150, blank=True, null=True)
    bike_threshold = DecimalField(default=0.5, max_digits=1, decimal_places=1, validators=[MaxValueValidator(1),
                                                                                           MinValueValidator(0)])

    person_object_color = models.CharField(default="#ff829d", max_length=150, blank=True, null=True)
    person_threshold = DecimalField(default=0.5, max_digits=1, decimal_places=1, validators=[MaxValueValidator(1),
                                                                                             MinValueValidator(0)])

    def __str__(self):
        return "{}".format(self.channel.camera_name)


class BaseConfig(models.Model):
    model = models.ForeignKey(AIModel, db_column='model', on_delete=models.CASCADE)

    vehicle_object_color = models.CharField(default="#5eb5ef", max_length=150, blank=True, null=True)
    vehicle_threshold = DecimalField(default=0.5, max_digits=1, decimal_places=1, validators=[MaxValueValidator(1),
                                                                                              MinValueValidator(0)])

    bike_object_color = models.CharField(default="#ffd878", max_length=150, blank=True, null=True)
    bike_threshold = DecimalField(default=0.5, max_digits=1, decimal_places=1, validators=[MaxValueValidator(1),
                                                                                           MinValueValidator(0)])

    person_object_color = models.CharField(default="#ff829d", max_length=150, blank=True, null=True)
    person_threshold = DecimalField(default=0.5, max_digits=1, decimal_places=1, validators=[MaxValueValidator(1),
                                                                                             MinValueValidator(0)])

    selected = models.BooleanField(default=False)

    def __str__(self):
        return "[SELECTED] Config of Model- {}".format(
            self.model.title) if self.selected else "Config of Model- {}".format(
            self.model.title)


class CollisionConfig(models.Model):
    collision_event_text = models.CharField(default="Collided", max_length=150, blank=True, null=True)
    collision_box_color = models.CharField(default="#FF2D00", max_length=150, blank=True, null=True)

    near_miss_event_text = models.CharField(default="Near Missed!!", max_length=150, blank=True, null=True)
    near_miss_box_color = models.CharField(default="#FFAD00", max_length=150, blank=True, null=True)

    collision_definition = models.CharField(
        max_length=250,
        default=("1", "If two or more objects intersect 25% each other"), choices=(
            ("0", "If two or more objects bodies touches"),
            ("1", "If two or more objects intersect 25% each other"),
            ("2", "If two or more objects intersect 50% each other"),
            ("3", "If two or more objects intersect 75% each other")
        ), blank=False)

    near_miss_definition = models.CharField(
        max_length=250,
        default=("0", "If two or more objects intersection is less than 25%"), choices=(
            ("0", "If two or more objects intersection is less than 25%"),
            ("1", "If two or more objects intersection is less than 50%")
        ), blank=False)

    selected = models.BooleanField(default=False)

    def __str__(self):
        return "[SELECTED] Config of Collision- {} Near Miss- {}".format(
            self.collision_event_text, self.near_miss_event_text) \
            if self.selected else "Config of Collision- {}".format(
            self.collision_event_text, self.near_miss_event_text)


class Process(models.Model):
    channel = models.ForeignKey(Channel, db_column='channel', on_delete=models.CASCADE)

    collisions = IntegerField(default=0, blank=True)
    near_misses = IntegerField(default=0, blank=True)
    vehicles = IntegerField(default=0, blank=True)
    bikes = IntegerField(default=0, blank=True)
    persons = IntegerField(default=0, blank=True)

    current = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.channel.camera_name)


class GraphConfig(models.Model):
    update_every = models.CharField(
        max_length=250,
        default=("1", "1 Seconds"), choices=(
            ("1", "1 Seconds"),
            ("5", "5 Seconds"),
            ("10", "10 Seconds"),
            ("15", "15 Seconds"),
            ("30", "30 Seconds"),
            ("60", "60 Seconds")
        ), blank=False)

    vehicle_flow_label = models.CharField(default="Vehicles", max_length=150, blank=True, null=True)
    vehicle_flow_color = models.CharField(default="#5eb5ef", max_length=150, blank=True, null=True)
    bike_flow_label = models.CharField(default="Bike", max_length=150, blank=True, null=True)
    bike_flow_color = models.CharField(default="#ffd878", max_length=150, blank=True, null=True)
    person_flow_label = models.CharField(default="Pedestrians", max_length=150, blank=True, null=True)
    person_flow_color = models.CharField(default="#ff829d", max_length=150, blank=True, null=True)

    vehicle_analysis_label = models.CharField(default="Vehicles", max_length=150, blank=True, null=True)
    vehicle_analysis_color = models.CharField(default="#5eb5ef", max_length=150, blank=True, null=True)
    bike_analysis_label = models.CharField(default="Bike", max_length=150, blank=True, null=True)
    bike_analysis_color = models.CharField(default="#ffd878", max_length=150, blank=True, null=True)
    person_analysis_label = models.CharField(default="Pedestrians", max_length=150, blank=True, null=True)
    person_analysis_color = models.CharField(default="#ff829d", max_length=150, blank=True, null=True)

    collision_label = models.CharField(default="Collisions", max_length=150, blank=True, null=True)
    collision_color = models.CharField(default="#FF2D00", max_length=150, blank=True, null=True)
    nearmiss_label = models.CharField(default="Near Miss", max_length=150, blank=True, null=True)
    nearmiss_color = models.CharField(default="#FFAD00", max_length=150, blank=True, null=True)

    selected = models.BooleanField(default=False)

    def __str__(self):
        return "[SELECTED] Config of Graph- {} {}".format(
            self.vehicle_flow_label, self.bike_flow_label) \
            if self.selected else "Config of Collision- {}".format(
            self.vehicle_flow_label, self.bike_flow_label)


class Output(models.Model):
    channel = models.ForeignKey(Channel, db_column='channel', on_delete=models.CASCADE)
    dir_name = models.CharField(default="Vehicles", max_length=150, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.dir_name)
