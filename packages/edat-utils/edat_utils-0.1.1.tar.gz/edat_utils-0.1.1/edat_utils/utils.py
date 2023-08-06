from strawberry.types import Info

class EdatUtils:
    def get_fields(info: Info):
        selected_fields = {item.name for field in info.selected_fields
                           for selection in field.selections for item in selection.selections}
        return selected_fields