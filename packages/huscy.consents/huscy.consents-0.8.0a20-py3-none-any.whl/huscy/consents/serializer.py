from rest_framework.serializers import ModelSerializer

from .models import Consent, ConsentCategory
from .services import (create_consent, create_consent_category,
                       update_consent, update_consent_category)


class ConsentCategorySerializer(ModelSerializer):
    class Meta:
        model = ConsentCategory
        fields = 'id', 'name', 'template_text_fragments'

    def create(self, validated_data):
        return create_consent_category(**validated_data)

    def update(self, consent_category, validated_data):
        return update_consent_category(consent_category, **validated_data)


class ConsentSerializer(ModelSerializer):
    class Meta:
        model = Consent
        fields = 'id', 'name', 'text_fragments'

    def create(self, validated_data):
        return create_consent(**validated_data)

    def update(self, consent, validated_data):
        return update_consent(consent, **validated_data)
