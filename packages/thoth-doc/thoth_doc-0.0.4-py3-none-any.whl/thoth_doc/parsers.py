import os
import re


def env_var_parser(line):
    ''' Parses [$env.ENV_VAR_NAME] syntax '''

    matches = re.findall(r'(\[\$env\.(\w+)\])', line)
    if matches:
        for match, var_name in matches:
            value = os.environ.get(var_name)
            line = line.replace(match, str(value))
        return line
    return None


def django_settings_parser(line):
    ''' Parses [$settings.SETTINGS_VAR_NAME] syntax '''

    matches = re.findall(r'(\[\$settings\.(\w+)\])', line)
    if matches:
        try:
            from django.conf import settings
        except ImportError:
            raise ImportError('Django is not installed')
        for match, setting_name in matches:
            value = getattr(settings, setting_name)
            line = line.replace(match, str(value))
        return line
    return None
