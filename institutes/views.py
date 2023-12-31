from rest_framework.views import APIView

from .api.serializers import (
    InstituteSerializer,
    BatchSerializer,
    UserStudentSerializer,
    JobCreateUpdateSerializer,
    InstitutePaymentDetailSerializer,
    DashboardGETSerializer,
    StudentPaymentGETSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import InstituteProfile, Job
from accounts.models import User
from .models import Batch
from django.shortcuts import get_object_or_404
from students.models import StudentProfile
from django.db.models import Q
from accounts.helpers.password_generator import generate_random_password
from django.core.mail import EmailMessage
from drf_yasg.utils import swagger_auto_schema
from accounts.models import User
from django.db.models import F, Count, Sum
from datetime import date
from payments.models import UserPaymentDetail
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from payments.models import StudentPayment
from .pagination import SmallResultPagination
from payments.api.serializers import StudentPaymentPostSerailizer
from django.utils import timezone


class InstituteProfileGetUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @swagger_auto_schema(
        tags=["Institute Profile"],
        operation_description="Institute Profile",
        responses={
            200: InstituteSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        serializer = InstituteSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Profile"],
        operation_description="Institute Profile Updation",
        request_body=InstituteSerializer,
        responses={
            200: InstituteSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def put(self, request, *args, **kwargs):
        serializer = InstituteSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Profile"],
        operation_description="Institute Profile",
        responses={
            200: InstituteSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = User.objects.filter(id=request.user.id).first()
        if instance:
            instance.delete()
            return Response(
                {"msg": "Institute Profile Deleted Successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        return Response({"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


class BatchListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Fetch",
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        # In this request user is institute
        # Based on institute i am filter their batches only
        # or else other institute can see other institute batches
        search = request.GET.get("search", None)
        scheduled = request.GET.get("scheduled", None)
        sort = request.GET.get("sort", "name")
        Q_filter = Q(institute__user_id=request.user.id)
        if search:
            Q_filter &= Q(name__istartswith=search)
        if scheduled:
            Q_filter &= Q(is_scheduled=True)
        match sort:
            case "desc":
                order_by = "-name"
            case "fee_asc":
                order_by = "batch_fees"
            case "fee_desc":
                order_by = "-batch_fees"
            case _:
                order_by = "name"
        instance = Batch.objects.filter(Q_filter).order_by(order_by)
        paginator = SmallResultPagination()
        queryset = paginator.paginate_queryset(instance, request)
        serializer = BatchSerializer(queryset, many=True)
        response_data = {
            "total_page": paginator.page.paginator.num_pages,
            "batch": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Creation",
        request_body=BatchSerializer,
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        institute = get_object_or_404(InstituteProfile, user=request.user)
        serializer = BatchSerializer(data=request.data)
        if serializer.is_valid():
            batch = Batch.objects.create(
                institute=institute,
                name=serializer.validated_data.get("name", None),
                start_date=serializer.validated_data.get("start_date", None),
                description=serializer.validated_data.get("description", None),
                batch_fees=serializer.validated_data.get("batch_fees", None),
                fee_penalty=serializer.validated_data.get("fee_penalty", None),
            )
            return Response(BatchSerializer(batch).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchGetUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Detail Fetch",
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        queryset = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        serializer = BatchSerializer(queryset)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Detail Update",
        request_body=BatchSerializer,
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, *args, **kwargs):
        # Here request.user is Institute
        instance = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        serializer = BatchSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            instance.name = serializer.validated_data.get("name", instance.name)
            instance.start_date = serializer.validated_data.get(
                "start_date", instance.start_date
            )
            instance.description = serializer.validated_data.get(
                "description", instance.description
            )
            instance.batch_fees = serializer.validated_data.get(
                "batch_fees", instance.batch_fees
            )
            instance.fee_penalty = serializer.validated_data.get(
                "fee_penalty", instance.fee_penalty
            )
            instance.scheduled_date = serializer.validated_data.get(
                "scheduled_date", instance.scheduled_date
            )
            instance.is_scheduled = bool(
                serializer.validated_data.get("is_scheduled", instance.is_scheduled)
            )
            instance.due_date = serializer.validated_data.get(
                "due_date", instance.due_date
            )
            institute_payment_detail = serializer.validated_data.get(
                "institute_payment_detail", None
            )
            if institute_payment_detail:
                instance.institute_payment_detail = institute_payment_detail
            instance.save(
                update_fields=[
                    "name",
                    "description",
                    "batch_fees",
                    "scheduled_date",
                    "is_scheduled",
                    "due_date",
                    "institute_payment_detail",
                ]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Detail Update",
        responses={
            204: "No Content",
            404: "Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        batch = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        if not batch:
            return Response({"msg": "No Batch Found"}, status=status.HTTP_404_NOT_FOUND)
        batch.delete()
        return Response(
            {"msg": "Batch Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class StudentListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Fetch",
        responses={
            200: UserStudentSerializer,
            404: "Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        # Based on every each institute filtering their batches
        search = request.GET.get("search", None)
        batch = request.GET.get("batch", None)
        sort = request.GET.get("sort", "asc")
        Q_filter = Q(student_profile__batch__institute_id=request.user.id)
        if search:
            Q_filter &= (
                Q(first_name__istartswith=search)
                | Q(last_name__iexact=search)
                | Q(unique_code__iexact=search)
                | Q(email__istartswith=search)
            )
        if batch and int(batch):
            Q_filter &= Q(student_profile__batch_id=batch)
        match sort:
            case "desc":
                order_by = "-first_name"
            case _:
                order_by = "first_name"
        # According to filtered batches listing all the students
        students = (
            User.objects.filter(Q_filter)
            .select_related("student_profile")
            .order_by(order_by)
        )
        paginator = SmallResultPagination()
        queryset = paginator.paginate_queryset(students, request)
        serializer = UserStudentSerializer(queryset, many=True)
        response_data = {
            "total_page": paginator.page.paginator.num_pages,
            "students": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Create",
        responses={
            201: UserStudentSerializer,
            400: "Not Found",
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        batch_id = request.data.pop("batch_id", None)
        serializer = UserStudentSerializer(data=request.data)
        if serializer.is_valid():
            if batch_id is None:
                return Response(
                    {"msg": "Before Creating Students,You want to create Batch First"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            batch = get_object_or_404(Batch, id=int(batch_id))
            student = User.objects.create(
                first_name=serializer.validated_data.get("first_name", None),
                last_name=serializer.validated_data.get("last_name", None),
                email=serializer.validated_data.get("email", None),
                phone_number=serializer.validated_data.get("phone_number", None),
                is_student=True,
            )
            password = generate_random_password()
            student.unique_code = "STU %06d" % student.id
            student.set_password(password)
            student.save(update_fields=["unique_code", "password"])
            student_profile = StudentProfile.objects.filter(user=student).first()
            student_profile.batch = batch
            student_profile.save(update_fields=["batch"])
            # Here request.user is Institute Not Students,
            # Students Have No Registeration Page
            # Sending Their Login Credential Through Email
            send_mail(
                subject=f"""Login Credentials From - {request.user.first_name+" "+request.user.last_name}""",
                message=f"""Dear{student.first_name + " "+student.last_name}
                Your Login Credentials For Your Class Room Are:
                Your Code :- {student.unique_code},
                Your Password :- {password}
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student.email],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstitutePaymentDetailListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        instance = UserPaymentDetail.objects.filter(user=request.user).values()
        if not instance:
            return Response([], status=status.HTTP_200_OK)
        return Response(instance, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = InstitutePaymentDetailSerializer(data=request.data)
        if serializer.is_valid():
            UserPaymentDetail.objects.create(
                user=request.user,
                payment_number=serializer.validated_data.get("payment_number", None),
                payment_qr=serializer.validated_data.get("payment_qr", None),
                payment_bank=serializer.validated_data.get("payment_bank", None),
                upi_id=serializer.validated_data.get("upi_id", None),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstitutePaymentDetailRetrieveUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, pk, user):
        user = UserPaymentDetail.objects.filter(id=pk, user=user)
        if not user:
            raise Response(
                {"msg": "Payment Details Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        return user

    def get(self, request, pk=None, *args, **kwargs):
        instance = (
            self.get_queryset(pk, request.user.id)
            .values("payment_number", "payment_qr", "payment_bank", "upi_id")
            .first()
        )
        return Response(instance, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user.id).first()
        serializer = InstitutePaymentDetailSerializer(data=request.data)
        if serializer.is_valid():
            instance.payment_number = serializer.validated_data.get(
                "payment_number", instance.payment_number
            )
            instance.payment_bank = serializer.validated_data.get(
                "payment_bank", instance.payment_bank
            )
            instance.payment_qr = serializer.validated_data.get(
                "payment_qr", instance.payment_qr
            )
            instance.save()
            return Response(
                {"msg": "Payment Detail Updated Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user.id).first()
        instance.delete()
        return Response(
            {"msg": "Payment Detail Deleted Successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class StudentGetUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Fetch",
        responses={
            200: UserStudentSerializer,
            400: "Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        serializer = UserStudentSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Update",
        request_body=UserStudentSerializer,
        responses={
            200: UserStudentSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, format=None, *args, **kwargs):
        student = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        serializer = UserStudentSerializer(
            instance=student, data=request.data, partial=True
        )
        if serializer.is_valid():
            batch_id = request.data.get("batch_id", None)
            student = User.objects.filter(id=pk).first()
            if batch_id is not None and student is not None:
                batch = Batch.objects.filter(id=int(batch_id)).first()
                student.student_profile.batch = batch
                student.student_profile.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Delete",
        request_body=UserStudentSerializer,
        responses={
            204: "Student Deleted",
            404: "Student Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        student = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        if not student:
            return Response(
                {"msg": "No Student Found"}, status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(
            {"msg": "User Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class StudentPaymentListCreateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", None)
        Q_filter = Q(sender__user=request.user.id) & Q(
            created_at__month=timezone.now().month
        )
        if search:
            Q_filter &= Q()
        instance = StudentPayment.objects.filter(Q_filter).values("fee_amount","fee_paid","fee_status","payment_method","payment_id",batch_name=F("student__user__student_profile__batch__name"),student_name=F("student__user__first_name"))
        serializer=StudentPaymentGETSerializer(instance,many=True)
        paginator = SmallResultPagination()
        queryset = paginator.paginate_queryset(serializer.data, request)
        response_data = {
            "total_page": paginator.page.paginator.num_pages,
            "students": queryset,
        }
        print(response_data)
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        from payments.models import UserPaymentDetail

        serializer = StudentPaymentPostSerailizer(data=request.data)
        if serializer.is_valid():
            payment_detail = get_object_or_404(UserPaymentDetail, id=request.user.id)
            payment = StudentPayment.objects.create(
                sender=payment_detail,
                student=serializer.validated_data.get("student", None),
                fee_amount=serializer.validated_data.get("fee_amount", None),
                fee_paid=serializer.validated_data.get("fee_paid", None),
                fee_status=serializer.validated_data.get("fee_status", None),
            )
            if payment.fee_paid:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class StudentPaymentRetrieveUpdateAPIView(APIView):
    def get_queryset(self, user, pk):
        return StudentPayment.objects.filter(sender=user, id=pk)

    def get(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(request.user.id, pk).values().first()
        return Response(instance, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(request.user.id, pk).first()
        if instance is None:
            return Response(
                {"msg": "Student Payment Not Found"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = StudentPaymentPostSerailizer(data=request.data)
        if serializer.is_valid():
            instance.fee_amount = serializer.validated_data.get(
                "fee_amount", instance.fee_amount
            )
            instance.fee_paid = serializer.validated_data.get(
                "fee_paid", instance.fee_paid
            )
            instance.fee_status = serializer.validated_data.get(
                "fee_status", instance.fee_status
            )
            if not instance.is_notified:
                pass
            instance.save()
            return Response(
                {"msg": "Student Payment Updated Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstituteDashboardAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        batch_data = Batch.objects.filter(institute=request.user.id).aggregate(
            batch_count=Count("id", distinct=True),
            student_count=Count("student_batch", distinct=True),
        )
        total_revenue_data = UserPaymentDetail.objects.filter(
            user=request.user
        ).aggregate(total_revenue=Sum("studentpayment__fee_paid"))
        # previous_month = timezone.now().replace(day=1) - timezone.timedelta(days=1)
        this_month_revenue_data = UserPaymentDetail.objects.filter(
            user=request.user, studentpayment__created_at__month=timezone.now().month
        ).aggregate(
            this_month_revenue=Sum("studentpayment__fee_paid"),
            remaining_amount=Sum("studentpayment__fee_amount")
            - Sum("studentpayment__fee_paid"),
        )
        serializer = DashboardGETSerializer(
            {
                "batch_count": batch_data["batch_count"],
                "student_count": batch_data["student_count"],
                "total_revenue": total_revenue_data["total_revenue"],
                "this_month_revenue": this_month_revenue_data["this_month_revenue"],
                "remaining_amount": this_month_revenue_data["remaining_amount"],
            }
        )
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ================================== Version 2 Release Features Job Portal For Teachers ==================================================================================
class JobListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, user):
        return Job.objects.filter(company=user.id).values()

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job List",
        responses={
            200: "Job List",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_queryset(user=request.user)
        if instance:
            return Response(instance, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Create",
        request_body=JobCreateUpdateSerializer,
        responses={
            201: JobCreateUpdateSerializer,
            400: JobCreateUpdateSerializer,
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = JobCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            Job.objects.create(
                title=serializer.validated_data.get("title", None),
                description=serializer.validated_data.get("description", None),
                category=serializer.validated_data.get("category", None),
                job_type=serializer.validated_data.get("job_type", None),
                company=serializer.validated_data.get("company", None),
                salary=serializer.validated_data.get("salary", None),
            )
            return Response(
                {"msg": "Job Created Successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobRetriveUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, pk, user):
        return Job.objects.filter(id=pk, company=user.id)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Retrieve",
        responses={
            200: "Job Rerieve",
            404: "Job Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk=pk, user=request.user).values().first()
        if instance:
            return Response(instance, status=status.HTTP_200_OK)
        return Response({"msg": "Job Not Found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Update",
        request_body=JobCreateUpdateSerializer,
        responses={
            200: JobCreateUpdateSerializer,
            404: "Job Not Found",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk=pk, user=request.user).first()
        if instance:
            serializer = JobCreateUpdateSerializer(data=request.data)
            if serializer.is_valid():
                instance.title = serializer.validated_data.get("title", instance.title)
                instance.description = serializer.validated_data.get(
                    "description", instance.description
                )
                instance.category = serializer.validated_data.get(
                    "category", instance.category
                )
                instance.job_type = serializer.validated_data.get(
                    "job_type", instance.job_type
                )
                instance.salary = serializer.validated_data.get(
                    "salary", instance.salary
                )
                instance.save(
                    update_fields=[
                        "title",
                        "description",
                        "category",
                        "job_type",
                        "salary",
                    ]
                )
                return Response(
                    {"msg": "Job Updated Successfully"}, status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg": "Job Not Found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Delete",
        request_body=JobCreateUpdateSerializer,
        responses={
            200: "Job Deleted Successfully",
            404: "Job Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk=pk, user=request.user).first()
        if instance:
            instance.delete()
            return Response(
                {"msg": "Job Deleted Successfully"}, status=status.HTTP_200_OK
            )
        return Response({"msg": "Job Not Found"}, status=status.HTTP_404_NOT_FOUND)


class TeacherListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = User.objects.filter(is_teacher=True).select_related(
            "teacher_profile"
        )
