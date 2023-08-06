from mock import patch
from datetime import date, datetime, timedelta

from ...helpers.date import first_day_next_month, date_to_str
from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError, MissingError


class TestContractTariffChangeWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.user_admin = self.browse_ref('base.user_admin')
        self.partner_id = self.browse_ref('somconnexio.res_partner_2_demo')
        partner_id = self.partner_id.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Service partner',
            'type': 'service'
        })
        masmovil_mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'icc': '123',
        })
        product = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        self.new_product = self.env.ref("somconnexio.150Min1GB")
        contract_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": datetime.now() - timedelta(days=12),
        }
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                masmovil_mobile_contract_service_info.id
            ),
            "contract_line_ids": [(0, 0, contract_line)],
            "email_ids": [(6, 0, [partner_id])],
        }
        self.contract = self.env["contract.contract"].create(vals_contract)

    @patch("odoo.addons.somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket")  # noqa
    @patch("odoo.addons.somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket")  # noqa
    @patch("odoo.addons.somconnexio.services.contract_contract_service.ContractService.get_fiber_contracts_to_pack")  # noqa
    def test_wizard_mobile_tariff_change_ok(
            self, mock_get_fiber_contracts_to_pack,
            MockExceptionalChangeTariffTicket, MockChangeTariffTicket):

        # No bonified mobile product available
        mock_get_fiber_contracts_to_pack.side_effect = MissingError("")

        wizard = self.env['contract.mobile.tariff.change.wizard'].with_context(  # noqa
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            "summary": "test",
            "new_tariff_product_id": self.new_product.id,
            "otrs_checked": True,
        })

        partner_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner_id.id)]
        )
        wizard.button_change()

        partner_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner_id.id)],
        )

        expected_start_date = first_day_next_month()
        self.assertEquals(len(partner_activities_after) -
                          len(partner_activities_before), 1)
        created_activity = partner_activities_after[-1]
        self.assertEquals(created_activity.user_id, self.user_admin)
        self.assertEquals(
            created_activity.activity_type_id,
            self.browse_ref('somconnexio.mail_activity_type_tariff_change')
        )
        self.assertEquals(created_activity.done, True)
        self.assertEquals(created_activity.summary, "test")

        # Check NO bonified product available
        self.assertIn(
            "('attribute_value_ids', '!=', " +
            str(self.env.ref('somconnexio.IsInPack').id) + ")",
            wizard.product_domain
        )
        self.assertEquals(wizard.start_date, expected_start_date)
        MockChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.new_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(expected_start_date),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": False,
                "send_notification": False,
            },
        )
        MockChangeTariffTicket.return_value.create.assert_called_once()
        MockExceptionalChangeTariffTicket.assert_not_called()

    @patch("odoo.addons.somconnexio.services.contract_contract_service.ContractService.get_fiber_contracts_to_pack")  # noqa
    def test_wizard_mobile_tariff_change_not_checked(
            self, mock_get_fiber_contracts_to_pack):

        mock_get_fiber_contracts_to_pack.side_effect = MissingError("")

        wizard = self.env['contract.mobile.tariff.change.wizard'].with_context(  # noqa
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            "summary": "test",
            "new_tariff_product_id": self.new_product.id,
        })

        self.assertRaisesRegex(
            ValidationError,
            "You must check if any previous tariff change is found in OTRS",
            wizard.button_change
        )

    @patch("odoo.addons.somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket")  # noqa
    @patch("odoo.addons.somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket")  # noqa
    @patch("odoo.addons.somconnexio.services.contract_contract_service.ContractService.get_fiber_contracts_to_pack")  # noqa
    def test_wizard_mobile_tariff_change_bonified_product_ok(
            self, mock_get_fiber_contracts_to_pack,
            MockExceptionalChangeTariffTicket, MockChangeTariffTicket):

        code = "828282"
        # Bonified product available
        mock_get_fiber_contracts_to_pack.return_value = [{"code": code}]

        self.pack_product = self.env.ref("somconnexio.TrucadesIllimitades20GBPack")

        wizard = self.env['contract.mobile.tariff.change.wizard'].with_context(  # noqa
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            "summary": "test",
            "new_tariff_product_id": self.pack_product.id,
            "otrs_checked": True,
        })
        wizard.button_change()

        # Check bonified product available
        self.assertNotIn(
            "('attribute_value_ids', '!=', " +
            str(self.env.ref('somconnexio.IsInPack').id) + ")",
            wizard.product_domain
        )
        MockChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.pack_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(first_day_next_month()),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": code,
                "send_notification": False,
            },
        )
        MockChangeTariffTicket.return_value.create.assert_called_once()
        MockExceptionalChangeTariffTicket.assert_not_called()

    @patch("odoo.addons.somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffTicket")  # noqa
    @patch("odoo.addons.somconnexio.wizards.contract_mobile_tariff_change.contract_mobile_tariff_change.ChangeTariffExceptionalTicket")  # noqa
    @patch("odoo.addons.somconnexio.services.contract_contract_service.ContractService.get_fiber_contracts_to_pack")  # noqa
    def test_wizard_mobile_exceptional_tariff_change_ok(
            self, mock_get_fiber_contracts_to_pack,
            MockExceptionalChangeTariffTicket, MockChangeTariffTicket):

        # No bonified mobile product available
        mock_get_fiber_contracts_to_pack.side_effect = MissingError("")

        wizard = self.env['contract.mobile.tariff.change.wizard'].with_context(  # noqa
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            "summary": "test",
            "exceptional_change": True,
            "new_tariff_product_id": self.new_product.id,
            "send_notification": True,
            "otrs_checked": True,
        })

        wizard.button_change()

        expected_start_date = date.today()

        self.assertEquals(wizard.start_date, expected_start_date)
        MockExceptionalChangeTariffTicket.assert_called_once_with(
            self.partner_id.vat,
            self.partner_id.ref,
            {
                "phone_number": self.contract.phone_number,
                "new_product_code": self.new_product.default_code,
                "current_product_code": self.contract.current_tariff_product.default_code,  # noqa
                "effective_date": date_to_str(expected_start_date),
                "subscription_email": self.partner_id.email,
                "language": self.partner_id.lang,
                "fiber_linked": False,
                "send_notification": True,
            },
        )
        MockExceptionalChangeTariffTicket.return_value.create.assert_called_once()
        MockChangeTariffTicket.assert_not_called()
