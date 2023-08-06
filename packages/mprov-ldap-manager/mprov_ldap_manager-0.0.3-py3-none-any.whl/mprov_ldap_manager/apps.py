# Describes this "App" or mProv section, to Django
from django.apps import AppConfig

class LDAPManager(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'mprov_ldap_manager'
  verbose_name = "LDAP Management"
  