try:
    import json as simplejson
except ImportError:
    try:
        import simplejson
    except ImportError:
        from django.utils import simplejson

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_unicode
import six

_JSONFieldBase = models.TextField

class JSONField(_JSONFieldBase):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', '{}')
        super(JSONField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return None
        if isinstance(value, basestring):
            try:
                return simplejson.loads(value)
            except Exception, e:
                raise ValidationError(str(e))
        else:
            return value
    
    def from_db_value(self, value, expression, connection, context):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return {}
        value = value or '{}'
        if isinstance(value, six.binary_type):
            value = six.text_type(value, 'utf-8')
        if isinstance(value, six.string_types):
            try:
                # with django 1.6 i have '"{}"' as default value here
                if value[0] == value[-1] == '"':
                    value = value[1:-1]
                
                return json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))
        else:
            return value
    
    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, basestring):
            super(JSONField, self).validate(value, model_instance)
            try:
                simplejson.loads(value)
            except Exception, e:
                raise ValidationError(str(e))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return simplejson.dumps(value)
        except Exception, e:
            raise ValidationError(str(e))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_unicode(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        return self.get_prep_value(self._get_val_from_obj(obj))


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^social_auth\.fields\.JSONField"])
except:
    pass
