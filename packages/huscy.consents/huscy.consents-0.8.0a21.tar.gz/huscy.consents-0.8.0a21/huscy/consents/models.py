from django.db import models


class AbstractConsentCategory(models.Model):
    name = models.CharField(max_length=128)
    template_text_fragments = models.JSONField()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class ConsentCategory(AbstractConsentCategory):
    pass


class AbstractConsent(models.Model):
    text_fragments = models.JSONField()
    version = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True


class Consent(AbstractConsent):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


def get_consent_file_upload_path(instance, filename):
    return f'consents/{filename}'


class AbstractConsentFile(models.Model):
    consent_version = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    filehandle = models.FileField(upload_to=get_consent_file_upload_path)

    class Meta:
        abstract = True


class ConsentFile(AbstractConsentFile):
    consent = models.ForeignKey(Consent, on_delete=models.PROTECT)
