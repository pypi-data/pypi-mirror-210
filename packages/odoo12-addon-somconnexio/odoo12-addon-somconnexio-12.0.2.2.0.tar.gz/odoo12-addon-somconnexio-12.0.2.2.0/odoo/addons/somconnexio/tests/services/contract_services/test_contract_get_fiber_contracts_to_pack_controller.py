import json
import odoo
from ...helpers import crm_lead_create
from ...common_service import BaseEMCRestCaseAdmin
from ....services.contract_contract_service import ContractService


from mock import patch, Mock
from datetime import date, timedelta
from pyotrs.lib import DynamicField
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffTicketConfiguration,
)


class TestContractGetFiberContractsNotPackedController(BaseEMCRestCaseAdmin):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env['contract.contract']

        mm_fiber_contract_service_info = self.env[
            'mm.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'mm_id': '123',
        })
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')
        partner_id = self.partner.id
        self.service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        product = self.browse_ref('somconnexio.Fibra100Mb')
        self.contract_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": "2020-01-01 00:00:00",
            "recurring_next_date": date.today() + timedelta(days=30),
        }
        self.fiber_signal = self.browse_ref(
            'somconnexio.FTTH_fiber_signal')

        self.vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mm_fiber_service_contract_info_id': (
                mm_fiber_contract_service_info.id
            ),
            'contract_line_ids': [
                (0, False, self.contract_line)
            ],
            'fiber_signal_type_id': self.fiber_signal.id
        }
        self.endpoint = "/api/contract/available-fibers-to-link-with-mobile"
        self.url = "{}?{}={}".format(self.endpoint, "partner_ref", self.partner.ref)

    def _null_side_effect(self, contracts):
        return contracts

    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets')  # noqa
    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines')  # noqa
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_ref_ok(self, mock_filter_ODOO_lead_lines,
                                                      mock_filter_OTRS_tickets):

        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        fiber_contract = self.Contract.create(self.vals_contract)

        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0]["id"], fiber_contract.id)
        self.assertEqual(
            result[0]["fiber_signal"], self.fiber_signal.code
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_ref_terminated(self):
        fiber_contract = self.Contract.create(self.vals_contract)
        fiber_contract.write({
            'is_terminated': True,
            'date_end': date.today(),
        })
        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets')  # noqa
    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines')  # noqa
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_two(self, mock_filter_ODOO_lead_lines,
                                                   mock_filter_OTRS_tickets):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        first_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract = self.Contract.create(self.vals_contract)

        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        self.assertEquals(len(result), 2)
        resulting_ids = [r["id"] for r in result]
        self.assertIn(first_fiber_contract.id, resulting_ids)
        self.assertIn(second_fiber_contract.id, resulting_ids)

    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets')  # noqa
    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines')  # noqa
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_one_already_in_pack(
            self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        first_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract = self.Contract.create(self.vals_contract)

        # Mobile contract
        mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
        })
        mobile_contract_line = self.contract_line.copy()
        mobile_contract_line.update({
            "name": "mobile contract line",
            "product_id": self.browse_ref('somconnexio.TrucadesIllimitades20GBPack').id
        })
        mobile_vals_contract = {
            'name': 'Test Contract Mbl',
            'partner_id': self.partner.id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                mobile_contract_service_info.id
            ),
            'contract_line_ids': [
                (0, False, mobile_contract_line)
            ],
        }
        mbl_contract = self.Contract.create(mobile_vals_contract)

        first_fiber_contract.write(
            {"children_pack_contract_ids": [(4, mbl_contract.id, 0)]}
        )

        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0]["id"], second_fiber_contract.id)

    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets')  # noqa
    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines')  # noqa
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_other_partner(
            self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        other_partner_id = self.ref("somconnexio.res_sponsored_partner_1_demo")
        vals_contract = self.vals_contract.copy()
        vals_contract.update({
            "partner_id": other_partner_id,
            "invoice_partner_id": other_partner_id,
            "service_partner_id": other_partner_id,
        })
        self.Contract.create(vals_contract)

        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets')  # noqa
    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines')  # noqa
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_already_packed(
            self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        mbl_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': "666777888",
            'icc': '123',
        })
        mbl_product = self.browse_ref('somconnexio.150Min1GB')
        mbl_contract_line = {
            "name": mbl_product.name,
            "product_id": mbl_product.id,
            "date_start": "2020-01-01 00:00:00",
            "recurring_next_date": date.today() + timedelta(days=30),
        }
        mbl_vals_contract = self.vals_contract.copy()
        mbl_vals_contract.update({
            "service_technology_id": self.ref(
                "somconnexio.service_technology_mobile"),
            "mm_fiber_service_contract_info_id": False,
            "mobile_contract_service_info_id": mbl_contract_service_info.id,
            "contract_line_ids": [(0, False, mbl_contract_line)],
        })
        mbl_contract = self.Contract.create(mbl_vals_contract)

        fiber_contract = self.Contract.create(self.vals_contract)
        mbl_contract.write({'parent_pack_contract_id': fiber_contract.id})

        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets')  # noqa
    @patch('odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines')  # noqa
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_technology(
            self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        mbl_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': "666777888",
            'icc': '123',
        })
        mbl_product = self.browse_ref('somconnexio.150Min1GB')
        mbl_contract_line = {
            "name": mbl_product.name,
            "product_id": mbl_product.id,
            "date_start": "2020-01-01 00:00:00",
            "recurring_next_date": date.today() + timedelta(days=30),
        }
        mbl_vals_contract = self.vals_contract.copy()
        mbl_vals_contract.update({
            "service_technology_id": self.ref(
                "somconnexio.service_technology_mobile"),
            "mm_fiber_service_contract_info_id": False,
            "mobile_contract_service_info_id": mbl_contract_service_info.id,
            "contract_line_ids": [(0, False, mbl_contract_line)],
        })
        self.Contract.create(mbl_vals_contract)

        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_no_partner(self):
        fake_partner_ref = "234252"
        url = "{}?{}={}".format(self.endpoint, "partner_ref", fake_partner_ref)
        response = self.http_get(url)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_bad_request(self):
        url = "{}?{}={}".format(self.endpoint, "partner_nif", self.partner.ref)

        response = self.http_get(url)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.reason, "BAD REQUEST")

    @patch('odoo.addons.somconnexio.services.contract_contract_service.SearchTicketsService')  # noqa
    def test_filter_out_fibers_used_in_OTRS_tickets(
            self, MockSearchTicketsService):
        first_code = '10'
        first_fiber_contract = self.Contract.create(self.vals_contract)
        first_fiber_contract.write({'code': first_code})
        second_code = '11'
        second_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract.write({'code': second_code})

        expected_dct = {"OdooContractRefRelacionat": [first_code, second_code]}
        expected_DF = DynamicField(
            name="OdooContractRefRelacionat",
            value=second_code
        )

        mock_ticket = Mock(spec=["response"])
        mock_ticket.response = Mock(spec=["dynamic_field_get"])
        # A ticket with second_code referenced in
        # OdooContractRefRelacionat DF will be found
        mock_ticket.response.dynamic_field_get.return_value = \
            expected_DF

        MockSearchTicketsService.return_value = Mock(spec=["search"])
        MockSearchTicketsService.return_value.search.return_value = \
            [mock_ticket]

        contract_service = ContractService(self.env)
        filtered_contracts = \
            contract_service._filter_out_fibers_used_in_OTRS_tickets(
                first_fiber_contract + second_fiber_contract)

        MockSearchTicketsService.assert_called_once_with(
            ChangeTariffTicketConfiguration)
        MockSearchTicketsService.return_value.search.assert_called_once_with(  # noqa
            self.partner.ref, df_dct=expected_dct
        )
        mock_ticket.response.dynamic_field_get.assert_called_with(
            "OdooContractRefRelacionat"
        )
        self.assertEqual(len(filtered_contracts), 1)
        # Only first fiber contract available
        self.assertEqual(filtered_contracts, first_fiber_contract)

    def test_filter_out_fibers_used_in_OTRS_tickets_empty(self):
        contracts = []
        service = ContractService(self.env)
        filtered_contracts = \
            service._filter_out_fibers_used_in_OTRS_tickets(contracts)

        self.assertFalse(filtered_contracts)

    def test_filter_out_fibers_used_in_ODOO_lead_lines(self):
        first_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract = self.Contract.create(self.vals_contract)
        third_fiber_contract = self.Contract.create(self.vals_contract)

        # Cancelled
        first_mbl_crm_lead = crm_lead_create(self.env, self.partner, "mobile")
        first_mbl_isp_info = first_mbl_crm_lead.lead_line_ids[0].mobile_isp_info
        first_mbl_isp_info.linked_fiber_contract_id = first_fiber_contract.id
        first_mbl_crm_lead.action_set_cancelled()

        # Already linked lead line
        second_mbl_crm_lead = crm_lead_create(self.env, self.partner, "mobile")
        second_mbl_isp_info = second_mbl_crm_lead.lead_line_ids[0].mobile_isp_info
        second_mbl_isp_info.linked_fiber_contract_id = second_fiber_contract.id

        # Unlinked lead line
        crm_lead_create(self.env, self.partner, "mobile")

        contract_service = ContractService(self.env)
        filtered_contracts = \
            contract_service._filter_out_fibers_used_in_ODOO_lead_lines(
                first_fiber_contract + second_fiber_contract +
                third_fiber_contract
            )

        self.assertEqual(len(filtered_contracts), 2)
        self.assertIn(first_fiber_contract, filtered_contracts)
        self.assertNotIn(second_fiber_contract, filtered_contracts)
        self.assertIn(third_fiber_contract, filtered_contracts)

    def test_filter_out_fibers_used_in_ODOO_lead_lines_empty(self):
        contracts = []
        service = ContractService(self.env)
        filtered_contracts = \
            service._filter_out_fibers_used_in_ODOO_lead_lines(
                contracts)

        self.assertFalse(filtered_contracts)
