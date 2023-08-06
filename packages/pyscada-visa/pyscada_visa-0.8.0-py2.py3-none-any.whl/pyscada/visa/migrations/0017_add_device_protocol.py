# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.visa import PROTOCOL_ID
from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    db_alias = schema_editor.connection.alias
    DeviceProtocol.objects.using(db_alias).update_or_create(protocol='visa',
                                                            defaults={'pk': PROTOCOL_ID,
                                                                      'description': 'VISA Device',
                                                                      'app_name': 'pyscada.visa',
                                                                      'device_class': 'pyscada.visa.device',
                                                                      'daq_daemon': True,
                                                                      'single_thread': True}
                                                            )


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    db_alias = schema_editor.connection.alias
    DeviceProtocol.objects.using(db_alias).filter(protocol="visa").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('visa', '0016_alter_visadevice_resource_name'),
        ('pyscada', '0041_update_protocol_id'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
