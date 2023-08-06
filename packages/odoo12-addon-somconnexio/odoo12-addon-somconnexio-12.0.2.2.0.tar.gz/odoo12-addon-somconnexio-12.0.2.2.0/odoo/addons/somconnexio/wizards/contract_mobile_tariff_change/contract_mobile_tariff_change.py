from datetime import date
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffTicket, ChangeTariffExceptionalTicket
)

from odoo import fields, api, _
from odoo.exceptions import MissingError, ValidationError

from ...services.contract_contract_service import ContractService
from ..contract_tariff_change.contract_tariff_change import (
    ContractTariffChangeWizard)
from ...helpers.date import first_day_next_month, date_to_str


class ContractMobileTariffChangeWizard(ContractTariffChangeWizard):
    _name = 'contract.mobile.tariff.change.wizard'

    fiber_contract_code_to_link = fields.Char()
    has_mobile_pack_offer_text = fields.Selection(
        [('yes', _('Yes')), ('no', 'No')],
        string='Is mobile pack offer available?',
        readonly=True
    )
    new_tariff_product_id = fields.Many2one(
        'product.product',
        string='New tariff',
        required=True
    )
    exceptional_change = fields.Boolean(default=False)
    send_notification = fields.Boolean(
        string='Send notification', default=False
    )
    otrs_checked = fields.Boolean(
        string='I have checked OTRS and no other tariff change is pending',
        default=False,
    )
    product_domain = fields.Char()
    location = fields.Char(
        related='contract_id.phone_number'
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['fiber_contract_code_to_link'] = \
            self._default_fiber_contract_code_to_link(
                self.env.context['active_id']
            )
        defaults['has_mobile_pack_offer_text'] = \
            "yes" if defaults['fiber_contract_code_to_link'] else "no"
        defaults['product_domain'] = self._default_product_domain(
            defaults['fiber_contract_code_to_link']
        )
        return defaults

    def _default_fiber_contract_code_to_link(self, contract_id):
        contract = self.env["contract.contract"].browse(contract_id)
        partner_ref = contract.partner_id.ref

        service = ContractService(self.env)
        try:
            fiber_contracts = service.get_fiber_contracts_to_pack(
                partner_ref=partner_ref)
        except MissingError:
            return False
        else:
            return fiber_contracts[0]['code']

    def _default_product_domain(self, has_mobile_pack_offer):
        mbl_product_templates = self.env["product.template"].search([
            ('categ_id', '=', self.env.ref('somconnexio.mobile_service').id),
        ])
        product_search_domain = [
            ('product_tmpl_id', 'in', mbl_product_templates.ids),
            ('active', '=', True),
            ('attribute_value_ids', '!=', self.env.ref('somconnexio.IsInPack').id)
        ]
        if has_mobile_pack_offer:
            del product_search_domain[-1]
        return product_search_domain

    def button_change(self):
        self.ensure_one()

        if not self.otrs_checked:
            raise ValidationError(_(
                "You must check if any previous tariff change is found in OTRS"
            ))

        partner = self.contract_id.partner_id

        if self.exceptional_change:
            self.start_date = date.today()
            Ticket = ChangeTariffExceptionalTicket
        else:
            self.start_date = first_day_next_month()
            Ticket = ChangeTariffTicket

        fields_dict = {
            "phone_number": self.contract_id.phone_number,
            "new_product_code": self.new_tariff_product_id.default_code,
            "current_product_code": self.current_tariff_product.default_code,
            "subscription_email": self.contract_id.email_ids[0].email,
            "effective_date": date_to_str(self.start_date),
            "language": partner.lang,
            "fiber_linked": False,
            "send_notification": self.send_notification,
        }

        if self.new_tariff_product_id.product_is_pack_exclusive:
            fields_dict["fiber_linked"] = self.fiber_contract_code_to_link

        Ticket(partner.vat, partner.ref, fields_dict).create()

        message = _("OTRS change tariff ticket created. Tariff to be changed from '{}' to '{}' with start_date: {}")  # noqa
        self.contract_id.message_post(
            message.format(
                self.current_tariff_contract_line.product_id.showed_name,
                self.new_tariff_product_id.showed_name,
                self.start_date,
            )
        )
        self._create_activity()
        return True
