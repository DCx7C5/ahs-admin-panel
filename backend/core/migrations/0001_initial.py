# Generated by Django 5.1.5 on 2025-01-16 00:20

import backend.core.models.mixins
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('address', models.GenericIPAddressField(protocol='IPv4', unique=True, verbose_name='host ip address')),
                ('name', models.CharField(blank=True, max_length=253, unique=True, verbose_name='hostname')),
                ('remote', models.BooleanField(verbose_name='is remote host')),
            ],
            options={
                'verbose_name': 'host',
                'verbose_name_plural': 'hosts',
            },
            bases=(models.Model, backend.core.models.mixins.CreationDateMixin, backend.core.models.mixins.UpdateDateMixin),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=256)),
                ('tld', models.CharField()),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.host')),
            ],
            options={
                'verbose_name': 'Domain Name',
                'verbose_name_plural': 'Domain Names',
            },
            bases=(models.Model, backend.core.models.mixins.CreationDateMixin, backend.core.models.mixins.UpdateDateMixin),
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The display name of the menu item.', max_length=64, verbose_name='Name')),
                ('path', models.URLField(help_text='The URL or path this menu item links to.', max_length=128, verbose_name='Path')),
                ('icon', models.CharField(blank=True, help_text='Optional icon class or identifier for the menu item.', max_length=50, null=True, verbose_name='Icon')),
                ('order', models.IntegerField(default=0, help_text='Order in which this item appears in the menu. Lower numbers appear first.', verbose_name='Order')),
                ('active', models.BooleanField(default=True, help_text='Whether this menu item is currently active and should be displayed.', verbose_name='Active')),
                ('app_label', models.CharField(blank=True, help_text='The app label for this menu item. This should match the app label of the app containing the viewset.', max_length=42, null=True, verbose_name='App Label')),
                ('parent', models.ForeignKey(blank=True, help_text='Parent menu item for nested or hierarchical menus.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.menuitem', verbose_name='Parent')),
            ],
            options={
                'verbose_name': 'Menu Item',
                'verbose_name_plural': 'Menu Items',
                'ordering': ['order', 'name'],
            },
            bases=(models.Model, backend.core.models.mixins.TreeMixin),
        ),
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=256)),
                ('default', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workspaces', related_query_name='workspace', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Workspace',
                'verbose_name_plural': 'Workspaces',
            },
        ),
        migrations.AddField(
            model_name='host',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.workspace'),
        ),
    ]
