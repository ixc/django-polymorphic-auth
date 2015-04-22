# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import polymorphic_auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('polymorphic_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsernameUser',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polymorphic_auth.User')),
                ('email', models.EmailField(help_text='Required. Unique.', unique=True, max_length=254, verbose_name='email address', error_messages={b'unique': 'A user with that email address already exists.'})),
                ('username', models.CharField(error_messages={b'unique': 'A user with that username already exists.'}, max_length=255, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'This field is invalid.', b'invalid')], help_text='Required. Unique. Must contain only letters, digits and @.+-_ characters.', unique=True, verbose_name='username')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user with username login',
                'verbose_name_plural': 'users with username login',
            },
            bases=(polymorphic_auth.models.UsernameMethodsMixin, 'polymorphic_auth.user', models.Model),
        ),
    ]
