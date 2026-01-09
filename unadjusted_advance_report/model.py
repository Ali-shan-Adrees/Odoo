#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import pandas as pd
import numpy as np
import pandas.io.sql as psql
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)

class UnadjustedAdvance(models.AbstractModel):
	_name = 'report.unadjusted_advance_report.unadjusted_advance_template'
	_description = 'Unadjusted Advance Report'
	
	print("////////////////////////")
	
	@api.model
	def _get_report_values(self, docids, data=None):
		docs = self.env['unadjusted.advance.wizard'].browse(self.env.context.get('active_ids'))

		# Ensure project is not None
		project = docs.project or self.env['alif.project']
		results = {}


		print("????????????????")
		sql_supplier_payments_query = """
			SELECT
				pay.number AS payment_number,
				pay.amount AS amount,
				supp.name AS partner_id,
				pay.reference AS reference
			FROM
				customer_payment_bcube pay
			JOIN
				res_partner supp ON pay.partner_id = supp.id
			LEFT JOIN
				customer_payment_tree cpt ON pay.id = cpt.customer_payment_link
			WHERE
				cpt.id IS NULL
				AND pay.alif_link = %(project_id)s
			GROUP BY
				pay.number,
				pay.amount,
				supp.name,
				pay.reference
		"""
		self.env.cr.execute(sql_supplier_payments_query,{'project_id': project.id})
		supplier_payments_dct = self.env.cr.dictfetchall()

		for items in supplier_payments_dct:
			if items['amount']:
				if items['amount'] != None:
					if items['amount'] != [None]:
						items['project'] = project.name
					else:
						items.clear()
				else:
					items.clear()
			else:
				items.clear()


		# supplier_payments_dct = [item for item in supplier_payments_dct if item['amount']]
		
		print(supplier_payments_dct)
		
		docargs = {
			'doc_ids': docids,
			'doc_model': 'unadjusted.advance.wizard',
			'project': project,
			'supplier_payments_dct': supplier_payments_dct,
		}

		return docargs
