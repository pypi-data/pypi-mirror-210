from copy import deepcopy

from NEMO.models import User
from NEMO.serializers import ModelSerializer, UserSerializer
from NEMO.views.api import UserViewSet
from rest_framework.fields import CharField

from NEMO_user_details.customizations import UserDetailsCustomization
from NEMO_user_details.models import UserDetails, get_user_details


class UserDetailsSerializer(ModelSerializer):
    gender_name = CharField(source="gender.name", default=None, read_only=True)
    race_name = CharField(source="race.name", default=None, read_only=True)
    ethnicity_name = CharField(source="ethnicity.name", default=None, read_only=True)

    def get_fields(self):
        fields = super().get_fields()
        disable_fields, require_fields = UserDetailsCustomization.disable_require_fields()
        for disable_field in disable_fields:
            if disable_field in fields:
                del fields[disable_field]
        for require_field in require_fields:
            fields[require_field].required = True
            fields[require_field].allow_blank = False
        return fields

    class Meta:
        model = UserDetails
        exclude = ("user",)


class UserWithDetailsSerializer(UserSerializer):
    details = UserDetailsSerializer(required=False)

    def get_fields(self):
        fields = super().get_fields()
        detail_fields = fields.pop("details")
        if detail_fields:
            for key, value in detail_fields.fields.items():
                if key != "id":
                    # reset the source to details
                    value.source = "details." + value.source
                    value.source_attrs = value.source.split(".")
                    fields[key] = value
        return fields

    def validate(self, attrs):
        attributes_data = dict(attrs)
        details_attrs = attributes_data.pop("details")
        super().validate(attributes_data)
        user_details = get_user_details(self.instance)
        for details_attr, details_value in details_attrs.items():
            setattr(user_details, details_attr, details_value)
        UserDetailsSerializer().full_clean(user_details, exclude=["user"])
        return attrs

    def update(self, instance, validated_data) -> User:
        data = deepcopy(validated_data)
        details_data = data.pop("details")
        user_instance = super().update(instance, data)
        user_details = get_user_details(user_instance)
        UserDetailsSerializer().update(user_details, details_data)
        return user_instance

    def create(self, validated_data) -> User:
        data = deepcopy(validated_data)
        details_data = data.pop("details")
        user_instance = super().create(data)
        details_data["user"] = user_instance
        UserDetailsSerializer().create(details_data)
        return user_instance


class UserWithDetailsViewSet(UserViewSet):
    serializer_class = UserWithDetailsSerializer
