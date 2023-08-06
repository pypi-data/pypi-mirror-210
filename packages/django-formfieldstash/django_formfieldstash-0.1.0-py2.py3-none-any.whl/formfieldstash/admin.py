from django.forms import widgets

from formfieldstash.helpers import get_advanced_stash_attrs, get_single_stash_attrs


class FormFieldStashMixin(object):

    def formfield_for_dbfield(self, db_field, *args, **kwargs):
        field = super(FormFieldStashMixin, self).formfield_for_dbfield(db_field, *args, **kwargs)
        if getattr(self, 'single_formfield_stash', None):
            for stash_field in self.single_formfield_stash:
                if db_field.name == stash_field:
                    field.widget.attrs.update(
                        get_single_stash_attrs(db_field.name)
                    )
        if getattr(self, 'formfield_stash', None):
            for stash_field, fields in self.formfield_stash.items():
                if db_field.name == stash_field:
                    the_choices = getattr(field, 'choices', [])
                    field.widget.attrs.update(
                        get_advanced_stash_attrs(db_field.name, fields, the_choices)
                    )
        return field

    def save_model(self, request, obj, form, change):
        # TODO: implement? design decision! do it on the model!?
        if getattr(self, 'single_formfield_stash', None):
            for stash_field in self.single_formfield_stash:
                for choice, display_choice in form.fields[stash_field].choices:
                    pass
        super(FormFieldStashMixin, self).save_model(request, obj, form, change)

    @property
    def media(self):
        js = (
            'admin/js/jquery.init.js',
            'formfield_stash/formfield_stash.js',
        )
        css = {}
        #     'all': ('formfield_stash/adjust-divers.css', ),
        # }
        original_media = super(FormFieldStashMixin, self).media
        return original_media + widgets.Media(css=css, js=js)
