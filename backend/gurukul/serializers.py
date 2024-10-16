from django.contrib.auth.models import User
from .models import Classrooms, Classmodule, Feed, Students, Teachers, Assignments, QnA, Announcements, Submission_base, Submissions, QSubmissions
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.exceptions import ValidationError

class ClassroomsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classrooms
        fields = '__all__'

    # def validate_email(self, value):
    #     """
    #     Ensure the email ends with @example.com.
    #     """
    #     if not value.endswith('@example.com'):
    #         raise ValidationError("Email must end with @example.com")
    #     return value.lower()

    # def create(self, validated_data):
    #     user = User(
    #         email=validated_data['email'],
    #         username=validated_data['username']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user
class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'


# Serializer for Students model
class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'


# Serializer for Teachers model
class TeachersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = '__all__'


# Serializer for Assignments model
class AssignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignments
        fields = '__all__'


# Serializer for QnA model
class QnASerializer(serializers.ModelSerializer):
    class Meta:
        model = QnA
        fields = '__all__'


# Serializer for Announcements model
class AnnouncementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcements
        fields = '__all__'


# Serializer for Submissions model
class SubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submissions
        fields = '__all__'


# Serializer for QSubmissions model
class QSubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QSubmissions
        fields = '__all__'
