from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prescriptions', '0001_initial'),
        ('farms', '0002_add_fields'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='farm',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='prescriptions',
                to='farms.farm'
            ),
        ),
        migrations.CreateModel(
            name='PrescriptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('sira', models.PositiveIntegerField(default=1)),
                ('uygulama_tipi', models.CharField(
                    choices=[('yapraktan', 'Yapraktan'), ('topraktan', 'Topraktan'), ('sulamayla', 'Sulamayla')],
                    default='sulamayla', max_length=20
                )),
                ('urun_adi', models.CharField(blank=True, default='', max_length=255)),
                ('doz', models.CharField(blank=True, default='', max_length=100)),
                ('not_field', models.TextField(blank=True, default='')),
                ('prescription', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='prescriptions.prescription'
                )),
                ('product', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='prescription_items',
                    to='products.product'
                )),
            ],
            options={'ordering': ['sira']},
        ),
    ]
