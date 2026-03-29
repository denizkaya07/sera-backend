from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('engineer', 'Mühendis'),
                    ('farmer', 'Çiftçi'),
                    ('dealer', 'Bayi'),
                    ('producer', 'Üretici Firma'),
                ],
                blank=True,
                default='',
            ),
        ),
    ]
