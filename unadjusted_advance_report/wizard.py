# #-*- coding:utf-8 -*-
from odoo import models, fields, api

class UnadjustedAdvanceWizard(models.TransientModel):
	_name = "unadjusted.advance.wizard"
	_description = 'Unadjust advance report'
	# form = fields.Date(string="From")
	# to = fields.Date(string="To")
	project = fields.Many2one('alif.project',string="Project")

	def print_report(self):
		data = {
			'form': self.read(['project'])[0] 
		}
		return self.env.ref('unadjusted_advance_report.report_unadjusted_advance').report_action(self, data=data)
