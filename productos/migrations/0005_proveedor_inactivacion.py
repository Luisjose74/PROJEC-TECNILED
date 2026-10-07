import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0004_proveedor_contacto_proveedor_direccion'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='motivo_inactivacion',
            field=models.TextField(blank=True, verbose_name='Motivo de inactivación'),
        ),
        migrations.AddField(
            model_name='proveedor',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]