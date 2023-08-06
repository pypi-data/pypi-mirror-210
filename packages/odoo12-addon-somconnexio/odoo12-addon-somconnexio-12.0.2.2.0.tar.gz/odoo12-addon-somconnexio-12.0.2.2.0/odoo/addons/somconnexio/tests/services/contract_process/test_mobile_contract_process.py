from mock import patch

from odoo.exceptions import UserError

from ....services.contract_process.fiber import FiberContractProcess
from ....services.contract_process.mobile import MobileContractProcess
from .base_test_contract_process import BaseContractProcessTestCase
from ...helpers import crm_lead_create


@patch("pyopencell.resources.subscription.Subscription.get")
@patch('odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractCreateService')  # noqa
class TestMobileContractProcess(BaseContractProcessTestCase):

    def setUp(self):
        super().setUp()
        self.data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [{
                "product_code": (
                    self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                "date_start": "2020-01-01 00:00:00"
            }],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        self.pack_code = self.browse_ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        ).default_code
        self.mobile_ticket_number = "123454321"
        self.fiber_ticket_number = "543212345"

        self.fiber_contract_data = {
            "partner_id": self.partner.ref,
            "email": self.partner.email,
            "service_address": self.service_address,
            "service_technology": "Fiber",
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                "vodafone_offer_code": "offer",
                "vodafone_id": "123",
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref("somconnexio.Fibra100Mb").default_code
                    ),
                    "date_start": "2020-01-01 00:00:00",
                }
            ],
            "iban": self.iban,
            "ticket_number": self.fiber_ticket_number,
        }

    def test_contract_create(self, *args):
        process = MobileContractProcess(self.env)
        content = process.create(**self.data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertIn(
            self.browse_ref('somconnexio.150Min1GB'), [
                c.product_id
                for c in contract.contract_line_ids
            ]
        )

    def test_contract_create_with_shared_data(self, *args):
        process = MobileContractProcess(self.env)
        shared_bond_id = "AAAA"

        mobile_content = self.data.copy()
        mobile_content["mobile_contract_service_info"].update({
            "shared_bond_id": shared_bond_id
        })

        content = process.create(**self.data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEqual(
            contract.mobile_contract_service_info_id.shared_bond_id,
            shared_bond_id
        )

    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.SetFiberContractCodeMobileTicket"  # noqa
    )
    def test_create_mobile_pack_contract_link_parent_contract(
        self, *args
    ):
        crm_lead = crm_lead_create(
            self.env, self.partner, "fiber", portability=False, pack=True
        )
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == self.pack_code:
                line.ticket_number = self.mobile_ticket_number
            else:
                line.ticket_number = self.fiber_ticket_number

        fiber_content = FiberContractProcess(self.env).create(
            **self.fiber_contract_data)
        fiber_contract = self.env["contract.contract"].browse(fiber_content["id"])
        mobile_content = self.data
        mobile_content.update({
            "ticket_number": self.mobile_ticket_number,
            "contract_lines": [{
                "product_code": self.pack_code,
                "date_start": "2020-01-01 00:00:00"
            }],
        })
        mobile_content = MobileContractProcess(self.env).create(**self.data)
        mobile_contract = self.env["contract.contract"].browse(mobile_content["id"])
        self.assertEqual(
            mobile_contract.parent_pack_contract_id,
            fiber_contract,
        )
        self.assertEqual(mobile_contract.number_contracts_in_pack, 2)
        self.assertTrue(mobile_contract.is_pack)

    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.SetFiberContractCodeMobileTicket"  # noqa
    )
    def test_create_mobile_pack_contract_link_with_contract_line(
        self, *args
    ):
        crm_lead = crm_lead_create(
            self.env, self.partner, "fiber", portability=False, pack=True
        )
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == self.pack_code:
                line.ticket_number = self.mobile_ticket_number
            else:
                line.ticket_number = self.fiber_ticket_number

        fiber_content = FiberContractProcess(self.env).create(
            **self.fiber_contract_data)
        fiber_contract = self.env["contract.contract"].browse(fiber_content["id"])
        mobile_content = self.data

        # Substitute a "contract_lines" list for a "contract_line" dict
        mobile_content.update({
            "ticket_number": self.mobile_ticket_number,
            "contract_line": {
                "product_code": self.pack_code,
                "date_start": "2020-01-01 00:00:00"
            },
        })
        mobile_content.pop("contract_lines")

        mobile_content = MobileContractProcess(self.env).create(**self.data)
        mobile_contract = self.env["contract.contract"].browse(mobile_content["id"])
        self.assertEqual(
            mobile_contract.parent_pack_contract_id,
            fiber_contract,
        )
        self.assertEqual(mobile_contract.number_contracts_in_pack, 2)
        self.assertTrue(mobile_contract.is_pack)

    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    def test_raise_error_if_not_found_parent_pack_contract(
        self, *args
    ):
        crm_lead = crm_lead_create(
            self.env, self.partner, "fiber", portability=False, pack=True
        )
        for line in crm_lead.lead_line_ids:
            if line.product_id.default_code == self.pack_code:
                line.ticket_number = self.mobile_ticket_number
            else:
                line.ticket_number = self.fiber_ticket_number
        mobile_content = self.data
        mobile_content.update({
            "ticket_number": self.mobile_ticket_number,
            "contract_lines": [{
                "product_code": self.pack_code,
                "date_start": "2020-01-01 00:00:00"
            }],
        })
        self.assertRaisesRegex(
            UserError,
            "Fiber contract of CRMLead ID = {}, ticket = {} not found".format(
                crm_lead.id,
                self.fiber_ticket_number,
            ),
            MobileContractProcess(self.env).create,
            **mobile_content
        )

    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    def test_create_mobile_pack_contract_link_known_fiber_contract(
        self, *args
    ):
        self.fiber_contract_data.update({"ticket_number": "867846"})
        fiber_content = FiberContractProcess(self.env).create(
            **self.fiber_contract_data)
        fiber_contract = self.env["contract.contract"].browse(fiber_content["id"])

        mobile_content = self.data
        mobile_content.update({
            "ticket_number": "34215134",
            "contract_lines": [{
                "product_code": self.pack_code,
                "date_start": "2020-01-01 00:00:00"
            }],
            "parent_pack_contract_id": fiber_contract.code
        })
        mobile_content = MobileContractProcess(self.env).create(**self.data)
        mobile_contract = self.env["contract.contract"].browse(mobile_content["id"])
        self.assertEqual(
            mobile_contract.parent_pack_contract_id,
            fiber_contract,
        )
        self.assertEqual(mobile_contract.number_contracts_in_pack, 2)
        self.assertTrue(mobile_contract.is_pack)

    @patch(
        "odoo.addons.somconnexio.services.contract_process.fiber.UnblockMobilePackTicket"  # noqa
    )
    def test_raise_error_if_not_found_parent_pack_contract_with_code(
        self, *args
    ):
        parent_contract_code = "272281"
        mobile_content = self.data
        mobile_content.update({
            "ticket_number": "",
            "contract_lines": [{
                "product_code": self.pack_code,
                "date_start": "2020-01-01 00:00:00"
            }],
            "parent_pack_contract_id": parent_contract_code
        })
        self.assertRaisesRegex(
            UserError,
            "Fiber contract with ref = {} not found".format(
                parent_contract_code,
            ),
            MobileContractProcess(self.env).create,
            **mobile_content
        )
