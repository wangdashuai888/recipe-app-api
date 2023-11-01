"""
serializers for recipe api
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """serializer for recipe objects"""

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link',
        ]
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """serializer for recipe detail objects"""
    description = serializers.CharField(required=False)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
