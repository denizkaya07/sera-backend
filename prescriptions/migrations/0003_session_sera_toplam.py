import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prescriptions', '0002_add_farm_items'),
    ]

    operations = [
        # 1) PrescriptionSession tablosu oluştur
        migrations.CreateModel(
            name='PrescriptionSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sira', models.PositiveIntegerField(default=1)),
                ('tarih', models.DateField(blank=True, null=True)),
                ('prescription', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sessions',
                    to='prescriptions.prescription',
                )),
            ],
            options={'ordering': ['sira']},
        ),

        # 2) PrescriptionItem.prescription → nullable yap
        migrations.AlterField(
            model_name='prescriptionitem',
            name='prescription',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='prescriptions.prescription',
            ),
        ),

        # 3) PrescriptionItem'a session FK ekle
        migrations.AddField(
            model_name='prescriptionitem',
            name='session',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='prescriptions.prescriptionsession',
            ),
        ),

        # 4) sera_toplam alanı ekle
        migrations.AddField(
            model_name='prescriptionitem',
            name='sera_toplam',
            field=models.CharField(blank=True, default='', max_length=100),
        ),

        # 5) uygulama_tipi choices genişlet (blank=True)
        migrations.AlterField(
            model_name='prescriptionitem',
            name='uygulama_tipi',
            field=models.CharField(
                blank=True, default='', max_length=20,
                choices=[
                    ('yapraktan', 'Yapraktan'),
                    ('topraktan', 'Topraktan'),
                    ('sulamayla', 'Sulamayla'),
                    ('damla_sulama', 'Damla Sulama'),
                    ('yagmurlama', 'Yagmurlama'),
                ],
            ),
        ),
    ]
