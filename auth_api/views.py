from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tipo_usuario = "INTERNO"
        avatar_url = None
        try:
            if hasattr(user, 'profile'):
                tipo_usuario = user.profile.tipo_usuario
                if user.profile.avatar:
                    avatar_url = request.build_absolute_uri(user.profile.avatar.url)
        except:
            pass

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tipo_usuario": tipo_usuario,
            "avatar": avatar_url,
            "is_staff": user.is_staff, # Keeping as fallback
        })

    def patch(self, request):
        user = request.user
        
        # Base user update
        if "first_name" in request.data:
            user.first_name = request.data["first_name"]
        if "last_name" in request.data:
            user.last_name = request.data["last_name"]
        if "email" in request.data:
            user.email = request.data["email"]
        user.save()

        # Update or create profile
        profile, created = user.profile, False
        if not hasattr(user, 'profile'):
            from accounts.models import UserProfile
            profile = UserProfile.objects.create(user=user)

        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
            profile.save()
            
        avatar_url = None
        if profile.avatar:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tipo_usuario": profile.tipo_usuario,
            "avatar": avatar_url,
        })

def health(request):
    return JsonResponse({"status": "ok"})
