from apps.home.models import AIModel, CollisionConfig, GraphConfig, BaseConfig, ConfigChannel, Process, ChannelGroup, \
    Channel


class DBHelper:

    @staticmethod
    def get_ai_models():
        title = 'person-vehicle-bike-detection-crossroad-0078'
        try:
            models = AIModel.objects.all().order_by("-id")
            if len(models) == 0:
                raise Exception('AI model not found!')
        except:
            AIModel.objects.update_or_create(title=title, defaults={
                'title': title,
                'model_bin': 'models/person-vehicle-bike-detection-crossroad-0078.bin',
                'model_xml': 'models/person-vehicle-bike-detection-crossroad-0078.xml',
                'floating_point_precision': 'FP16',
                'device': 'CPU'
            })
            models = AIModel.objects.all().order_by("-id")

        return models

    @staticmethod
    def get_or_create_channel_config(channel):
        try:
            config = ConfigChannel.objects.get(channel=channel)
        except:
            config = DBHelper.get_base_config()

        return config

    @staticmethod
    def update_or_create_then_get_channel_config(channel, data):
        model_id = data.get("model", 0)
        vehicle_th = data.get("vehicleTh", 0.5)
        vehicle_color = data.get("vehicleColor", "#000")
        bike_th = data.get("bikeTh", 0.5)
        bike_color = data.get("bikeColor", "#000")
        person_th = data.get("personTh", 0.5)
        person_color = data.get("personColor", "#000")

        models = AIModel.objects.get(id=model_id)

        ConfigChannel.objects.update_or_create(channel=channel, defaults={
            'channel': channel,
            'model': models,
            'vehicle_threshold': vehicle_th,
            'vehicle_object_color': vehicle_color,
            'bike_threshold': bike_th,
            'bike_object_color': bike_color,
            'person_threshold': person_th,
            'person_object_color': person_color
        })

        return ConfigChannel.objects.get(channel=channel)

    @staticmethod
    def update_or_create_then_get_process(channel):
        Process.objects.update_or_create(channel=channel, defaults={
            'channel': channel,
            'collisions': 0, 'near_misses': 0, 'vehicles': 0, 'bikes': 0, 'persons': 0,
            'current': True
        })
        return Process.objects.get(channel=channel)

    @staticmethod
    def get_base_config():
        try:
            config = BaseConfig.objects.get(selected=True)
        except:
            BaseConfig.objects.update_or_create(selected=True, defaults={
                'model': DBHelper.get_ai_models()[0],
                'selected': True
            })
            config = BaseConfig.objects.get(selected=True)

        return config

    @staticmethod
    def get_collision_config():
        try:
            config = CollisionConfig.objects.get(selected=True)
        except:
            CollisionConfig.objects.update_or_create(selected=True, defaults={
                'selected': True,
                'collision_definition': 1, 'near_miss_definition': 0
            })
            config = CollisionConfig.objects.get(selected=True)

        return config

    @staticmethod
    def get_graph_config():
        try:
            config = GraphConfig.objects.get(selected=True)
        except:
            GraphConfig.objects.update_or_create(selected=True, defaults={
                'update_every': 1,
                'selected': True
            })
            config = GraphConfig.objects.get(selected=True)

        return config

    @staticmethod
    def get_or_create_channel_group():
        try:
            group = ChannelGroup.objects.get(active=True)
        except:
            ChannelGroup.objects.update_or_create(active=True, defaults={
                'active': True
            })
            group = ChannelGroup.objects.get(active=True)

        return group

    @staticmethod
    def update_or_create_then_get_channel_group(channel_id, slot_name):

        channel = Channel.objects.get(id=channel_id) if channel_id else None

        ChannelGroup.objects.update_or_create(active=True, defaults={slot_name: channel})

        return ChannelGroup.objects.get(active=True)
