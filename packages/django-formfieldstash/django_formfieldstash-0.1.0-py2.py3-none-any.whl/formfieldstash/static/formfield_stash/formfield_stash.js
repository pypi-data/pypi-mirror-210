(function($){
    $.fn.formfield_stash = function(custom_options) {
        var options = {
            type:'dealer',
            dummy: 'dummy'
        }

        return this.each(function() {
            var _self = $(this);
            var prefix = '';
            var $options = _self.find("option");
            var fields = [];
            var fieldconfigs = {};
            var has_configs = false;
            if (_self.attr("data-original-field") != _self.attr("name")) {
                prefix = _self.attr("name").replace(_self.attr("data-original-field"), '');
            }

            _self.attr('data-formfield-stash', 'initialized');
            $.each($options, function(index, item) {
                // TODO: check for formsets/name prefixes in inlines
                var value = $(item).val();
                var config = _self.attr('data-formfield-stash-' + value)
                if (config) {
                    has_configs = true;
                    var temp_fields = config.split(",");
                    fieldconfigs[value] = temp_fields;
                    fields = fields.concat(temp_fields);
                } else {
                    fields.push(value);
                }
            });
            var $form = _self.closest("form");

            var on_change = function(e) {
                clearTimeout(timeout_id);
                var current_value = _self.val();
                $.each(fields, function(index, item) {
                    if (!item.length) {
                        return;
                    }
                    // basic try: field with id
                    var id_selector = "#id_" + prefix + item;
                    var $wrap = $form.find(selector).closest(".form-row");
                    if (item.indexOf("#") > -1) {
                        // handmade targeting via ID, mainly used for inlines
                        $wrap = $(item);
                    }
                    if (!$wrap.length) {
                        // special items, like m2m with filter_horizontal, try the label!
                        var selector = 'label[for="id_' + prefix + item + '"]';
                        $wrap = $form.find(selector).closest(".form-row");
                    }
                    if (!$wrap.length) {
                        // multi widget fields workaround, for now!
                        $wrap = $form.find(id_selector + "_0").closest(".form-row");
                    }
                    if (has_configs && fieldconfigs[current_value]) {
                        var current_config = fieldconfigs[current_value];
                        if ($.inArray(item, current_config) > -1) {
                            $wrap.show(0);
                        } else {
                            $wrap.hide(0);
                        }
                    } else {
                        if (item == current_value) {
                            $wrap.show(0);
                        } else {
                            $wrap.hide(0);
                        }
                    }
                })
            };

            _self.change(on_change);
            // allow other widgets to initialize in a visible state
            // ie filer widget
            var timeout_id = setTimeout(on_change, 20);
            // on_change();

            return this;
        });
    }
})(django.jQuery);


// init, including add row for inlines
django.jQuery(document).ready( function($) {

    // https://docs.djangoproject.com/en/4.2/ref/contrib/admin/javascript/
    $(document).on('formset:added', (event, $row, formsetName) => {
        if (event.detail && event.detail.formsetName) {
            // Django >= 4.1
            handleFormsetAdded(event.target, event.detail.formsetName)
        } else {
            // Django < 4.1, use $row and formsetName
            handleFormsetAdded($row.get(0), formsetName)
        }
    })

    function handleFormsetAdded(row, formsetName) {
        var $to_enhance = $(row).find('select[data-formfield-stash="true"]')
        $to_enhance.formfield_stash();
    }

    $('form select[data-formfield-stash=true]').not("[name*=__prefix__]").formfield_stash();

});