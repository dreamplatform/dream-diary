from django.db.models import fields
from django.db.models import Max


class OrderField(fields.IntegerField):
    """Ignores the incoming value and instead gets the maximum plus one of the field."""
    def __init__(self, *args, **kwargs):
        self.instance_is_archivable = kwargs.pop('instance_is_archivable', False)
        return super(OrderField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        #if the model is new and not an update
        #or this model is marked as archivable and is not archived and order is None
        # -> means archived item is beeing unarchived and needs new order
        if add or \
                (self.instance_is_archivable and model_instance.is_archived == False \
                and getattr(model_instance, self.attname) == None):
            records = model_instance.__class__.objects.aggregate(Max(self.name))
            if records:
                # get the maximum attribute from the first record and add 1 to it
                value = records['%s__max' % self.name]
                if value:
                    value = value +1
                else:
                    value = 1
            else:
                value = 1
        #otherwise the model is updating, pass the attribute value through
        else:
            value = getattr(model_instance, self.attname)
        setattr(model_instance, self.attname, value)
        return value

    def formfield(self, **kwargs):
        return None


class HtmlColorCodeField(fields.CharField):
    """A CharField that checks that the value is a valid HTML color code (Hex triplet).
    Has no required argument.
    """
    def __init__(self, **kwargs):
        kwargs['max_length'] = 7
        super(HtmlColorCodeField,self).__init__(**kwargs)

    def pre_save(self, model_instance, add):
        """Checks that field_data is a HTML color code string.
        """
        value = getattr(model_instance, self.attname)
        if not value.startswith("#") or not len(value) == 7:
            raise ValueError("Value %s is not valid rgb hex string" % value)
        return value


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^dreamdiary\.fields\.OrderField"])
    add_introspection_rules([], ["^dreamdiary\.fields\.HtmlColorCodeField"])
except ImportError:
  pass
