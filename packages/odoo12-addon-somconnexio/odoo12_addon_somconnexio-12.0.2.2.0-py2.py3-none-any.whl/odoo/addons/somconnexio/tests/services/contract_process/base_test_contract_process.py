from faker import Faker

from ...sc_test_case import SCTestCase


class BaseContractProcessTestCase(SCTestCase):
    def setUp(self):
        super().setUp()
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")

        self.iban = self.partner.bank_ids[0].acc_number

        fake = Faker("es-ES")

        self.mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.partner.bank_ids[0].id,
                "state": "valid",
                "partner_id": self.partner.id,
                "signature_date": fake.date_time_this_month(),
            }
        )

        self.service_address = {
            "street": fake.street_address() + " " + fake.secondary_address(),
            "zip_code": fake.postcode(),
            "city": fake.city(),
            "state": self.browse_ref("base.state_es_m").code,
            "country": self.browse_ref("base.es").code,
        }

        self.ticket_number = "1234"
