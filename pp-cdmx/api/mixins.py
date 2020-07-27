from rest_framework import viewsets, mixins, generics
class MultiSerializerViewSet(viewsets.GenericViewSet):
    def get_serializer_class(self):
        if hasattr(self, "action_serializers"):
            try:
                return self.action_serializers.get(self.action,
                    self.serializer_class)
            except Exception as e:
                pass
        return super(MultiSerializerViewSet, self).get_serializer_class()

class MultiSerializerListRetrieveMix(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    MultiSerializerViewSet):
    pass

class MultiSerializerListRetrieveUpdateMix(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    MultiSerializerViewSet):
    pass

class MultiSerializerListCreateRetrieveUpdateMix(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    MultiSerializerViewSet):
    pass

class MultiSerializerCreateRetrieveMix(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    MultiSerializerViewSet):
    pass

class ListMix(
    mixins.ListModelMixin,
    MultiSerializerViewSet):
    pass

class CreateMix(
    mixins.CreateModelMixin,
    MultiSerializerViewSet):
    pass

class ListCreateAPIView(
    generics.ListCreateAPIView,
    MultiSerializerViewSet):
    pass

class MultiSerializerModelViewSet(
    viewsets.ModelViewSet,
    MultiSerializerViewSet):
    pass
