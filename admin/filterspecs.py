"""
FilterSpec encapsulates the logic for displaying filters in the Django admin.
Filters are specified in models with the "list_filter" option.

Each filter subclass knows how to display a filter for a field that passes a
certain test -- e.g. being a DateField or ForeignKey.
"""

from django.db import models
from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
import datetime
from google.appengine.ext import db

class FilterSpec(object):
    filter_specs = []
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        self.field = f
        self.params = params
        self.field_path = field_path
        if field_path is None:
            if isinstance(f, models.related.RelatedObject):
                self.field_path = f.var_name
            else:
                self.field_path = f.name

    def register(cls, test, factory):
        cls.filter_specs.append((test, factory))
    register = classmethod(register)

    def create(cls, f, request, params, model, model_admin, field_path=None):
        for test, factory in cls.filter_specs:
            if test(f):
                return factory(f, request, params, model, model_admin,
                               field_path=field_path)
    create = classmethod(create)

    def has_output(self):
        return True

    def choices(self, cl):
        raise NotImplementedError()

    def title(self):
        return self.field.verbose_name

    def output(self, cl):
        t = []
        if self.has_output():
            t.append(_(u'<h3>By %s:</h3>\n<ul>\n') % escape(self.title()))

            for choice in self.choices(cl):
                t.append(u'<li%s><a href="%s">%s</a></li>\n' % \
                    ((choice['selected'] and ' class="selected"' or ''),
                     iri_to_uri(choice['query_string']),
                     choice['display']))
            t.append('</ul>\n\n')
        return mark_safe("".join(t))

class BooleanFieldFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(BooleanFieldFilterSpec, self).__init__(f, request, params, model,
                                                     model_admin,
                                                     field_path=field_path)
        self.lookup_kwarg = '%s__bool' % self.field_path
        self.lookup_kwarg2 = '%s__isnull' % self.field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val2 = request.GET.get(self.lookup_kwarg2, None)

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        for k, v in ((_('All'), None), (_('Yes'), '1'), (_('No'), '0')):
            yield {'selected': self.lookup_val == v and not self.lookup_val2,
                   'query_string': cl.get_query_string(
                                   {self.lookup_kwarg: v},
                                   [self.lookup_kwarg2]),
                   'display': k}
        if isinstance(self.field, models.NullBooleanField):
            yield {'selected': self.lookup_val2 == 'True',
                   'query_string': cl.get_query_string(
                                   {self.lookup_kwarg2: 'True'},
                                   [self.lookup_kwarg]),
                   'display': _('Unknown')}

FilterSpec.register(lambda f: isinstance(f, db.BooleanProperty),
                                 BooleanFieldFilterSpec)

class ChoicesFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(ChoicesFilterSpec, self).__init__(f, request, params, model,
                                                model_admin,
                                                field_path=field_path)
        self.lookup_kwarg = '%s__exact' % self.field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
               'display': _('All')}
        for k, v in self.field.flatchoices:
            yield {'selected': smart_unicode(k) == self.lookup_val,
                    'query_string': cl.get_query_string(
                                    {self.lookup_kwarg: k}),
                    'display': v}

FilterSpec.register(lambda f: bool(f.choices), ChoicesFilterSpec)

class DateFieldFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None): 
        super(DateFieldFilterSpec, self).__init__(f, request, params, model,
                                                  model_admin,
                                                  field_path=field_path)

        self.field_generic = '%s__' % self.field_path

        self.date_params = dict([(k, v) for k, v in params.items()
                                 if k.startswith(self.field_generic)])

        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        today_str = isinstance(self.field, models.DateTimeField) \
                    and today.strftime('%Y-%m-%d 23:59:59') \
                    or today.strftime('%Y-%m-%d')

        self.links = (
            (_('Any date'), {}),
            (_('Today'), {'%s__year' % self.field_path: str(today.year),
                       '%s__month' % self.field_path: str(today.month),
                       '%s__day' % self.field_path: str(today.day)}),
            (_('Past 7 days'), {'%s__gte' % self.field_path:
                                    one_week_ago.strftime('%Y-%m-%d'),
                             '%s__lte' % self.field_path: today_str}),
            (_('This month'), {'%s__year' % self.field_path: str(today.year),
                             '%s__month' % self.field_path: str(today.month)}),
            (_('This year'), {'%s__year' % self.field_path: str(today.year)})
        )

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        for title, param_dict in self.links:
            yield {'selected': self.date_params == param_dict,
                   'query_string': cl.get_query_string(
                                   param_dict,
                                   [self.field_generic]),
                   'display': title}

FilterSpec.register(lambda f: isinstance(f, db.DateProperty) or isinstance(f, db.DateTimeProperty),
                              DateFieldFilterSpec)