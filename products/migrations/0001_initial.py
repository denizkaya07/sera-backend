from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('urun_tipi', models.CharField(choices=[('ilac', 'Ilac'), ('gubre', 'Gubre'), ('diger', 'Diger')], default='ilac', max_length=20)),
                ('etken_madde', models.CharField(blank=True, default='', max_length=255)),
                ('doz', models.CharField(blank=True, default='', max_length=100)),
                ('kullanim_amaci', models.TextField(blank=True, default='')),
                ('uretici', models.CharField(blank=True, default='', max_length=255)),
                ('ozellikler', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_products', to='users.user')),
            ],
        ),
    ]
