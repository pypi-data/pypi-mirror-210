import os.path
import pdb
from copy import copy

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from edc_action_item import action_fields
from edc_pdutils import SYSTEM_COLUMNS

style = color_style()


class Command(BaseCommand):

    help = "Generate STATA export script"

    def add_arguments(self, parser):
        parser.add_argument(
            "--odbc",
            dest="odbc_name",
            default="EDC_DB",
            help="ODBC connection name",
        )

    def handle(self, *args, **options) -> None:
        """
        odbc load, exec("<sql">) clear dsn("<ODBC_NAME>"); save <filename>, all emptyok
        """

        odbc_name = options.get("odbc_name")

        # get list of CRFs
        # get list of PRNs
        # get registered subject
        # get appointments
        # get AEs
        odbc_name = "META_DB"
        drop_prefix_for_dta = True
        crf_table_prefix = "meta_subject_"
        screening_table_prefix = "meta_screening"
        ae_table_prefix = "meta_ae_"
        prn_table_prefix = "meta_prn_"
        screening_table_prefix = "meta_screening_"
        consent_table_prefix = "meta_consent_"

        app_name = "meta_edc"
        db_name = "meta3_production"
        path = os.path.expanduser("~/meta_edc/stata")

        system_columns = copy(SYSTEM_COLUMNS)
        system_columns.extend(action_fields)
        system_columns.remove("created")
        system_columns.remove("modified")

        for model in django_apps.get_models():
            tbl = model._meta.db_table
            if tbl.startswith(crf_table_prefix):
                crf_field_list = ", ".join(
                    [
                        f"crf.{fld.name}"
                        for fld in model._meta.get_fields()
                        if fld.name not in system_columns
                    ]
                )
                sql = (
                    "select consent.subject_identifier, consent.gender, consent.dob, r.sid, "
                    "consent.consent_datetime, consent.site_id as site, "
                    "v.report_datetime as visit_datetime, "
                    "v.visit_code, v.visit_code_sequence, v.reason, "
                    f"{crf_field_list} from {db_name}.{tbl} as crf "
                    f"left join {db_name}.{crf_table_prefix}subjectvisit as v "
                    "on crf.subject_visit_id=v.id "
                    f"left join {db_name}.{consent_table_prefix}subjectconsent as consent "
                    "on consent.subject_identifier=v.subject_identifier "
                    f"left join {db_name}.edc_registration_registeredsubject as r "
                    "on r.subject_identifier=v.subject_identifier"
                )
                dta_filename = os.path.join(path, f"{tbl}.dta")
                if drop_prefix_for_dta:
                    dta_filename = dta_filename.replace(crf_table_prefix, "")
                statement = (
                    f'odbc load, exec("{sql}") clear dsn("{odbc_name}"); '
                    f"save {dta_filename}, all emptyok\n"
                )
            elif tbl.startswith(screening_table_prefix):
                print(statement)
        # for tbl in
        # template = odbc load, exec("selec * from mytable") clear dsn("REMOTE_DB")
