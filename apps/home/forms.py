# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from .models import Channel


class CCTVChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CCTVChannelForm, self).__init__(*args, **kwargs)

