from django import forms
from django.contrib import admin

from formfieldstash.admin import FormFieldStashMixin
from formfieldstash.helpers import get_advanced_stash_attrs, get_single_stash_attrs
from .models import TestModelSingle, TestModelAdvanced, TestModelInInlineModel, TestInlineModelSingle, \
    TestInlineModel, TestModelAdvanced2, TestModelSingle2, SET_CHOICES, SELECTION_CHOICES


@admin.register(TestModelSingle)
class TestModelAdmin(FormFieldStashMixin, admin.ModelAdmin):
    single_formfield_stash = ('selection', )


class TestModel2Form(forms.ModelForm):
    selection = forms.ChoiceField(
        required=False,
        choices=SELECTION_CHOICES,
        widget=forms.Select(
            attrs=get_single_stash_attrs('selection')
        )
    )


@admin.register(TestModelSingle2)
class TestModel2Admin(FormFieldStashMixin, admin.ModelAdmin):
    form = TestModel2Form


class TestInlineModelInline(admin.StackedInline):
    model = TestInlineModel


ADVANCED_STASH = {
    'set': {
        'set1': ('set1_1', '#testinlinemodel_set-group', ),
        'set2': ('set2_1', 'set2_2', 'set2_3', ),
        # 'set3': ('set3_1', 'set2_1', ),
    },
}


@admin.register(TestModelAdvanced)
class TestModelAdvancedAdmin(FormFieldStashMixin, admin.ModelAdmin):
    inlines = [TestInlineModelInline, ]
    formfield_stash = ADVANCED_STASH


class TestModelAdvanced2AdminForm(forms.ModelForm):
    set = forms.ChoiceField(
        required=False,
        choices=SET_CHOICES,
        widget=forms.Select(
            attrs=get_advanced_stash_attrs('set', ADVANCED_STASH['set'])
        )
    )


@admin.register(TestModelAdvanced2)
class TestModelAdvanced2AdminWithForm(FormFieldStashMixin, admin.ModelAdmin):
    inlines = [TestInlineModelInline, ]
    form = TestModelAdvanced2AdminForm


class TestInlineModelSingleInline(FormFieldStashMixin, admin.StackedInline):
    model = TestInlineModelSingle
    single_formfield_stash = ('selection', )


@admin.register(TestModelInInlineModel)
class TestModelInInlineModelAdmin(FormFieldStashMixin, admin.ModelAdmin):
    inlines = [TestInlineModelSingleInline, ]
