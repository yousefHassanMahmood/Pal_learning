from .models import CustomUser

def is_instructor_or_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == CustomUser.INSTRUCTOR
    )
