
from odoo import models, fields, _
import datetime
from datetime import timedelta
import pytz

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col - 1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class AgeingReport(models.AbstractModel):
    _name = 'report.ageing.xlsx'
    _inherit = 'report.report_xlsx.abstract'


    def _get_invoice_address(self, part):
        inv_addr_id = part.address_get(["invoice"]).get("invoice", part.id)
        return self.env["res.partner"].browse(inv_addr_id)

    def _format_date_to_partner_lang(
        self, date, date_format=DEFAULT_SERVER_DATE_FORMAT
    ):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        return date.strftime(date_format) if date else ""

    def _get_account_display_lines(
        self, company_id, partner_ids, date_start, date_end, account_type, sale_rep_id
    ):
        raise NotImplementedError

    def _get_account_initial_balance(
        self, company_id, partner_ids, date_start, account_type
    ):
        return {}

    def _show_buckets_sql_q1(self, partners, date_end, account_type, sale_rep_id, partner_id):

        if sale_rep_id:
            sale_rep_id = tuple([sale_rep_id.id])
        else:
            sale_rep_id = tuple(self.env['sales.repo'].search([]).ids)
        partner_data = []
        if partner_id:
            partner_data.append(partner_id.id)
            partner_data = tuple(partner_data)
        else:
            partner_data = partners


        return str(
            self._cr.mogrify(
                """
            SELECT l.partner_id,p.name as partner_name,rp.name as sale_rep,p.ref as ref, l.currency_id, l.company_id, l.move_id,
            CASE WHEN l.balance > 0.0
                THEN l.balance - sum(coalesce(pd.amount, 0.0))
                ELSE l.balance + sum(coalesce(pc.amount, 0.0))
            END AS open_due,
            CASE WHEN l.balance > 0.0
                THEN l.amount_currency - sum(coalesce(pd.debit_amount_currency, 0.0))
                ELSE l.amount_currency + sum(coalesce(pc.credit_amount_currency, 0.0))
            END AS open_due_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_move m ON (l.move_id = m.id)
            JOIN account_account aa ON (aa.id = l.account_id)
            JOIN res_partner p ON (p.id = l.partner_id)
            JOIN sales_repo rp ON (rp.id = p.sales_rep)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date <= %(date_end)s
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date <= %(date_end)s
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN %(partner_data)s AND aa.account_type = %(account_type)s AND p.sales_rep IN %(sale_rep_id)s
                                AND (
                                  (pd.id IS NOT NULL AND
                                      pd.max_date <= %(date_end)s) OR
                                  (pc.id IS NOT NULL AND
                                      pc.max_date <= %(date_end)s) OR
                                  (pd.id IS NULL AND pc.id IS NULL)
                                ) AND l.date <= %(date_end)s AND not l.blocked
                                  AND m.state IN ('posted')
            GROUP BY l.partner_id, l.currency_id, l.date, l.date_maturity,p.name,p.ref,rp.name,
                                l.amount_currency, l.balance, l.move_id,
                                l.company_id, l.id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _show_buckets_sql_q2(self, date_end, minus_30, minus_60, minus_90, minus_120):
        return str(
            self._cr.mogrify(
                """
            SELECT partner_id, currency_id, date_maturity, open_due, 
                open_due_currency, move_id, company_id,
            CASE
                WHEN %(date_end)s <= date_maturity AND currency_id is null
                    THEN open_due
                WHEN %(date_end)s <= date_maturity AND currency_id is not null
                    THEN open_due_currency
                ELSE 0.0
            END as current,
            CASE
                WHEN %(minus_30)s < date_maturity
                    AND date_maturity < %(date_end)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_30)s < date_maturity
                    AND date_maturity < %(date_end)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_1_30,
            CASE
                WHEN %(minus_60)s < date_maturity
                    AND date_maturity <= %(minus_30)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_60)s < date_maturity
                    AND date_maturity <= %(minus_30)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_30_60,
            CASE
                WHEN %(minus_90)s < date_maturity
                    AND date_maturity <= %(minus_60)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_90)s < date_maturity
                    AND date_maturity <= %(minus_60)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_60_90,
            CASE
                WHEN %(minus_120)s < date_maturity
                    AND date_maturity <= %(minus_90)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_120)s < date_maturity
                    AND date_maturity <= %(minus_90)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_90_120,
            CASE
                WHEN date_maturity <= %(minus_120)s
                    AND currency_id is null
                THEN open_due
                WHEN date_maturity <= %(minus_120)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_over_120
            FROM Q1
            GROUP BY partner_id, currency_id, date_maturity, open_due,
                open_due_currency, move_id, company_id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _show_buckets_sql_q3(self, company_id):
        return str(
            self._cr.mogrify(
                """
            SELECT Q2.partner_id, current, b_1_30, b_30_60, b_60_90, b_90_120,
                                b_over_120, p.name as partner_name,rp.name as sale_rep, p.ref as ref,
            COALESCE(Q2.currency_id, c.currency_id) AS currency_id
            FROM Q2
            JOIN res_company c ON (c.id = Q2.company_id)
            JOIN res_partner p ON (p.id=Q2.partner_id)
            JOIN sales_repo rp ON (rp.id=p.sales_rep)
            WHERE c.id = %(company_id)s
        """,
                locals(),
            ),
            "utf-8",
        )

    def _show_buckets_sql_q4(self):
        return """
            SELECT partner_id, currency_id, sum(current) as current, partner_name,ref,sale_rep,
                sum(b_1_30) as b_1_30, sum(b_30_60) as b_30_60,
                sum(b_60_90) as b_60_90, sum(b_90_120) as b_90_120,
                sum(b_over_120) as b_over_120
            FROM Q3
            GROUP BY partner_id, currency_id, partner_name, sale_rep,ref
        """

    def _get_bucket_dates(self, date_end, aging_type):
        return getattr(
            self, "_get_bucket_dates_%s" % aging_type, self._get_bucket_dates_days
        )(date_end)

    def _get_bucket_dates_days(self, date_end):

        return {
            "date_end": date_end,
            "minus_30": date_end - timedelta(days=30),
            "minus_60": date_end - timedelta(days=60),
            "minus_90": date_end - timedelta(days=90),
            "minus_120": date_end - timedelta(days=120),
        }

    def _get_bucket_dates_months(self, date_end):
        res = {}
        d = date_end
        for k in ("date_end", "minus_30", "minus_60", "minus_90", "minus_120"):
            res[k] = d
            d = d.replace(day=1) - timedelta(days=1)
        return res

    def _get_account_show_buckets(
        self, company_id, partner_ids, date_end, account_type, aging_type,sale_rep_id, partner_id
    ):
        buckets = dict(map(lambda x: (x, []), partner_ids))
        partners = tuple(partner_ids)
        full_dates = self._get_bucket_dates(date_end, aging_type)
        # pylint: disable=E8103
        # All input queries are properly escaped - false positive
        self.env.cr.execute(
            """
            WITH Q1 AS (%s),
                Q2 AS (%s),
                Q3 AS (%s),
                Q4 AS (%s)
            SELECT partner_id,partner_name,sale_rep,ref, currency_id, current, b_1_30, b_30_60, b_60_90,
                b_90_120, b_over_120,
                current+b_1_30+b_30_60+b_60_90+b_90_120+b_over_120
                AS balance
            FROM Q4
            GROUP BY partner_id,partner_name,sale_rep,ref, currency_id, current, b_1_30, b_30_60,
                b_60_90, b_90_120, b_over_120"""
            % (
                self._show_buckets_sql_q1(partners, date_end, account_type, sale_rep_id, partner_id),
                self._show_buckets_sql_q2(
                    full_dates["date_end"],
                    full_dates["minus_30"],
                    full_dates["minus_60"],
                    full_dates["minus_90"],
                    full_dates["minus_120"],
                ),
                self._show_buckets_sql_q3(company_id),
                self._show_buckets_sql_q4(),
            )
        )
        for row in self.env.cr.dictfetchall():
            buckets[row.pop("partner_id")].append(row)
        return buckets

    def _get_bucket_labels(self, date_end, aging_type):


        return getattr(
            self, "_get_bucket_labels_%s" % aging_type, self._get_bucket_dates_days
        )(date_end)

    def _get_bucket_labels_days(self, date_end):
        return [

            _("Current"),
            _("1 - 30 Days"),
            _("31 - 60 Days"),
            _("61 - 90 Days"),
            _("91 - 120 Days"),
            _("121 Days +"),
            _("Total"),
        ]

    def _get_bucket_labels_months(self, date_end):
        return [
            _("Current"),
            _("1 Month"),
            _("2 Months"),
            _("3 Months"),
            _("4 Months"),
            _("Older"),
            _("Total"),
        ]

    def _get_line_currency_defaults(self, currency_id, currencies, balance_forward):

        if currency_id not in currencies:
            # This will only happen if currency is inactive
            currencies[currency_id] = self.env["res.currency"].browse(currency_id)
        return (
            {
                "lines": [],
                "buckets": [],
                "balance_forward": balance_forward,
                "amount_due": balance_forward,
            },
            currencies,
        )



    def generate_xlsx_report(self, workbook, data, wiz):



        date_to = str(wiz.start_date) + ' ' + '23:59:59'
        date_from = str(wiz.end_date) + ' ' + '00:00:00'
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 15,
                                              })
        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bg_color': '#d4d4d3,',
                                                  'bold': True, 'size': 11,
                                                  })
        sub_heading_format_company = workbook.add_format({'align': 'left',
                                                          'valign': 'left',
                                                          'bold': True, 'size': 12,
                                                          })
        sub_heading_format_company_new = workbook.add_format({'align': 'left',
                                                          'valign': 'left',

                                                          'bold': True, 'size': 12,
                                                          })

        col_format = workbook.add_format({'valign': 'left',
                                          'align': 'left',
                                          'bold': True,
                                          'size': 10,
                                          'font_color': '#000000'
                                          })
        data_format = workbook.add_format({'valign': 'center',
                                           'align': 'center',
                                           'size': 10,
                                           'font_color': '#000000'
                                           })
        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Ageing Report')


        worksheet.set_column('A:A', 16)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 18)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 18)
        worksheet.set_column('F:F', 18)
        worksheet.set_column('G:G', 18)
        worksheet.set_column('H:H', 18)
        worksheet.set_column('I:I', 18)
        worksheet.set_column('J:J', 18  )
        worksheet.set_column('K:K', 25)
        worksheet.set_column('L:L', 25)
        worksheet.set_column('M:M', 25)
        worksheet.set_column('N:N', 25)
        worksheet.set_column('O:O', 25)
        worksheet.set_column('P:P', 25)
        worksheet.set_column('Q:Q', 25)
        worksheet.set_column('R:R', 12)
        worksheet.set_column('S:S', 12)
        worksheet.set_column('T:T', 25)
        worksheet.set_column('U:U', 25)
        worksheet.set_column('V:V', 12)
        worksheet.set_column('W:W', 12)
        worksheet.set_column('X:X', 12)
        worksheet.set_column('Y:Y', 12)
        worksheet.set_column('Z:Z', 12)
        worksheet.set_column('AA:AA', 12)
        worksheet.set_column('AB:AB', 12)
        worksheet.set_column('AC:AC', 12)
        worksheet.set_column('AD:AD', 12)
        worksheet.set_column('AE:AE', 25)
        worksheet.set_column('AF:AF', 25)
        worksheet.set_column('AG:AG', 18)
        worksheet.set_column('AH:AH', 25)
        worksheet.set_column('AI:AI', 25)
        worksheet.set_column('AJ:AJ', 25)
        worksheet.set_column('AK:AK', 25)
        row = 1
        worksheet.set_row(row, 20)
        starting_col = excel_style(row, 1)
        ending_col = excel_style(row, 5)
        from_date = datetime.datetime.strptime(str(wiz.start_date), '%Y-%m-%d').strftime('%d/%m/%Y')
        to_date = datetime.datetime.strptime(str(wiz.end_date), '%Y-%m-%d').strftime('%d/%m/%Y')

        worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                              "Ageing Report",
                              heading_format)
        row += 1
        worksheet.write(row, 0, "Start Date", sub_heading_format_company)
        worksheet.write(row, 1, from_date, data_format)
        worksheet.write(row, 3, "End Date", sub_heading_format_company)
        worksheet.write(row, 4, to_date, data_format)
        row += 2
        worksheet.write(row, 0, "PARTNER REF:", sub_heading_format_company_new)
        worksheet.write(row, 1, "NAME", sub_heading_format_company_new)
        worksheet.write(row, 2, "SALESMAN", sub_heading_format_company_new)
        worksheet.write(row, 3, "CURRENCY", sub_heading_format_company_new)
        worksheet.write(row, 4, "AMOUNT", sub_heading_format_company_new)
        worksheet.write(row, 5, "0 - 30", sub_heading_format_company_new)
        worksheet.write(row, 6, "31 - 60", sub_heading_format_company_new)
        worksheet.write(row, 7, "61 - 90", sub_heading_format_company_new)
        worksheet.write(row, 8, "91 - 120", sub_heading_format_company_new)
        worksheet.write(row, 9, "120 +", sub_heading_format_company_new)

        company_id = self.env.company.id
        partner_ids = self.env['res.partner'].search([]).ids
        date_start = wiz.start_date
        # if date_start and isinstance(date_start, str):
        #     date_start = datetime.strptime(
        #         date_start, DEFAULT_SERVER_DATE_FORMAT
        #     ).date()
        date_end = wiz.end_date
        if isinstance(date_end, str):
            date_end = datetime.datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        account_type = wiz.account_type
        aging_type = wiz.ageing_type
        sale_rep_id = wiz.sale_rep_id
        partner_id = wiz.partner_id

        today = fields.Date.today()
        amount_field = data.get("amount_field", "amount")


        # There should be relatively few of these, so to speed performance
        # we cache them - default needed if partner lang not set
        self._cr.execute(
            """
            SELECT p.id, l.date_format
            FROM res_partner p LEFT JOIN res_lang l ON p.lang=l.code
            WHERE p.id IN %(partner_ids)s
            """,
            {"partner_ids": tuple(partner_ids)},
        )
        date_formats = {r[0]: r[1] for r in self._cr.fetchall()}
        default_fmt = self.env["res.lang"]._lang_get(self.env.user.lang).date_format
        currencies = {x.id: x for x in self.env["res.currency"].search([])}

        res = {}

        balances_forward = self._get_account_initial_balance(
            company_id, partner_ids, date_start, account_type
        )



        buckets = self._get_account_show_buckets(
            company_id, partner_ids, date_end, account_type, aging_type, sale_rep_id, partner_id
        )
        bucket_labels = self._get_bucket_labels(date_end, aging_type)





        # organise and format for report
        format_date = self._format_date_to_partner_lang
        partners_to_remove = set()
        for partner_id in partner_ids:

            res[partner_id] = {
                "today": format_date(today, date_formats.get(partner_id, default_fmt)),
                "start": format_date(
                    date_start, date_formats.get(partner_id, default_fmt)
                ),
                "end": format_date(date_end, date_formats.get(partner_id, default_fmt)),
                "currencies": {},
            }
            currency_dict = res[partner_id]["currencies"]

            for line in balances_forward.get(partner_id, []):

                (
                    currency_dict[line["currency_id"]],
                    currencies,
                ) = self._get_line_currency_defaults(
                    line["currency_id"], currencies, line["balance"]
                )


            for line in buckets[partner_id]:
                if line["currency_id"] not in currency_dict:
                    (
                        currency_dict[line["currency_id"]],
                        currencies,
                    ) = self._get_line_currency_defaults(
                        line["currency_id"], currencies, 0.0
                    )
                line_currency = currency_dict[line["currency_id"]]
                line_currency["buckets"] = line

        buckets_to_remove = []

        for key,val in buckets.items():

            if not val:
                buckets_to_remove.append(key)
                # del buckets[key]
        # if any([v["lines"] or v["balance_forward"] for v in values]):

        for bucket in buckets_to_remove:
            del buckets[bucket]


        for partner in partner_ids:
            if partner in buckets:
                for bck in buckets[partner]:

                    row += 1
                    worksheet.write(row, 0, bck['ref'], data_format)
                    worksheet.write(row, 1, bck['partner_name'], data_format)
                    worksheet.write(row, 2, bck['sale_rep'], data_format)
                    worksheet.write(row, 3, 'SAR', data_format)
                    worksheet.write(row, 4, bck['balance'], data_format)

                    worksheet.write(row, 5, bck['current'] + bck['b_1_30'], data_format)
                    worksheet.write(row, 6, round(bck['b_30_60']), data_format)
                    worksheet.write(row, 7, bck['b_60_90'], data_format)
                    worksheet.write(row, 8, bck['b_90_120'], data_format)
                    worksheet.write(row, 9, bck['b_over_120'], data_format)
                    row += 1
