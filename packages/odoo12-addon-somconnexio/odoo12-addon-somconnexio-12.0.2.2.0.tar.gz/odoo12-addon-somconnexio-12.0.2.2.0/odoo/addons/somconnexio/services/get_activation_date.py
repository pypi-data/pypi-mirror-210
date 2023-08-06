from datetime import date, timedelta


class GetActivationDate:
    def __init__(self, env):
        self.env = env

    def get_activation_date(self):
        """
        First working day after the 8th day from fiber contract creation
        """
        create_date = date.today()
        activaton_date = create_date + timedelta(days=8)
        holidays = self.env["hr.holidays.public.line"].sudo().search([]).mapped("date")
        while (
            activaton_date in holidays
            or not activaton_date.weekday() < 5  # 5 Sat, 6 Sun
        ):
            activaton_date = activaton_date + timedelta(days=1)
        return activaton_date
