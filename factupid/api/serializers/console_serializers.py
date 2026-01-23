from rest_framework import serializers
from django.contrib.auth.models import User,Group,Permission
from console.models import Customer, SelectedService, Service, Service_Plan, SupplierStamp, Plan, Post, User_Service

#Serializer para los models de la app de Console
class SupplierStampSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierStamp
        fields = '__all__'


class ServicePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_Plan
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class UserServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Service
        fields = '__all__'


class SelectedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedService
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        
#Serializer para los modelos de permisos y grupos de Django
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id","codename","name","content_type"]

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id","name"]

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    user_permissions = PermissionSerializer(many=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_staff", "is_active", "is_superuser", "groups", "user_permissions"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        group_permissions = Permission.objects.filter(group__user=instance).distinct()
        group_permissions_serializer = PermissionSerializer(group_permissions, many=True)
        representation['user_permissions'] += group_permissions_serializer.data
        return representation