import json
from contentcuration.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.utils.translation import ugettext_lazy as _
from le_utils.constants import exercises, licenses

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput, label=_('Email'), required=True)
    first_name = forms.CharField(widget=forms.TextInput, label=_('First Name'), required=True)
    last_name = forms.CharField(widget=forms.TextInput, label=_('Last Name'), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, label=_('Password'), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Password (again)'), required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error('email', _('Email already exists.'))
        else:
            return email

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        self.check_field('email', _('Email is required.'))
        self.check_field('first_name', _('First name is required.'))
        self.check_field('last_name', _('Last name is required.'))

        if self.check_field('password1', _('Password is required.')):
            if 'password2' not in self.cleaned_data or self.cleaned_data['password1'] != self.cleaned_data['password2']:
                self.errors['password2'] = self.error_class()
                self.add_error('password2', _('Passwords don\'t match.'))
        else:
            self.errors['password2'] = self.error_class()

        return self.cleaned_data

    def check_field(self, field, error):
        if field not in self.cleaned_data:
            self.errors[field] = self.error_class()
            self.add_error(field, error)
            return False
        return True


class InvitationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput, label=_('First Name'), required=True)
    last_name = forms.CharField(widget=forms.TextInput, label=_('Last Name'), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, label=_('Password'), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Password (again)'), required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        return email

    def clean(self):
        cleaned_data = super(InvitationForm, self).clean()

        self.check_field('first_name', _('First name is required.'))
        self.check_field('last_name', _('Last name is required.'))

        if self.check_field('password1', _('Password is required.')):
            if 'password2' not in self.cleaned_data or self.cleaned_data['password1'] != self.cleaned_data['password2']:
                self.errors['password2'] = self.error_class()
                self.add_error('password2', _('Passwords don\'t match.'))
        else:
            self.errors['password2'] = self.error_class()

        return self.cleaned_data

    def check_field(self, field, error):
        if field not in self.cleaned_data:
            self.errors[field] = self.error_class()
            self.add_error(field, error)
            return False
        return True

    def save(self, user):
        user.set_password(self.cleaned_data["password1"])
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = True
        user.save()
        return user


class InvitationAcceptForm(AuthenticationForm):
    user = None
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'), required=True)

    class Meta:
        model = User
        fields = ('password',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InvitationAcceptForm, self).__init__(*args, **kwargs)

    def clean(self):
        if 'password' not in self.cleaned_data:
            self.errors['password'] = self.error_class()
            self.add_error('password', _('Password is required.'))
        elif not self.user.check_password(self.cleaned_data["password"]):
            self.errors['password'] = self.error_class()
            self.add_error('password', _('Password is incorrect.'))
        else:
            self.confirm_login_allowed(self.user)
        return self.cleaned_data


class ProfileSettingsForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control setting_input'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control setting_input'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        exclude = ('password', 'email')

    def clean_password(self):
        pass

    def clean(self):
        cleaned_data = super(ProfileSettingsForm, self).clean()

        if 'first_name' not in self.cleaned_data:
            self.errors['first_name'] = self.error_class()
            self.add_error('first_name', _('First name is required.'))

        if 'last_name' not in self.cleaned_data:
            self.errors['last_name'] = self.error_class()
            self.add_error('last_name', _('Last name is required.'))
        return self.cleaned_data

    def save(self, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user

MASTERY = tuple([(k, _(v)) for k,v in [t for t in exercises.MASTERY_MODELS] if k != "skill_check"])

class PreferencesSettingsForm(forms.Form):
    # TODO: Add language, audio thumbnail, document thumbnail, exercise thumbnail, html5 thumbnail once implemented
    author = forms.CharField(required=False, label=_('Author'), widget=forms.TextInput(attrs={'class': 'form-control setting_input'}))
    copyright_holder = forms.CharField(required=False, label=_('Copyright Holder'), widget=forms.TextInput(attrs={'class': 'form-control setting_input'}))
    license_description = forms.CharField(required=False, label=_('License Description'), widget=forms.TextInput(attrs={'class': 'form-control setting_input'}))
    license = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control setting_change'}), label=_('License'), choices=licenses.choices)
    mastery_model = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control setting_change'}), choices=MASTERY, label=_("Mastery at"))
    m_value = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control setting_input setting_change'}), label=_("M"))
    n_value = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control setting_input setting_change'}), label=_("N"))
    auto_derive_video_thumbnail = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'setting_change'}), label=_("Videos"))
    auto_derive_audio_thumbnail = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'setting_change'}), label=_("Audio"))
    auto_derive_document_thumbnail = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'setting_change'}), label=_("Documents"))
    auto_derive_html5_thumbnail = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'setting_change'}), label=_("HTML Apps"))
    auto_randomize_questions = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'setting_change'}))

    class Meta:
        model = User
        fields = ('author', 'copyright_holder', 'license', 'license_description', 'mastery_model', 'm_value', 'n_value', 'auto_derive_video_thumbnail', 'auto_randomize_questions')

    def save(self, user):
        user.preferences = json.dumps({
            'author': self.cleaned_data["author"] or "",
            'copyright_holder': self.cleaned_data["copyright_holder"],
            'license': self.cleaned_data["license"],
            'license_description': self.cleaned_data['license_description'] if self.cleaned_data['license'] == 'Special Permissions' else None,
            'mastery_model': self.cleaned_data["mastery_model"],
            'auto_randomize_questions': self.cleaned_data["auto_randomize_questions"],
            'auto_derive_video_thumbnail': self.cleaned_data["auto_derive_video_thumbnail"],
            'auto_derive_audio_thumbnail': self.cleaned_data["auto_derive_audio_thumbnail"],
            'auto_derive_document_thumbnail': self.cleaned_data["auto_derive_document_thumbnail"],
            'auto_derive_html5_thumbnail': self.cleaned_data["auto_derive_html5_thumbnail"],
            'm_value': self.cleaned_data["m_value"],
            'n_value': self.cleaned_data["n_value"],
        })
        user.save()
        return user


class AccountSettingsForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control setting_input'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control setting_input'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control setting_input'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def clean(self):
        cleaned_data = super(AccountSettingsForm, self).clean()

        self.check_field('old_password', _('Current password is incorrect.'))

        if self.check_field('new_password1', _('New password is required.')):
            if 'new_password2' not in self.cleaned_data or self.cleaned_data['new_password1'] != self.cleaned_data['new_password2']:
                self.errors['new_password2'] = self.error_class()
                self.add_error('new_password2', _('New passwords don\'t match.'))
        else:
            self.errors['new_password2'] = self.error_class()

        return self.cleaned_data

    def check_field(self, field, error):
        if field not in self.cleaned_data:
            self.errors[field] = self.error_class()
            self.add_error(field, error)
            return False
        return True
