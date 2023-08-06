from faker import Faker
from datetime import datetime, timedelta
import random

faker = Faker("es_CA")


def random_icc(odoo_env):
    icc_prefix = odoo_env['ir.config_parameter'].get_param(
        'somconnexio.icc_start_sequence'
    )
    random_part = [
        str(random.randint(0, 9))
        for _ in range(19-len(icc_prefix))
    ]
    return icc_prefix + "".join(random_part)


def random_ref():
    return str(random.randint(0, 99999))


def random_mobile_phone():
    """
    Returns a random 9 digit number starting with either 6 or 7
    """
    return str(random.randint(6, 7)) + str(random.randint(10000000, 99999999))


def random_landline_number():
    """
    Returns a random 9 digit number starting with either 8 or 9
    """
    return str(random.randint(8, 9)) + str(random.randint(10000000, 99999999))


def subscription_request_create_data(odoo_env):
    return {
        "partner_id": 0,
        "already_cooperator": False,
        "is_company": False,
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "email": faker.email(),
        "ordered_parts": 1,
        "share_product_id": odoo_env.browse_ref(
            "easy_my_coop.product_template_share_type_2_demo"
        ).product_variant_id.id,
        "address": faker.street_address(),
        "city": faker.city(),
        "zip_code": faker.postcode(),
        "country_id": odoo_env.ref("base.es"),
        "date": datetime.now() - timedelta(days=12),
        "company_id": 1,
        "source": "manual",
        "lang": random.choice(["es_ES", "ca_ES"]),
        "sponsor_id": False,
        "vat": faker.vat_id(),
        "discovery_channel_id": odoo_env.browse_ref(
            "somconnexio.other_cooperatives"
        ).id,
        "iban": faker.iban(),
        "state": "draft",
    }


def partner_create_data(odoo_env):
    return {
        "parent_id": False,
        "name": faker.name(),
        "email": faker.email(),
        "street": faker.street_address(),
        "street2": faker.street_address(),
        "city": faker.city(),
        "zip_code": faker.postcode(),
        "country_id": odoo_env.ref("base.es"),
        "state_id": odoo_env.ref("base.state_es_b"),
        "customer": True,
        "ref": random_ref(),
        "lang": random.choice(["es_ES", "ca_ES"]),
    }


def crm_lead_create(
    odoo_env, partner_id, service_category, portability=False, pack=False
):
    product_switcher = {
        "mobile": odoo_env.ref("somconnexio.TrucadesIllimitades20GBPack") if pack else odoo_env.ref("somconnexio.TrucadesIllimitades20GB"),  # noqa
        "fiber": odoo_env.ref("somconnexio.Fibra100Mb"),
        "adsl": odoo_env.ref("somconnexio.ADSL20MBSenseFix"),
        "4G": odoo_env.ref("somconnexio.Router4G"),
    }
    crm_lead_line_args = {
        "name": "CRM Lead",
        "product_id": product_switcher[service_category].id,
    }
    isp_info_args = (
        {
            "type": "portability",
            "previous_contract_type": "contract",
            "previous_provider": odoo_env.ref("somconnexio.previousprovider39").id,
            "phone_number": None,
            "previous_owner_vat_number": faker.vat_id(),
            "previous_owner_name": faker.first_name(),
            'previous_owner_first_name': faker.last_name(),
        }
        if portability
        else {"type": "new"}
    )

    if service_category == "mobile":
        isp_info_args.update({
            "phone_number": random_mobile_phone(),
            'icc': random_icc(odoo_env)
        })
        isp_info = odoo_env["mobile.isp.info"].create(isp_info_args)
        crm_lead_line_args.update({"mobile_isp_info": isp_info.id})
    else:
        isp_info_args.update(
            {
                "phone_number": "-" if service_category == "4G" else random_landline_number(),  # noqa
                "service_full_street": faker.address(),
                "service_city": faker.city(),
                "service_zip_code": "08015",
                "service_state_id": odoo_env.ref("base.state_es_b").id,
                "service_country_id": odoo_env.ref("base.es").id,
            }
        )
        isp_info = odoo_env["broadband.isp.info"].create(isp_info_args)
        crm_lead_line_args.update({"broadband_isp_info": isp_info.id})

    crm_lead_line_ids = [odoo_env["crm.lead.line"].create(crm_lead_line_args).id]

    if pack and service_category == "fiber":
        isp_info_args = {
            "type": "new",
            "phone_number": random_mobile_phone(),
        }
        isp_info = odoo_env["mobile.isp.info"].create({
            "type": "new",
            "phone_number": random_mobile_phone(),
            "icc": random_icc(odoo_env),
        })
        mobile_crm_lead_line_args = {
            "name": "CRM Lead",
            "product_id": product_switcher["mobile"].id,
            "mobile_isp_info": isp_info.id,
        }
        crm_lead_line_ids.append(
            odoo_env["crm.lead.line"].create(mobile_crm_lead_line_args).id
        )

    return odoo_env["crm.lead"].create(
        {
            "name": "Test Lead",
            "partner_id": partner_id.id,
            "iban": partner_id.bank_ids[0].sanitized_acc_number,
            "lead_line_ids": [(6, 0, crm_lead_line_ids)],
            "stage_id": odoo_env.ref("crm.stage_lead1").id,
        }
    )


def _mobil_service_product_create_data(odoo_env):
    return {
        "name": "Sense minutes",
        "type": "service",
        "categ_id": odoo_env.ref("somconnexio.mobile_service").id,
    }


def _fiber_service_product_create_data(odoo_env):
    return {
        "name": "Fiber 200 Mb",
        "type": "service",
        "categ_id": odoo_env.ref("somconnexio.broadband_fiber_service").id,
    }


def _adsl_service_product_create_data(odoo_env):
    return {
        "name": "ADSL 20Mb",
        "type": "service",
        "categ_id": odoo_env.ref("somconnexio.broadband_adsl_service").id,
    }


def _4G_service_product_create_data(odoo_env):
    return {
        "name": "Router 4G",
        "type": "service",
        "categ_id": odoo_env.ref("somconnexio.broadband_4G_service").id,
    }
