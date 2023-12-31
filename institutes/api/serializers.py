from rest_framework import serializers
from ..models import InstituteProfile
from accounts.models import User
from ..models import Batch, Topic, Job, Application
from students.models import StudentProfile
from payments.models import UserPaymentDetail, StudentPayment


class InstituteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteProfile
        exclude = ("user",)


class InstituteSerializer(serializers.ModelSerializer):
    institute_profile = InstituteProfileSerializer(many=False)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "unique_code",
            "institute_profile",
        ]
        extra_kwargs = {"unique_code": {"read_only": True}}

    def validate_email(self, value):
        # Profile Updation
        if not self.instance is None:
            if User.objects.exclude(id=self.instance.id).filter(email=value).exists():
                raise serializers.ValidationError(
                    {"email": "This email is already in use."}
                )
            return value

        # New Institute Creating
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
        profile_data = validated_data.pop("institute_profile")
        InstituteProfileSerializer(data=profile_data, partial=True).update(
            instance=instance.institute_profile, validated_data=profile_data
        )
        return super().update(instance, validated_data)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, required=False)

    class Meta:
        model = Batch
        fields = (
            "id",
            "name",
            "start_date",
            "description",
            "institute_payment_detail",
            "batch_fees",
            "fee_penalty",
            "scheduled_date",
            "is_scheduled",
            "due_date",
            "topics",
        )


class InstitutePaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPaymentDetail
        fields = ("payment_number", "payment_qr", "payment_bank", "upi_id")


class UserStudentProfileSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    date_of_birth = serializers.CharField()

    class Meta:
        model = StudentProfile
        exclude = ("user", "id")
        depth = 1

    def validate_date_of_birth(self, value):
        return value.split("T")[0]


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


class StudentPaymentGETSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField()
    batch_name = serializers.CharField()

    class Meta:
        model = StudentPayment
        fields = (
            "student_name",
            "batch_name",
            "fee_amount",
            "fee_status",
            "payment_id",
            "payment_method",
            "is_notified",
        )


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "title",
            "requirements",
            "description",
            "category",
            "job_type",
            "company",
            "salary",
        )

    def validate_title(self, value):
        return value.title()

    def validate_job_type(self, value):
        return value.lower()

    def category(self, value):
        return value.lower()


class DashboardGETSerializer(serializers.Serializer):
    batch_count = serializers.IntegerField()
    student_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    this_month_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
