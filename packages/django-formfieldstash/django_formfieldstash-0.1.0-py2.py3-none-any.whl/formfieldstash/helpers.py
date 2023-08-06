

def get_base_attrs(field_name):
    attrs = {
        'data-formfield-stash': "true",
        'data-original-field': field_name,
    }
    return attrs


def get_single_stash_attrs(field_name):
    attrs = get_base_attrs(field_name)
    return attrs


def get_advanced_stash_attrs(field_name, stash_config, field_choices=[]):
    attrs = get_base_attrs(field_name)
    for choice in field_choices:
        if choice[0] not in stash_config:
            stash_config[choice[0]] = [choice[0], ]
    for choice, show_fields in stash_config.items():
        attrs['data-formfield-stash-%s' % choice] = (
            ','.join(show_fields)
        )
    return attrs
