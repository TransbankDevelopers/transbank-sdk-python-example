from django_components import component

@component.register("data_table")
class TbkTable(component.Component):
    template_name = "components/data_table.html"

    def get_context_data(self, data):
        return {"data": data}
