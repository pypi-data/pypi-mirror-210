import sys


sys.path.append('/var/www/mprov_control_center')
from django.conf import settings
# add in the icons to JAZZMIN
settings.JAZZMIN_SETTINGS['icons']['mprov_ldap_manager'] = "far fa-address-book"
settings.JAZZMIN_SETTINGS['icons']['mprov_ldap_manager.ldapuser'] = "fas fa-user-tag"
settings.JAZZMIN_SETTINGS['icons']['mprov_ldap_manager.ldapgroup'] = "fas fa-users"