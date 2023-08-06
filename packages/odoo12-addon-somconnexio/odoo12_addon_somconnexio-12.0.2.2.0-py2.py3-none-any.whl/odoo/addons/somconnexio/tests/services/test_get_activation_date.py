from ..sc_test_case import SCTestCase
from mock import patch
from datetime import date
from ...services.get_activation_date import GetActivationDate


class GetActivationDateTests(SCTestCase):

    @patch('odoo.addons.somconnexio.services.get_activation_date.date')
    def test_activation_date_no_holidays(self, mock_date):
        mock_date.today.return_value = date(2023, 3, 8)
        self.assertEquals(
            GetActivationDate(self.env).get_activation_date(),
            date(2023, 3, 16)
        )

    @patch('odoo.addons.somconnexio.services.get_activation_date.date')
    def test_activation_date_holidays(self, mock_date):
        mock_date.today.return_value = date(2023, 3, 8)
        holiday2 = self.env['hr.holidays.public'].create({
            'year': 2023,
            'country_id': self.env.ref('base.es').id
        })
        self.env['hr.holidays.public.line'].create({
            'name': 'holiday 5',
            'date': '2023-03-16',
            'year_id': holiday2.id
        })
        self.assertEquals(
            GetActivationDate(self.env).get_activation_date(),
            date(2023, 3, 17)
        )

    @patch('odoo.addons.somconnexio.services.get_activation_date.date')
    def test_activation_date_weekend(self, mock_date):
        mock_date.today.return_value = date(2023, 3, 10)
        self.assertEquals(
            GetActivationDate(self.env).get_activation_date(),
            date(2023, 3, 20)
        )
