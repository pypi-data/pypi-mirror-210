# Defines the DB Models that will be used by this Django App or section of mProv
# -*- coding: utf-8 -*-
# excerpts from https://github.com/django-ldapdb/django-ldapdb/tree/master/examples
# This software is distributed under the two-clause BSD license.
# Copyright (c) The django-ldapdb project

from django.db.models import Manager
from django import forms


import ldapdb.models
from ldapdb.models import fields

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete, post_save


# Users
# - uid -> username
# - uidNumber -> uid
# - gidNumber -> primary GID
# - cn -> fisrt name
# - sn -> last name
# - mail -> email
# - 

class LdapUser(ldapdb.models.Model):
    """
    Area for managing LDAP users
    """
    # LDAP meta-data
    base_dn = settings.DATABASES['ldap']['BASEDN']
    object_classes = ['posixAccount', 'shadowAccount', 'inetOrgPerson']
    last_modified = fields.DateTimeField(db_column='modifyTimestamp', editable=False)

    # inetOrgPerson
    first_name = fields.CharField(db_column='givenName', verbose_name="First name")
    last_name = fields.CharField("Last name", db_column='sn')
    full_name = fields.CharField(db_column='cn')
    email = fields.CharField(db_column='mail')
    phone = fields.CharField(db_column='telephoneNumber', blank=True)
    mobile_phone = fields.CharField(db_column='mobile', blank=True)
    photo = fields.ImageField(db_column='jpegPhoto')

    # posixAccount
    uid = fields.IntegerField(db_column='uidNumber', unique=True)
    group = models.ForeignKey('LdapGroup', to_field='gid', db_column='gidNumber', on_delete=models.SET_NULL, null=True)
    gecos = fields.CharField(db_column='gecos')
    home_directory = fields.CharField(db_column='homeDirectory')
    login_shell = fields.CharField(db_column='loginShell', default='/bin/bash')
    username = fields.CharField(db_column='uid', primary_key=True)
    password = fields.CharField(db_column='userPassword', blank=True, null=True, help_text="To remain unchanged, leave blank")

    # shadowAccount
    last_password_change = fields.TimestampField(db_column='shadowLastChange')

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name

# groups
# cn -> groupname
# gidNumber -> gid
# memberUid -> uid of member (multiple allowed)

class LdapGroup(ldapdb.models.Model):
    """
    Area for managing LDAP groups
    """
    # LDAP meta-data
    base_dn =  settings.DATABASES['ldap']['BASEDN']
    object_classes = ['posixGroup']

    # posixGroup attributes
    gid = fields.IntegerField(db_column='gidNumber', unique=True)
    name = fields.CharField(db_column='cn', max_length=200, primary_key=True)
    usernames = fields.ListField(db_column='memberUid')
    
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
    

# OU
# ou -> OU Name





