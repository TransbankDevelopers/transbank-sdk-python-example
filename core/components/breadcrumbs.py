from django_components import component

@component.register("breadcrumbs")
class Breadcrumbs(component.Component):
    template_name = "components/breadcrumbs.html"

    def get_context_data(self, items):
        return {"items": items}
