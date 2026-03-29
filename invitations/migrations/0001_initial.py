from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('farms', '0002_add_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Bekliyor'), ('accepted', 'Kabul Edildi'), ('rejected', 'Reddedildi')], default='pending', max_length=20)),
                ('message', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to='users.user')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_invitations', to='users.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='invitation',
            constraint=models.UniqueConstraint(fields=('sender', 'receiver'), name='unique_invitation'),
        ),
        migrations.CreateModel(
            name='FarmPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('year', models.IntegerField(default=2026)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('invitation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='invitations.invitation')),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='farms.farm')),
            ],
        ),
        migrations.CreateModel(
            name='FarmNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='farms.farm')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
        ),
    ]
