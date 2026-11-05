from django.db import migrations


def create_default_classrooms(apps, schema_editor):
    classroom_model = apps.get_model('core', 'ClassRoom')
    classrooms = (
        ('Crèche', 'creche'),
        ('Petite Section', 'maternelle'),
        ('Moyenne Section', 'maternelle'),
        ('Grande Section', 'maternelle'),
    )
    for name, section_type in classrooms:
        classroom_model.objects.get_or_create(
            name=name,
            section_type=section_type,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_default_classrooms,
            migrations.RunPython.noop,
        ),
    ]
