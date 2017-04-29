
"""This XBlock provides an HTML page fragment to display a button
   allowing the Course user to launch an external course Container
   via Appsembler's Container deploy API.
"""

import pkg_resources
import logging

from django.conf import settings
from django.template import Context, Template
from django.core import validators

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment


log = logging.getLogger(__name__)


DEFAULT_API_CONF = {
    'DOMAIN': 'https://wharf.appsembler.com',
    'PATH': '/isc/newdeploy'
}


class LaunchContainerXBlock(XBlock):
    """
    Provide a Fragment with associated Javascript to display to
    Students a button that will launch a configurable external course
    Container via a call to Appsembler's container deploy API.
    """

    project = String(
        display_name='Project name',
        default=u'(EDIT THIS COMPONENT TO SET PROJECT NAME)',
        scope=Scope.content,
        help=(u"The name of the container's Project as defined for the "
              "Appsembler API"),
    )

    project_friendly = String(
        display_name='Project Friendly name',
        default=u'',
        scope=Scope.content,
        help=(u"The name of the container's Project as displayed to the end "
              "user"),
    )

    project_friendly = String(
        display_name='Project Friendly name',
        default=u'',
        scope=Scope.content,
        help=(u"The name of the container's Project as displayed to the end "
              "user"),
    )

    project_friendly = String(
        display_name='Project Token',
        default=u'',
        scope=Scope.content,
        help=(u"This is a unique token that can be found in the AVL dashboard.")
    )

    @property
    def block_course_org(self):
        return self.runtime.course_id.org

    @property
    def student_email(self):
        if hasattr(self, "runtime"):
            user = self.runtime._services['user'].get_current_user()
            return user.emails[0]
        else:
            return None

    def _get_API_url(self):
        api_conf = settings.ENV_TOKENS.get('LAUNCHCONTAINER_API_CONF', DEFAULT_API_CONF)
        url_validator = validators.URLValidator()
        url_validator(api_conf['DOMAIN'])

        if not all([api_conf.get('DOMAIN'),
                   api_conf.get('PATH')]):
            msg = ("The LAUNCHCONTAINER_API_CONF is not configured properly. "
                   "Please provide both a domain and path.")
            raise validators.ValidationError(msg)

        domain = api_conf['DOMAIN']
        path = api_conf['PATH']
        if not path.startswith('/'):
            path = '/' + path

        return '{}{}'.format(domain, path)

    def student_view(self, context=None):
        """
        The primary view of the LaunchContainerXBlock, shown to students
        when viewing courses.
        """

        user_email = None
        # workbench runtime won't supply system property
        if getattr(self, 'system', None):
            if self.system.anonymous_student_id:
                if getattr(self.system, 'get_real_user', None):
                    anon_id = self.system.anonymous_student_id
                    user = self.system.get_real_user(anon_id)
                    if user and user.is_authenticated():
                        user_email = user.email
                elif self.system.user_is_staff:  # Studio preview
                    from django.contrib.auth.models import User
                    user = User.objects.get(id=self.system.user_id)
                    user_email = user.email

        context = {
            'project': self.project,
            'project_friendly': self.project_friendly,
            'user_email': user_email,
            'API_url': self._get_API_url()
        }
        frag = Fragment()
        frag.add_content(
            render_template('static/html/launchcontainer.html', context)
        )
        frag.add_css(render_template("static/css/launchcontainer.css"))
        frag.add_javascript(render_template("static/js/src/launchcontainer.js",
                                            context))
        frag.initialize_js('LaunchContainerXBlock')
        return frag

    def studio_view(self, context=None):
        """
        Return fragment for editing block in studio.
        """
        try:
            cls = type(self)

            def none_to_empty(data):
                """
                Return empty string if data is None else return data.
                """
                return data if data is not None else ''

            edit_fields = (
               (field, none_to_empty(getattr(self, field.name)), validator)
               for field, validator in (
                   (cls.project, 'string'),
                   (cls.project_friendly, 'string'), )
            )

            context = {
                'fields': edit_fields
            }
            fragment = Fragment()
            fragment.add_content(
                render_template(
                    'static/html/launchcontainer_edit.html',
                    context
                )
            )
            fragment.add_javascript(
                load_resource("static/js/src/launchcontainer_edit.js"))
            fragment.initialize_js('LaunchContainerEditBlock')

            return fragment
        except:  # pragma: NO COVER
            log.error("Don't swallow my exceptions", exc_info=True)
            raise

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        log.info(u'Received data: {}'.format(data))
        try:
            self.project = data['project']
            self.project_friendly = data['project_friendly']
            self.api_url = self._get_API_url()

            return {
                'result': 'success',
            }
        except Exception as e:
            return {
                'result': 'Error saving data:{0}'.format(str(e))
            }

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("A single launchcontainer",
             """\
                <vertical_demo>
                    <launchcontainer/>
                </vertical_demo>
             """)
        ]


def load_resource(resource_path):  # pragma: NO COVER
    """
    Gets the content of a resource
    """
    resource_content = pkg_resources.resource_string(__name__, resource_path)

    return unicode(resource_content)


def render_template(template_path, context=None):  # pragma: NO COVER
    """
    Evaluate a template by resource path, applying the provided context.
    """
    if context is None:
        context = {}

    template_str = load_resource(template_path)
    template = Template(template_str)

    return template.render(Context(context))
