import csv
import logging
import os
import uuid
from pathlib import Path

import cv2
from django import template
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from openvino.runtime import Core
from datetime import datetime

from analytics.tools.remover import NoisyObjectRemover
from core import settings as app_setting

from analytics.common.images_capture import open_images_capture
from analytics.object.detector import Detector
from analytics.processing.frame_processing import process
from core import settings as app_settings
from .db_helper import DBHelper
from .forms import CCTVChannelForm
from .models import Channel, BaseConfig, AIModel, CollisionConfig, ConfigChannel, Process, GraphConfig, Output
from .utilities import ByteSize
from ..django_serverside_datatable.views import ServerSideDatatableView
from ..functions.functions import uploaded_file, generate_thumbnails


class ItemListView(ServerSideDatatableView):
    queryset = Channel.objects.all()
    columns = ['id', 'source', 'camera_name', 'camera_id', 'apple_hls', 'jpeg_url']


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:

        print(e)

        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def data(request):
    try:
        process_id = request.GET.get('id', None)
        process_obj = Process.objects.get(id=process_id, current=True)

        payload = {
            'data': {
                'collisions': process_obj.collisions,
                'near_miss': process_obj.near_misses,
                'pedestrians': process_obj.persons,
                'vehicles': process_obj.vehicles,
                'bikes': process_obj.bikes,
            }
        }

        return JsonResponse(payload, status=200)
    except Exception as e:
        return JsonResponse({'status': 'false', 'message': e.__str__()}, status=500)


def stream(request):
    process_id = request.GET.get('process', None)
    channel_id = request.GET.get('channel', None)

    channel, filename, model_config, collision_config = None, None, None, None
    if channel_id:
        # Retrieve channel information
        channel = Channel.objects.get(pk=channel_id)

        # Construct filename. If source is referring any local file then we join Media root with file path
        # Else we return the source url
        if channel.source in ['Video', 'Image']:
            filename = os.path.join(app_setting.MEDIA_ROOT, channel.apple_hls)
        else:
            filename = channel.apple_hls

        # Load Model configuration
        try:
            model_config = ConfigChannel.objects.get(channel=channel)
        except:
            model_config = BaseConfig.objects.get(selected=True)

        collision_config = CollisionConfig.objects.get(selected=True)

    return StreamingHttpResponse(
        process(capture=open_images_capture(filename, False),
                channel=channel,
                proc_id=process_id,
                detector=Detector(Core(), model_config),
                model_config=model_config,
                collision_config=collision_config),
        content_type='multipart/x-mixed-replace; boundary=frame')


@login_required(login_url="/login/")
def dashboard(request):
    context = {}

    try:
        load_template = 'dashboard.html'
        channel_id = request.GET.get('id', None)

        context['models'] = DBHelper.get_ai_models()
        context['collision_config'] = DBHelper.get_collision_config()
        context['graph_config'] = DBHelper.get_graph_config()
        context['model_config'] = DBHelper.get_base_config()
        context['segment'] = load_template

        if channel_id:
            context['channel'] = channel_id
            channel = Channel.objects.get(id=channel_id)

            context['process'] = DBHelper.update_or_create_then_get_process(channel=channel).id

            # Update or create channel configuration
            if request.method == "POST" and request.POST:
                context['model_config'] = DBHelper.update_or_create_then_get_channel_config(channel, request.POST)
            else:
                context['model_config'] = DBHelper.get_or_create_channel_config(channel)

        html_template = loader.get_template('home/' + load_template)

        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def channels(request):
    context = {}

    try:
        load_template = 'channels.html'
        if request.method == "POST":

            query_data = request.POST
            export = query_data.get("export", False)
            if export:
                all_channels = Channel.objects.all().order_by("id")

                # Create the HttpResponse object with the appropriate CSV header.
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="csv_database_write.csv"'
                writer = csv.writer(response)

                writer.writerow(
                    ['Source', 'Camera_Name', 'Camera_ID', 'Apple_HLS(public)', 'JPEG_URL(public)', 'Latitude',
                     'Longitude'])

                for channel in all_channels:
                    writer.writerow([channel.source, channel.camera_name, channel.camera_id,
                                     channel.apple_hls, channel.jpeg_url, channel.latitude,
                                     channel.longitude])

                return response

            source = query_data.get("source", None)
            if source is not None:
                title = query_data.get("title", None)

                data_dict = {
                    "source": source,
                    "camera_name": title,
                    "camera_id": query_data.get("id", None),
                    "apple_hls": None,
                    "jpeg_url": None,
                    "latitude": None,
                    "longitude": None
                }

                if source in ['Elko', 'Reno', 'Las Vegas']:
                    data_dict['apple_hls'] = query_data.get("apple_hls", None)
                    data_dict['jpeg_url'] = query_data.get("jpeg_url", None)
                    data_dict['latitude'] = query_data.get("latitude", None)
                    data_dict['longitude'] = query_data.get("longitude", None)

                elif source == "Link":
                    link = query_data.get("apple_hls", None)
                    data_dict['apple_hls'] = link
                    generate_thumbnails_url = generate_thumbnails(link, title + '.jpg', link=True)
                    data_dict['jpeg_url'] = generate_thumbnails_url

                elif source == "Video":
                    file = request.FILES["file"]
                    uploaded_file_url = uploaded_file(file, 'videos')
                    data_dict['apple_hls'] = uploaded_file_url
                    generate_thumbnails_url = generate_thumbnails(uploaded_file_url, file.name)
                    data_dict['jpeg_url'] = generate_thumbnails_url

                elif source == "Image":
                    file = request.FILES["file"]
                    uploaded_file_url = uploaded_file(file, 'images')
                    data_dict['apple_hls'] = uploaded_file_url
                    data_dict['jpeg_url'] = '/media/{}'.format(uploaded_file_url)

                try:
                    form = CCTVChannelForm(data_dict)
                    if form.is_valid():
                        form.save()
                    else:
                        logging.getLogger("error_logger").error(form.errors.as_json())
                except Exception as e:
                    logging.getLogger("error_logger").error(repr(e))
                    pass
            else:
                csv_file = request.FILES["csv_file"]
                if csv_file.name.endswith('.csv'):
                    file_data = csv_file.read().decode("utf-8")
                    lines = file_data.split("\n")

                    for line in lines[1:]:
                        try:
                            fields = line.split(",")
                            data_dict = {
                                "source": fields[0],
                                "camera_name": fields[1],
                                "camera_id": fields[2] or None,
                                "apple_hls": fields[3],
                                "jpeg_url": fields[4],
                                "latitude": fields[5] or None,
                                "longitude": fields[6] or None
                            }

                            form = CCTVChannelForm(data_dict)
                            if form.is_valid():
                                form.save()
                            else:
                                logging.getLogger("error_logger").error(form.errors.as_json())
                        except Exception as e:
                            logging.getLogger("error_logger").error(repr(e))
                            pass

        view_mode = request.GET.get('view') or "list"

        data_obj = Channel.objects.all().order_by("-id")
        page_obj = None

        try:
            paginator = Paginator(data_obj, len(data_obj)) if view_mode == 'list' else Paginator(data_obj, 6)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        except:
            pass

        context['channels'] = page_obj
        context['view'] = view_mode
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def channel_group(request):
    context = {}

    try:
        load_template = 'channel_group.html'

        if request.method == "POST":
            query_data = request.POST

            channel_id = query_data.get("channel_id", "")
            slot_name = query_data.get("slot_name", "")

            DBHelper.update_or_create_then_get_channel_group(channel_id, slot_name)

        channel_groups = DBHelper.get_or_create_channel_group()

        slots = [None, None, None, None, None, None]
        if channel_groups:
            groups = [channel_groups.slot1, channel_groups.slot2, channel_groups.slot3,
                      channel_groups.slot4, channel_groups.slot5, channel_groups.slot6]

            for i, group in enumerate(groups):
                slots[i] = {
                    "slot_name": 'slot{}'.format(i+1),
                    "slot_infer_id": 'infer{}'.format(i+1),
                    "channel_id": group.id,
                    "process_id": DBHelper.update_or_create_then_get_process(channel=group).id
                } if group else None

        context['slots'] = slots
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def outputs(request):
    context = {}
    try:
        load_template = 'outputs.html'

        output_id = request.GET.get('id', None)

        if request.method == 'POST' and output_id:
            # query_data = request.POST
            output = Output.objects.get(id=output_id)
            dir_path = Path(os.path.join(app_settings.MEDIA_ROOT, f'screenshots/{output.dir_name}'))

            try:
                model_config = ConfigChannel.objects.get(channel=output.channel)
            except:
                model_config = BaseConfig.objects.get(selected=True)

            object_remover = NoisyObjectRemover(Detector(Core(), model_config))

            screenshots = []
            for file in dir_path.iterdir():
                if file.is_file():
                    # screenshots
                    filename = os.path.join(dir_path, file.name)
                    if object_remover.is_removable(open_images_capture(filename, False)):
                        os.remove(filename)
                    else:
                        screenshots.append({
                            'name': file.name,
                            'size': ByteSize(file.stat().st_size),
                            'date_modified': datetime.utcfromtimestamp(file.stat().st_mtime).strftime(
                                '%Y-%m-%d %H:%M:%S')
                        })

            context['dir_name'] = output.dir_name
            context['screenshots'] = screenshots

        elif output_id:
            output = Output.objects.get(id=output_id)
            dir_path = Path(os.path.join(app_settings.MEDIA_ROOT, f'screenshots/{output.dir_name}'))

            screenshots = []
            for file in dir_path.iterdir():
                if file.is_file():
                    screenshots.append({
                        'name': file.name,
                        'size': ByteSize(file.stat().st_size),
                        'date_modified': datetime.utcfromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })

            context['channel'] = output.channel
            context['output_id'] = output_id
            context['dir_name'] = output.dir_name
            context['screenshots'] = screenshots
        else:
            try:
                output = Output.objects.all().order_by("-id")
                dir_path = Path(os.path.join(app_settings.MEDIA_ROOT, 'screenshots'))
                directories = []
                for directory in dir_path.iterdir():
                    if directory.is_dir():
                        for value in output:
                            if value.dir_name == directory.name:
                                directories.append({
                                    'id': value.id,
                                    'name': directory.name,
                                    'size': ByteSize(
                                        sum(f.stat().st_size for f in directory.glob('**/*') if f.is_file())),
                                    'date_modified': datetime.utcfromtimestamp(directory.stat().st_mtime).strftime(
                                        '%Y-%m-%d %H:%M:%S')
                                })
                                break
                context['directories'] = directories
            except:
                pass

        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def settings(request):
    context = {}
    try:
        load_template = 'settings.html'

        if request.method == 'POST' and 'modelConfigForm' in request.POST:
            query_data = request.POST
            model_id = query_data.get("model", 0)
            vehicle_th = query_data.get("vehicleTh", 0.5)
            vehicle_color = query_data.get("vehicleColor", "#000")
            bike_th = query_data.get("bikeTh", 0.5)
            bike_color = query_data.get("bikeColor", "#000")
            person_th = query_data.get("personTh", 0.5)
            person_color = query_data.get("personColor", "#000")

            models = AIModel.objects.get(id=model_id)
            BaseConfig.objects.update_or_create(selected=True, defaults={
                'model': models,
                'vehicle_threshold': vehicle_th,
                'vehicle_object_color': vehicle_color,
                'bike_threshold': bike_th,
                'bike_object_color': bike_color,
                'person_threshold': person_th,
                'person_object_color': person_color,
                'selected': True
            })

        if request.method == 'POST' and 'collisionConfigForm' in request.POST:
            query_data = request.POST
            collision_text = query_data.get("collisionText", "Collided")
            collision_color = query_data.get("collisionColor", "#FF2D00")
            near_miss_text = query_data.get("nearMissText", "Near Missed!!")
            near_miss_color = query_data.get("nearMissColor", "#FFAD00")
            collision_definition = query_data.get("collisionDefinition", 0)
            near_miss_definition = query_data.get("nearMissDefinition", 0)

            CollisionConfig.objects.update_or_create(selected=True, defaults={
                'collision_event_text': collision_text,
                'collision_box_color': collision_color,
                'near_miss_event_text': near_miss_text,
                'near_miss_box_color': near_miss_color,
                'collision_definition': collision_definition,
                'near_miss_definition': near_miss_definition,
                'selected': True
            })

        if request.method == 'POST' and 'graphConfigForm' in request.POST:
            query_data = request.POST
            GraphConfig.objects.update_or_create(selected=True, defaults={
                'update_every': query_data.get("update_every", 1),
                'vehicle_flow_label': query_data.get("vehicle_flow_label", "Vehicles"),
                'vehicle_flow_color': query_data.get("vehicle_flow_color", "#5eb5ef"),
                'bike_flow_label': query_data.get("bike_flow_label", "Bike"),
                'bike_flow_color': query_data.get("bike_flow_color", "#ffd878"),
                'person_flow_label': query_data.get("person_flow_label", "Pedestrians"),
                'person_flow_color': query_data.get("person_flow_color", "#ff829d"),
                'vehicle_analysis_label': query_data.get("vehicle_analysis_label", "Vehicles"),
                'vehicle_analysis_color': query_data.get("vehicle_analysis_color", "#5eb5ef"),
                'bike_analysis_label': query_data.get("bike_analysis_label", "Bike"),
                'bike_analysis_color': query_data.get("bike_analysis_color", "#ffd878"),
                'person_analysis_label': query_data.get("person_analysis_label", "Pedestrians"),
                'person_analysis_color': query_data.get("person_analysis_color", "#ff829d"),
                'collision_label': query_data.get("collision_label", "Collisions"),
                'collision_color': query_data.get("collision_color", "#FF2D00"),
                'nearmiss_label': query_data.get("nearmiss_label", "Near Miss"),
                'nearmiss_color': query_data.get("nearmiss_color", "#FFAD00"),
                'selected': True
            })

        ai_models = AIModel.objects.all().order_by("-id")
        model_config = BaseConfig.objects.get(selected=True)
        collision_config = CollisionConfig.objects.get(selected=True)

        try:
            graph_config = GraphConfig.objects.get(selected=True)
            context['graph_config'] = graph_config
        except:
            GraphConfig.objects.update_or_create(selected=True, defaults={
                'update_every': 1, 'vehicle_flow_label': "Vehicles", 'vehicle_flow_color': "#5eb5ef",
                'bike_flow_label': "Bike", 'bike_flow_color': "#ffd878", 'person_flow_label': "Pedestrians",
                'person_flow_color': "#ff829d", 'vehicle_analysis_label': "Vehicles",
                'vehicle_analysis_color': "#5eb5ef", 'bike_analysis_label': "Bike", 'bike_analysis_color': "#ffd878",
                'person_analysis_label': "Pedestrians", 'person_analysis_color': "#ff829d",
                'collision_label': "Collisions", 'collision_color': "#5eb5ef", 'nearmiss_label': "Near Miss",
                'nearmiss_color': "#ffd878", 'selected': True
            })
            graph_config = GraphConfig.objects.get(selected=True)
            context['graph_config'] = graph_config

        context['segment'] = load_template
        context['models'] = ai_models
        context['model_config'] = model_config
        context['collision_config'] = collision_config

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        print(e)
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
