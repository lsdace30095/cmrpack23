# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.
from .models import Channel, AIModel, BaseConfig, ConfigChannel, CollisionConfig, Process, GraphConfig, \
    Output, ChannelGroup

admin.site.register(Channel)
admin.site.register(ChannelGroup)
admin.site.register(AIModel)
admin.site.register(BaseConfig)
admin.site.register(ConfigChannel)
admin.site.register(CollisionConfig)
admin.site.register(Process)
admin.site.register(GraphConfig)
admin.site.register(Output)
