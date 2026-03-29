from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='farm',
            name='isletme_tipi',
            field=models.CharField(blank=True, choices=[('sera', 'Sera'), ('bahce', 'Bahce'), ('tarla', 'Tarla'), ('fidelik', 'Fidelik'), ('diger', 'Diger')], default='sera', max_length=20),
        ),
        migrations.AddField(
            model_name='farm',
            name='il',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='farm',
            name='ilce',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='farm',
            name='mahalle',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='farm',
            name='sera_tipi',
            field=models.CharField(blank=True, choices=[('cam', 'Cam Sera'), ('plastik', 'Plastik Sera'), ('polykarbon', 'Polykarbon Sera'), ('diger', 'Diger')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='farm',
            name='buyukluk',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='farm',
            name='urun_tipi',
            field=models.CharField(blank=True, choices=[('domates', 'Domates'), ('biber', 'Biber'), ('salatalik', 'Salatalik'), ('patlican', 'Patlican'), ('marul', 'Marul'), ('diger', 'Diger')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='farm',
            name='urun_cesidi',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='farm',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]