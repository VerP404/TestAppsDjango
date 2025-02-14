# Generated by Django 5.1.6 on 2025-02-14 07:47

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(unique=True, verbose_name='Код')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Страховую компанию',
                'verbose_name_plural': 'Страховые компании',
            },
        ),
        migrations.CreateModel(
            name='PhysicalPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=255, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=255, verbose_name='Имя')),
                ('middle_name', models.CharField(default='-', max_length=255, verbose_name='Отчество')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('gender', models.CharField(choices=[('М', 'М'), ('Ж', 'Ж')], max_length=1, verbose_name='Пол')),
                ('snils', models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(message='СНИЛС должен состоять из 11 цифр', regex='^[0-9]{11}$')], verbose_name='СНИЛС')),
                ('phone', models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(message='Телефон должен начинаться с 8 и содержать 11 цифр', regex='^8[0-9]{10}$')], verbose_name='Телефон')),
                ('telegram', models.BigIntegerField(blank=True, null=True, verbose_name='Телеграм')),
            ],
            options={
                'verbose_name': 'Физическое лицо',
                'verbose_name_plural': 'Физические лица',
                'constraints': [models.UniqueConstraint(condition=models.Q(('snils__isnull', False)), fields=('snils',), name='unique_snils')],
            },
        ),
        migrations.CreateModel(
            name='InsurancePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enp', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='ЕНП должен состоять из 16 цифр', regex='^[0-9]{16}$')], verbose_name='ЕНП')),
                ('start_date', models.DateField(verbose_name='Дата начала страхования')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания страхования')),
                ('insurance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='person.insurance', verbose_name='Страховая организация')),
                ('physical_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='policies', to='person.physicalperson', verbose_name='Физическое лицо')),
            ],
            options={
                'verbose_name': 'Полис',
                'verbose_name_plural': 'Полисы',
                'indexes': [models.Index(fields=['enp'], name='person_insu_enp_f979b5_idx')],
            },
        ),
        migrations.CreateModel(
            name='AttachmentPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enp', models.CharField(blank=True, max_length=16, null=True, verbose_name='ЕНП')),
                ('smo', models.CharField(blank=True, max_length=50, null=True, verbose_name='СМО')),
                ('start_date', models.DateField(verbose_name='Дата начала прикрепления')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания прикрепления')),
                ('report_date', models.DateField(verbose_name='Дата отчёта')),
                ('station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='organization.station', verbose_name='Участок')),
                ('physical_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.physicalperson', verbose_name='Физическое лицо')),
            ],
            options={
                'verbose_name': 'Прикрепление (интервал)',
                'verbose_name_plural': 'Прикрепления (интервалы)',
                'indexes': [models.Index(fields=['report_date'], name='person_atta_report__517099_idx'), models.Index(fields=['enp'], name='person_atta_enp_d9b79a_idx')],
            },
        ),
    ]
