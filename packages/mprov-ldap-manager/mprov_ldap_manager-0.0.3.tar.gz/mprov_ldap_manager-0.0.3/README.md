# mprov_ldap_manager
This is an mPCC python module add-on that will allow the mPCC to manage an LDAP directory.


# Installation
Follow these easy steps to enable this module in the mPCC

1. Go into `/var/www/mprov_control_center` and run `source bin/activate` from a bash prompt.
2. `pip install mprov_ldap_manager` This will install the python module into your mPCC environment
3. Edit the `/var/www/mprov_control_center/mprov_control_center/settings.py` file and add `mprov_ldap_manager` to the bottom of the `INSTALLED_APPS` array.
4. In the same `settings.py` file, add the following:
```
DATABASES = {
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://ldap.nodomain.org/',
        'USER': 'cn=admin,dc=nodomain,dc=org',
        'PASSWORD': 'some_secret_password',
        'BASEDN': 'dc=somedomain,dc=something',
        'CONNECTION_OPTIONS': {
           ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER 
         }
     },
     'default': {
        # your default DB config
     }
}
DATABASE_ROUTERS = ['ldapdb.router.Router']
'''


5. Run `touch /var/www/mprov_control_center/mprov_control_center/wsgi.py` to refresh the mPCC or restart your webserver.