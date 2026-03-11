from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('featured', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='featuredproduct',
            name='ends_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='featuredproduct',
            name='starts_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]