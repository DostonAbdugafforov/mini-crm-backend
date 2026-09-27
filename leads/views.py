from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import LeadFilter
from .models import Lead, LeadActivity
from .serializers import LeadSerializer, LeadStatusUpdateSerializer, LeadActivitySerializer
from .pagination import StandardResultsPagination


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    filterset_class = LeadFilter
    search_fields = ["name", "phone", "email", "note"]
    ordering_fields = ["created_at", "updated_at", "name", "status"]

    def get_queryset(self):
        # Hozircha hamma autentifikatsiyadan o'tgan user barcha leadlarni ko'radi
        # (jamoaviy CRM stsenariysi). Agar faqat o'z leadlarini ko'rish kerak
        # bo'lsa, bu yerga .filter(owner=self.request.user) qo'shiladi.
        return Lead.objects.select_related("owner").all()

    # ---- standart formatga o'ralgan CRUD javoblari ----

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"success": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "data": None}, status=status.HTTP_200_OK)

    # ---- activity log bilan bog'liq override'lar ----

    def perform_create(self, serializer):
        lead = serializer.save(owner=self.request.user)
        LeadActivity.objects.create(
            lead=lead,
            lead_id_snapshot=lead.id,
            lead_name_snapshot=lead.name,
            user=self.request.user,
            action=LeadActivity.Action.CREATED,
            new_value=lead.status,
        )

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_values = {
            "name": old_instance.name, "phone": old_instance.phone,
            "email": old_instance.email, "source": old_instance.source,
            "note": old_instance.note,
        }
        lead = serializer.save()

        changed = []
        new_values = {
            "name": lead.name, "phone": lead.phone,
            "email": lead.email, "source": lead.source,
            "note": lead.note,
        }
        for field, old_val in old_values.items():
            if old_val != new_values[field]:
                changed.append(field)

        if changed:
            LeadActivity.objects.create(
                lead=lead,
                lead_id_snapshot=lead.id,
                lead_name_snapshot=lead.name,
                user=self.request.user,
                action=LeadActivity.Action.UPDATED,
                old_value=", ".join(changed),
                new_value="updated",
            )

    def perform_destroy(self, instance):
        # Lead o'chirilishidan oldin DELETED action'ini yozib qo'yamiz,
        # snapshot maydonlari tufayli lead o'chsa ham tarix saqlanadi.
        LeadActivity.objects.create(
            lead=None,
            lead_id_snapshot=instance.id,
            lead_name_snapshot=instance.name,
            user=self.request.user,
            action=LeadActivity.Action.DELETED,
            old_value=instance.status,
        )
        instance.delete()

    # ---- status o'zgartirish uchun alohida endpoint ----

    @action(detail=True, methods=["patch"], url_path="status")
    def change_status(self, request, pk=None):
        lead = self.get_object()
        serializer = LeadStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = lead.status
        new_status = serializer.validated_data["status"]

        if old_status == new_status:
            return Response(
                {"success": True, "data": LeadSerializer(lead).data}
            )

        lead.status = new_status
        lead.save(update_fields=["status", "updated_at"])

        LeadActivity.objects.create(
            lead=lead,
            lead_id_snapshot=lead.id,
            lead_name_snapshot=lead.name,
            user=request.user,
            action=LeadActivity.Action.STATUS_CHANGED,
            old_value=old_status,
            new_value=new_status,
        )
        return Response({"success": True, "data": LeadSerializer(lead).data})

    # ---- activity tarixi ----

    @action(detail=True, methods=["get"], url_path="activity")
    def activity(self, request, pk=None):
        lead = self.get_object()
        queryset = lead.activities.select_related("user").all()

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = LeadActivitySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)