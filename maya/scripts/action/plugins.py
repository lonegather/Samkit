# -*- coding:utf-8 -*-
import json
from maya import cmds
import pyblish.api


def get_context(key=None):
    task_info = cmds.fileInfo('samkit_context', q=True)
    task_info = task_info[0].replace(r'\"', '"').replace(r'\\\\', r'\\') if task_info else '{}'
    task = json.loads(task_info)
    return task.get(key, None) if key else task


class EntityCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder

    def process(self, context):
        task = get_context()
        context.set_data('label', task['path'])
        instance = context.create_instance(task['entity'])
        instance.data['families'] = [task['stage']]
        instance.data['family'] = task['stage']


class ModelHistoryValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder
    label = 'Validate Model History'
    families = ['mdl']

    def process(self, instance):
        from pprint import pprint
        pprint(instance.data)
