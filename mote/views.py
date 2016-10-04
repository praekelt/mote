import os
import glob
import re
import ujson as json
from collections import OrderedDict
from termcolor import cprint

from cached_property import cached_property

from django.views.generic.base import TemplateView
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.template import engines
from django.templatetags.static import PrefixNode
from django.utils.six.moves.urllib.parse import urljoin

from mote.models import Project, Aspect, Pattern, Element, Variation


lib = ""

class HomeView(TemplateView):

    template_name = "mote/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        li = [Project(id) for id in os.listdir(os.path.join(os.path.dirname(__file__), "..", "projects"))]
        li.sort(lambda a, b: cmp(a.metadata.get("position"), a.metadata.get("position")))
        context["projects"] = li
        return context


class ProjectView(TemplateView):
    """Detail view for a project"""

    template_name = "mote/project.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context["project"] = Project(kwargs["id"])
        return context


class AspectView(TemplateView):
    """Detail view for an aspect"""

    template_name = "mote/aspect.html"

    def get_context_data(self, **kwargs):
        context = super(AspectView, self).get_context_data(**kwargs)
        project = Project(kwargs["id"])
        context["aspect"] = Aspect(kwargs["aspect"], project)
        return context


class PatternView(TemplateView):
    """Detail view for a pattern"""

    template_name = "mote/pattern.html"

    def get_context_data(self, **kwargs):
        context = super(PatternView, self).get_context_data(**kwargs)
        project = Project(kwargs["id"])
        aspect = Aspect(kwargs["aspect"], project)
        pattern = Pattern(kwargs["pattern"], aspect)
        context["pattern"] = pattern

        # A pattern may have an intro view. First look in the pattern itself,
        # then fall back to normal template resolution.
        template_names = (
            "%s/%s/src/patterns/%s/mote/intro.html" % (project.id, aspect.id, pattern.id),
            "mote/pattern/intros/%s.html" % pattern.id,
        )
        intro = None
        for template_name in template_names:
            # todo: dont' render it here, only in the template. Just check that it loads.
            try:
                intro = render_to_string(template_name, {})
                break
            except TemplateDoesNotExist:
                pass
        context["intro"] = intro

        return context


class ElementBaseView(TemplateView):

    @cached_property
    def element(self):
        project = Project(self.kwargs["id"])
        aspect = Aspect(self.kwargs["aspect"], project)
        pattern = Pattern(self.kwargs["pattern"], aspect)
        element = Element(self.kwargs["element"], pattern)
        return element

    def get_context_data(self, **kwargs):
        context = super(ElementBaseView, self).get_context_data(**kwargs)
        context["element"] = self.element
        context["static_root"] = urljoin(PrefixNode.handle_simple("STATIC_URL"), self.element.aspect.relative_path)
        return context


class ElementIndexView(ElementBaseView):
    """Index view for an element. Provides common UI around an element."""

    def get_template_names(self):
        return [self.element.index_template_name]


class ElementPartialView(ElementBaseView):
    """Element view with no wrapping html and body tags"""

    def get_template_names(self):
        return [self.element.template_name]


class ElementIframeView(ElementBaseView):
    """Element view suitable for rendering in an iframe"""

    def get_template_names(self):
        return ["mote/element/iframe.html"]


class VariationBaseView(ElementBaseView):

    @cached_property
    def variation(self):
        return Variation(self.kwargs["variation"], self.element)

    def get_context_data(self, **kwargs):
        context = super(VariationBaseView, self).get_context_data(**kwargs)
        # Rename some variables so we can re-use templates
        context["original_element"] = self.element
        context["element"] = self.variation
        return context


class VariationPartialView(VariationBaseView):

    def get_template_names(self):
        return [self.variation.template_name]


class VariationIframeView(VariationBaseView):
    """Element view suitable for rendering in an iframe"""

    def get_template_names(self):
        return ["mote/element/iframe.html"]


class Brand(TemplateView):

    """ Brand Guidelines view

    Basic brand identity elements like colour,
    typography and iconography.

    """

    template_name = "mote/brand.html"

    def get_context_data(self, **kwargs):

        results = super(TemplateView, self).get_context_data(**kwargs)
        #results["sass_colors"] = get_sass_variables("colors")
        #results["sass_breakpoints"] = get_sass_variables("breakpoints")
        results["active_page"] = "brand"
        return results


class Docs(TemplateView):

    """ Documentation view

    Project documentation for the pattern lab sysytem
    as well as how Javascript is used in the project.

    """

    template_name = "mote/docs.html"

    def get_context_data(self, **kwargs):

        results = super(TemplateView, self).get_context_data(**kwargs)
        results["active_page"] = "docs"
        return results


        #RES_DIR = os.path.join(os.path.dirname(__file__), "res")


        '''
        results["active_page"] = "patterns"
        #results["sass_colors"] = get_sass_variables("colors")
        #results["sass_breakpoints"] = get_sass_variables("breakpoints")

        global lib
        lib = self.kwargs["library"]

        menu = get_menu_items()

        results["menu_items"] = menu["menu_items"]
        results["links"] = menu["links"]

        # Return the base page if no category is specified.
        # Needs refactoring to include a separate pattern.html template.
        if self.kwargs["category"] == None:
            self.template_name = "mote/base.html"
            return results

        # Find a matching path using supplied category
        pattern = "*" + self.kwargs["category"]
        path = glob.glob(os.path.join(settings.BASE_DIR, settings.SG_PATTERN_DIR, settings.SG_LIBS[lib]["dir"], pattern))[0]

        active_category = self.kwargs["category"]
        results["active_category"] = active_category
        templates = template_walker(path, "mote_")
        results["templates"] = templates

        results["library"] = lib
        '''


class Basic(TemplateView):

    """ Basic pattern listing

    Generates a list of links to basic version of all the patterns

    """

    global lib
    template_name = "mote/basic.html"

    def get_context_data(self, **kwargs):

        results = super(TemplateView, self).get_context_data(**kwargs)
        templates = template_walker(os.path.join(settings.BASE_DIR,
                                                 settings.SG_PATTERN_DIR,
                                                 settings.SG_LIBS[lib]["dir"],
                                                 "mote_"))
        results["templates"] = templates
        menu = get_menu_items()
        results["menu_items"] = menu["menu_items"]
        results["links"] = menu["links"]
        return results


def template_walker(directory, category):

    """ Finds a set of mote templates within a project's /fed/ folder.

    Args:
        directory (string): template sub-directory to search.

    Returns:
        A dictionary containing the names and paths of templates.

    """

    global lib
    template_files = []
    template_names = []

    print directory

    for dir, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if category in filename:
                template_names.append(filename[:-5])
                template = os.path.join(directory, dir, filename)
                template_files.append(template)



    return {"names": template_names, "files": template_files}


def get_menu_items():

    """ Generates a list of all patterns available in the project's /fed/ folder.

    Returns:
        A dictionary containing menu items and links.

    """

    global lib
    menu_items = {}
    templates = template_walker(os.path.join(settings.BASE_DIR,
                                             settings.SG_PATTERN_DIR,
                                             settings.SG_LIBS[lib]["dir"])
                                             , "mote_")

    # Search through a list of all template paths and
    # generate corresponding menu items
    for object in templates["files"]:

        search_str = object.replace(settings.SG_PATTERN_DIR, '')
        search_str = search_str.replace(settings.SG_LIBS[lib]["dir"], '')

        pattern = re.search(r"\//(?P<category>\w+)/(?P<item>[\w-]+)/", search_str)

        category = pattern.group("category")
        item = pattern.group("item")

        if category not in menu_items:
            menu_items[category] = []

        menu_items[category].append(item)


    links = templates["files"]

    sorting_ref_json = open(settings.SG_LIBS[lib]["config"], "r+")
    sorting_ref = json.loads(sorting_ref_json.read(), object_pairs_hook=OrderedDict)["sorting"]

    cprint(sorting_ref, "red", "on_white")
    cprint(menu_items, "blue", "on_white")

    for item in menu_items:
        if item in sorting_ref:
            menu_items[item] = sorting_ref[item]
        else:
            sorting_ref[item] = menu_items[item]

    # cprint(sorting_ref, "red", "on_white")

    new_dict = OrderedDict(sorting_ref)

    print menu_items, links
    return {"menu_items": new_dict, "links": links}

def create_pattern(request, library):
    global lib
    lib = library

    pattern_type = request.GET.get('type', '')
    pattern_name = request.GET.get('name', '')
    pattern_desc = request.GET.get('desc', '')

    pattern_match = "*" + pattern_type
    walk_path = glob.glob(os.path.join(settings.BASE_DIR,
                                       settings.SG_PATTERN_DIR,
                                       settings.SG_LIBS[lib]["dir"],
                                       pattern_match))[0]

    pattern_literal = os.path.split(walk_path)[1]

    directory = os.path.join(settings.BASE_DIR,
                             settings.SG_PATTERN_DIR,
                             settings.SG_LIBS[lib]["dir"],
                             pattern_literal,
                             pattern_name)

    if not os.path.exists(directory):
        os.makedirs(directory)
        sg_dir = os.path.join(directory, "mote")
        os.makedirs(sg_dir)

    sg_path = os.path.join(sg_dir, "mote_" + pattern_name + ".html")
    sg_file = open(sg_path, "w+")
    sg_template_path = os.path.join(settings.TEMPLATES[0]["DIRS"][0], 'mote/mote_pattern.html')

    sg_template = open(sg_template_path, 'r+')

    sg_string = sg_template.read()
    sg_string = sg_string.replace("_PATTERN_NAME", pattern_name)
    sg_string = sg_string.replace("_PATTERN_DESC", pattern_desc)
    sg_file.write(sg_string)

    pattern_path = os.path.join(directory, pattern_name + ".html")
    pattern_file = open(pattern_path, "w+")
    pattern_file.write("");

    return HttpResponse("success")

def sort_menu(request):
    pattern_list_json = request.POST.get("pattern_list", "")
    lib = request.POST.get("library", "")
    pattern_list = json.loads(pattern_list_json, object_pairs_hook=OrderedDict)

    # return HttpResponse(pattern_list)

    with open(settings.SG_LIBS[lib]["config"], "r+") as f:
        data = f.read()
        config = json.loads(data, object_pairs_hook=OrderedDict)
        config["sorting"] = pattern_list
        output = json.dumps(config, sort_keys=False, indent=4, separators=(',', ': '))

        f.seek(0)
        f.write(output)
        f.truncate()


    return HttpResponse('success')
