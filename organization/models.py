from django.db import models


class Organization(models.Model):
    name = models.CharField("Название организации", max_length=255)
    address = models.TextField("Адрес")
    phone_number = models.CharField("Номер телефона", max_length=20)
    email = models.EmailField("Электронная почта")
    code_mo = models.CharField("Код МО в СМО", max_length=20, blank=True, null=True)
    oid_mo = models.CharField("OID МО", max_length=50)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return f"{self.name} ({self.code_mo or 'без кода МО'})"


class MOConfiguration(models.Model):
    """
    Модель для выбора конкретной МО (медицинской организации),
    используемой в установленной версии, и хранения конфигурации в формате JSON.
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        verbose_name="Выбранная МО"
    )
    configuration = models.JSONField("Конфигурация", blank=True, null=True)

    class Meta:
        verbose_name = "Конфигурация МО"
        verbose_name_plural = "Конфигурации МО"

    def __str__(self):
        return f"Конфигурация для {self.organization}"


class Building(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='buildings',
        verbose_name="Организация"
    )
    name = models.CharField("Название корпуса", max_length=255)
    additional_name = models.CharField("Дополнительное название корпуса", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпусы"

    def __str__(self):
        additional = f" - {self.additional_name}" if self.additional_name else ""
        return f"{self.name}{additional}"


class Department(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name="Корпус"
    )
    name = models.CharField("Название отделения", max_length=255)
    additional_name = models.CharField("Дополнительное название отделения", max_length=255, blank=True, null=True)
    # Поле для связи с внешними системами
    external_id = models.CharField("Идентификатор из внешней системы", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделения"

    def __str__(self):
        return f"{self.name} ({self.building.name})"


class RelatedDepartment(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='oms_departments',
        verbose_name="Отделение"
    )
    name = models.CharField("Название отделения", max_length=255)
    # Добавляем поле «Источник»
    source = models.CharField("Источник", max_length=255)
    # Поле для хранения файлов или настроек конфигурации в формате JSON
    configuration = models.JSONField("Конфигурация", blank=True, null=True)

    class Meta:
        verbose_name = "Отделение: связанное"
        verbose_name_plural = "Отделения: связанные"

    def __str__(self):
        return f"{self.name} (Web-ОМС)"


class Station(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name="Отделение"
    )
    code = models.CharField("Код участка", max_length=255)
    name = models.CharField("Название участка", max_length=255, blank=True, null=True)
    open_date = models.DateField("Дата введения участка", blank=True, null=True)
    close_date = models.DateField("Дата закрытия участка", blank=True, null=True)

    class Meta:
        verbose_name = "Участок"
        verbose_name_plural = "Участки"

    def __str__(self):
        return f"{self.name} ({self.department})"
