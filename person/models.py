from django.db import models
from django.core.validators import RegexValidator


class Insurance(models.Model):
    """
    Страховые компании
    """
    code = models.IntegerField(unique=True, db_column="Код")
    name = models.CharField("Название", max_length=255)

    class Meta:
        verbose_name = "Страховая компания"
        verbose_name_plural = "Страховые компании"

    def __str__(self):
        return f"{self.name} - {self.code}"


class InsurancePolicy(models.Model):
    """
    Страховые полиса
    """
    enp = models.CharField("ЕНП", max_length=16, unique=True)
    start_date = models.DateField("Дата_начала_страхования")
    end_date = models.DateField("Дата_окончания_страхования", null=True, blank=True)
    insurance = models.ForeignKey(
        Insurance,
        on_delete=models.PROTECT,
        db_column="Код_СМО",
        verbose_name="Страховая организация"
    )

    class Meta:
        verbose_name = "Полис"
        verbose_name_plural = "Полисы"
        indexes = [
            models.Index(fields=['enp']),
        ]

    def __str__(self):
        return f'{self.enp}: {self.start_date} - {self.end_date}'


class PhysicalPerson(models.Model):
    """
    Физические лица
    """
    last_name = models.CharField("Фамилия", max_length=255)
    first_name = models.CharField("Имя", max_length=255)
    middle_name = models.CharField("Отчество", max_length=255)
    birth_date = models.DateField("Дата_рождения")
    gender = models.CharField("Пол", max_length=1, choices=(('М', 'М'), ('Ж', 'Ж')))
    snils = models.CharField(
        "СНИЛС",
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{11}$',
                message="СНИЛС должен состоять из 11 цифр"
            )
        ]
    )
    phone = models.CharField(
        "Телефон",
        max_length=11,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^8[0-9]{10}$',
                message="Телефон должен начинаться с 8 и содержать 11 цифр"
            )
        ]
    )
    telegram = models.BigIntegerField("Телеграм", null=True, blank=True)
    # Теперь может быть несколько полисов для одного физического лица.
    policies = models.ManyToManyField(
        InsurancePolicy,
        blank=True,
        verbose_name="Полисы",
        related_name="physical_persons"
    )

    class Meta:
        verbose_name = "Физическое лицо"
        verbose_name_plural = "Физические лица"
        indexes = [
            models.Index(
                fields=['last_name', 'birth_date', 'snils', 'phone'],
            ),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
