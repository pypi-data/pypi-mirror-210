from . import schemas
from odoo.addons.component.core import Component


class CrmLeadService(Component):
    _inherit = "crm.lead.service"
    _name = "crm.lead.service"

    def _validator_create(self):
        validator_schema = super()._validator_create().copy()
        validator_schema.update(schemas.S_CRM_LEAD_CREATE)
        return validator_schema
