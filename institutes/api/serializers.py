from rest_framework import serializers
from ..models import InstituteProfile
from accounts.models import User
from ..models import Batch, Topic
from students.models import StudentProfile


class InstituteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteProfile
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}}


class InstituteSerializer(serializers.ModelSerializer):
    profile = InstituteProfileSerializer()
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)
    institute_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "institute_name",
            "email",
            "phone_number",
            "unique_code",
            "profile",
        ]
        extra_kwargs = {"unique_code": {"read_only": True}}

    def validate_email(self, value):
        user = self.context["user"]
        if User.objects.exclude(pk=user.id).filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email is already in use."}
            )
        return value

    def validate_phone_number(self, value):
        user = self.context["user"]
        if User.objects.exclude(pk=user.id).filter(phone_number=value).exists():
            raise serializers.ValidationError(
                {"email": "This Phone Number is already in use."}
            )
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user = User.objects.create(**validated_data)
        InstituteProfile.objects.create(user=user, **profile_data)
        return user


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, required=False)

    class Meta:
        model = Batch
        fields = "__all__"
        read_only_fields = ("institute",)


class UserStudentProfileSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        exclude = ("user", "id")
        depth = 1


class UserStudentSerializer(serializers.ModelSerializer):
    student_profile = UserStudentProfileSerializer(many=False, required=False)
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_student",
            "unique_code",
            "student_profile",
        )
        read_only_fields = ("id", "is_student")

    def validate_email(self, value):
        # Profile Updation
        if not self.instance is None:
            if User.objects.exclude(id=self.instance.id).filter(email=value).exists():
                raise serializers.ValidationError(
                    {"email": "This email is already in use."}
                )
            return value

        # New User Creating
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email is already in use."}
            )
        return value

    def validate_phone_number(self, value):
        # Profile Updation
        if not self.instance is None:
            if (
                User.objects.exclude(id=self.instance.id)
                .filter(phone_number=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    {"phone_number": "This Phone Number is already in use."}
                )
            return value

        # New User Creating
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                {"phone_number": "This Phone Number is already in use."}
            )
        return value

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("student_profile", {})
        UserStudentProfileSerializer(data=profile_data).update(
            instance=instance.student_profile, validated_data=profile_data
        )
        return super().update(instance, validated_data)
