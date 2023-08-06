from . import schemas
from odoo.addons.component.core import Component


class CrmLeadService(Component):
    _inherit = "crm.lead.service"
    _name = "crm.lead.service"

    def _validator_create(self):
        validator_schema = super()._validator_create().copy()
        validator_schema.update(schemas.S_CRM_LEAD_CREATE)
        return validator_schema

    def _prepare_create(self, params):
        create_dict = super()._prepare_create(params)
        form_order_lines = params.get('order_lines', False)
        if form_order_lines:
            crm_order_lines_args = [
                line
                for line in form_order_lines
            ]
            crm_order_lines = self.env["crm.sale.order.line"].create(
                crm_order_lines_args)
            create_dict['crm_order_line_ids'] = [
                (6, 0, [line.id for line in crm_order_lines])]
        return create_dict
