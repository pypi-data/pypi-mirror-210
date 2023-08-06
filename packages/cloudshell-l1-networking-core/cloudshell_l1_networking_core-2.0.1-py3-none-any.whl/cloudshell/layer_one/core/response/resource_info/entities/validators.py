from __future__ import annotations


class EntityValidator:
    @staticmethod
    def validate_id_for_name_template(resource_id: str | int) -> str:
        resource_id = str(resource_id)
        if not resource_id.isdigit():
            return resource_id
        else:
            return resource_id.zfill(2)
