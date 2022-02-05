from core.models import User
from rest_framework import generics, authentication, permissions, status, views
from django.contrib.auth import authenticate, login, logout, get_user_model
from user.serializers import (
    UserSerializer,
    LoginSerializer,
    LogoutSerializer,
    ResetPasswordSerializer,
    BasicUserSerializer,
    UserUpdateDataSerializer,
)
from rest_framework.response import Response
from decouple import config
import requests
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated


baseUrl = config("API_BASE_URL")


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class UserAPIView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]


class RetrieveUpdateDestroyUserAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]


class UserCreateView(generics.GenericAPIView):
    """Creates a new user to the system"""

    serializer_class = BasicUserSerializer
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        """Create a user and returns access_token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            user.is_active = True
            user.is_staff = True
            user.save()
            data = {
                "grant_type": "password",
                "username": serializer.validated_data["email"],
                "password": serializer.validated_data["password"],
                "client_id": config("CLIENT_ID"),
                "client_secret": config("CLIENT_SECRET"),
            }
            res = requests.post(f"{baseUrl}/user/oauth/token/", json=data)
            data = res.json()
            data["id"] = user.id
            return Response(status=status.HTTP_200_OK, data=data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid user data")


class UserLoginView(generics.GenericAPIView):
    """Logs in Admin user to the system"""

    serializer_class = LoginSerializer
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request):
        """Logs in user to the system"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # user = serializer.validate()

        user = authenticate(
            request=request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data="Incorrect ID or password"
            )

        user.is_active = True
        user.save()
        data = {
            "grant_type": "password",
            "username": serializer.validated_data["email"],
            "password": serializer.validated_data["password"],
            "client_id": config("CLIENT_ID"),
            "client_secret": config("CLIENT_SECRET"),
        }
        res = requests.post(
            f"{baseUrl}/user/oauth/token/",
            json=data,
            headers={"content-type": "application/json"},
            timeout=120,
        )
        return Response(status=status.HTTP_200_OK, data=res.json())


class UserLogoutView(generics.GenericAPIView):
    """Log out and revoke token"""

    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """Revoke access token and logout user"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.data.get("token", None)

        if serializer.is_valid():
            data = {
                "token": token,
                "client_id": config("CLIENT_ID"),
                "client_secret": config("CLIENT_SECRET"),
            }
            requests.post(f"{baseUrl}/user/oauth/revoke-token/", json=data)
            request.user.save()
            return Response(status=status.HTTP_200_OK, data="Successfully logged out.")
        else:
            return Response(
                data="User not logged in", status=status.HTTP_400_BAD_REQUEST
            )


class UserPasswordResetView(generics.GenericAPIView):
    """Resets user password"""

    serializer_class = ResetPasswordSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        """Resets user password"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.data.get("old_password", None)
        new_password = serializer.data.get("new_password", None)

        user = self.request.user
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="User not found")
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(
                status=status.HTTP_200_OK, data="Password was changed successfully"
            )
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Password don't match")


class UserLoginCheckView(generics.GenericAPIView):
    """Checks id=f user is still logged in"""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """Checks app login data"""
        user = self.request.user
        merchant = get_or_none(User, user=user)
        # merchant = Merchant.objects.filter(user=user).first()
        if merchant:
            parcel = Parcel.objects.filter(merchant=merchant).count()
            is_payment_added = False
            if merchant.is_payment_method_added:
                is_payment_added = merchant.is_payment_method_added
            is_new_merchant = True
            if parcel > 0:
                is_new_merchant = False

            data = {
                "is_payment_added": is_payment_added,
                "is_new_merchant": is_new_merchant,
            }
            return Response(status=status.HTTP_200_OK, data=data)
        return Response(
            status=status.HTTP_404_NOT_FOUND, data="Merchant data was not found"
        )


class CoreUserUpdateView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""

    serializer_class = UserUpdateDataSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrive and return authenticated user"""
        return self.request.user

    def patch(self, request):
        """Partially update user"""
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_200_OK,
                data=UserUpdateDataSerializer(self.request.user).data,
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data="Please check the update field"
        )


# def send_otp(phone, otp):
#     greenweburl = "http://api.greenweb.com.bd/api.php"
#     token = f"{config('GREEN_WEB_SMS_OTP_TOKEN')}"
#     # sms receivers number here (separated by comma)
#     to = f"{phone}"
#     data = {
#         "token": token,
#         "to": to,
#         "message": f"{otp} is your ZEENCourier verification OTP code. It will be valid till 5 minutes.",
#     }
#     responses = requests.post(url=greenweburl, data=data)
#     print(responses)
#     return responses


# def get_otp(phone):
#     if phone:
#         key = random.randint(999, 9999)
#         print(key)
#         return key
#     else:
#         return False


# { "phone": "+8801711120516"} or { "phone": "+8801711120516" , "isRegister": "Yes"}
# class ValidatePhoneSendOTP(views.APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, *args, **kwargs):
#         phone_number = request.data.get("phone")
#         isRegister = request.data.get("isRegister", False)
#         if phone_number:
#             phone = PhoneNumber.from_string(phone_number)
#             # user = get_user_model().objects.get(phone=phone)
#             user = get_or_none(get_user_model(), phone=phone)
#             if user and isRegister:
#                 return Response(
#                     status=status.HTTP_400_BAD_REQUEST,
#                     data="Phone number already exists.",
#                 )
#             else:
#                 key = get_otp(str(phone_number))
#                 if key:
#                     old = user = get_or_none(PhoneOTP, phone=phone)
#                     # old = PhoneOTP.objects.get(phone=phone)
#                     if old:
#                         respose_otp = send_otp(str(phone_number), key)
#                         if respose_otp.status_code == 200:
#                             count = old.count  # Add logic if you want to limit OTP send
#                             old.count = count + 1
#                             old.otp = key
#                             old.validated = False
#                             old.save()
#                             return Response(
#                                 status=status.HTTP_200_OK,
#                                 data="OTP sent successfully.",
#                             )
#                         else:
#                             return Response(
#                                 status=status.HTTP_400_BAD_REQUEST,
#                                 data="Something went wrong with OTP sending.",
#                             )
#                     else:
#                         PhoneOTP.objects.create(phone=phone, otp=key)
#                         respose_otp = send_otp(str(phone_number), key)
#                         if respose_otp.status_code == 200:
#                             return Response(
#                                 status=status.HTTP_200_OK,
#                                 data="OTP sent successfully.",
#                             )
#                         else:
#                             return Response(
#                                 status=status.HTTP_400_BAD_REQUEST,
#                                 data="Something went wrong with OTP sending.",
#                             )
#                 else:
#                     return Response(
#                         status=status.HTTP_400_BAD_REQUEST,
#                         data="Sending OTP error.",
#                     )
#         else:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 data="Phone number is not given in post request.",
#             )


# {"phone": "+8801711120516", "otp": "5483"}


# class ValidateOTP(views.APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, *args, **kwargs):
#         phone_number = request.data.get("phone", False)
#         otp_sent = request.data.get("otp", False)

#         phone = PhoneNumber.from_string(phone_number)

#         if phone and otp_sent:
#             old = get_or_none(PhoneOTP, phone=phone)
#             # old = PhoneOTP.objects.get(phone=phone)
#             if old:
#                 old = old
#                 otp = old.otp
#                 five_minutes_ago = timezone.now() + datetime.timedelta(minutes=-6)
#                 valid = old.updated_at > five_minutes_ago
#                 print(valid)
#                 print(str(otp_sent) == str(otp))
#                 if str(otp_sent) == str(otp) and valid:
#                     old.validated = True
#                     old.save()
#                     return Response(
#                         status=status.HTTP_200_OK,
#                         data="OTP matched. Please proceed",
#                     )
#                 else:
#                     return Response(
#                         status=status.HTTP_400_BAD_REQUEST,
#                         data="OTP incorrect or more than 5 mins old.",
#                     )
#             else:
#                 return Response(
#                     status=status.HTTP_400_BAD_REQUEST,
#                     data="First proceed via sending otp request.",
#                 )
#         else:
#             return Response(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 data="Please provide both phone and otp for validations",
#             )
