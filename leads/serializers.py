from rest_framework import serializers

from .models import Lead, LeadActivity, LeadStatus


class LeadSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id", "name", "phone", "email", "source", "status", "note",
            "owner", "owner_username", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate(self, attrs):
        # update paytida attrs faqat o'zgargan maydonlarni o'z ichiga oladi,
        # shuning uchun mavjud instance qiymatlaridan fallback qilamiz.
        phone = attrs.get("phone", getattr(self.instance, "phone", None))
        email = attrs.get("email", getattr(self.instance, "email", None))
        if not phone and not email:
            raise serializers.ValidationError(
                "phone yoki email kamida bittasi kiritilishi shart."
            )
        return attrs


class LeadStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=LeadStatus.choices)


class LeadActivitySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = LeadActivity
        fields = [
            "id", "action", "old_value", "new_value",
            "user_username", "created_at",
        ]
        read_only_fields = fields