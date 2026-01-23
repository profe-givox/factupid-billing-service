from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cfdi', '0087_alter_informacionfiscal_calle_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFPersonalizado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('html', models.TextField()),
                ('css', models.TextField(blank=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pdf_personalizados/')),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='pdf_personalizados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
                'unique_together': {('created_by', 'name')},
            },
        ),
    ]
