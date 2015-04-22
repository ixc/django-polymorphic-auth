# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polymorphic_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailUser',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polymorphic_auth.User')),
                ('email', models.EmailField(help_text='Required. Unique.', unique=True, max_length=254, verbose_name='email address', error_messages={b'unique': 'A user with that email address already exists.'})),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user with email login',
                'verbose_name_plural': 'users with email login',
            },
            bases=('polymorphic_auth.user', models.Model),
        ),
    ]
