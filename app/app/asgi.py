import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_asgi_application()


# """
#For Production

# import os
# import sys

# from django.core.asgi import get_asgi_application

# project_home = u'home/ubuntu/dirname/app'
# if project_home not in sys.path:
#     sys.path.append(project_home)

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# application = get_asgi_application()
