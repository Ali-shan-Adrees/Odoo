from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class PropertyRegistrationRenumbering(models.Model):
	_name = 'property.registration.renumbering'
	_description = 'Property File Renumbering Request'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
	alif_link_sale = fields.Many2one(
		'alif.project', 
		string="Project",
		compute='_compute_alif_link_sale',
		store=True,
		readonly=True,
		help="Automatically populated from the selected Sale Order's project"
	)
	@api.depends('old_file_id')
	def _compute_alif_link_sale(self):
		for record in self:
			if (record.old_file_id and 
				hasattr(record.old_file_id, 'alif_link_sale') and 
				record.old_file_id.alif_link_sale):
				record.alif_link_sale = record.old_file_id.alif_link_sale
			else:
				record.alif_link_sale = False
	old_file_id = fields.Many2one(
		'sale.order', 
		string='Old File (Sale Order)', 
		required=True, 
		tracking=True
	)
	
	old_file_name = fields.Char(
		string='Old File Name', 
		compute='_compute_old_file_name', 
		store=True, 
		readonly=True,
		tracking=True
	)
	
	new_file_name = fields.Char(
		string='New File Name', 
		required=True, 
		tracking=True,
		copy=False
	)
	original_sale_name = fields.Char(
		string='Original Sale Name',
		readonly=True,
		copy=False,
		help="Stores the Sale Order's name right before the renumbering is finalized."
	)
	state = fields.Selection([
		('draft', 'Draft'),
		('send_for_approval', 'Sent For Approval'),
		('first_approval', 'First Approval'),
		('approved', 'Approved'),
		('rejected', 'Rejected'),
	], string='Status', default='draft', tracking=True, copy=False)

	first_approval_name = fields.Char(
		string="First Approval By", 
		readonly=True, 
		tracking=True,
		help="Name of the user who granted the first approval."
	)
	
	second_approval_name = fields.Char(
		string="Second Approval By", 
		readonly=True, 
		tracking=True,
		help="Name of the user who granted the second approval."
	)
	# company_id = fields.Many2one('res.company', string='Company', required=True)

	def action_send_for_approval(self):
		if self.state != 'draft':
			raise UserError(_("Only draft records can be sent for approval."))
		
		# Check if new file name already exists before sending for approval
		self.check_duplicate_file_name()
		
		# Transition state and log message
		self.state = 'send_for_approval'
		self.message_post(body=_("Request sent for First Approval."))
	
	@api.depends('old_file_id')
	def _compute_old_file_name(self):
		for record in self:
			record.old_file_name = record.old_file_id.name if record.old_file_id else False

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('property.registration.renumbering') or _('New')
		return super(PropertyRegistrationRenumbering, self).create(vals)

	def unlink(self):
		for record in self:
			if record.state != 'draft':
				raise UserError(_("You can only delete Renumbering Requests that are in the 'Draft' state."))
		return super(PropertyRegistrationRenumbering, self).unlink()

	def action_first_approval(self):
		if self.state != 'send_for_approval':
			raise UserError(_("Record must be 'Send for Approval' to receive First Approval."))
		
		self.check_duplicate_file_name()
		
		if self.old_file_id and not self.original_sale_name:
			self.original_sale_name = self.old_file_id.name
			
		self.first_approval_name = self.env.user.name
		self.state = 'first_approval'
		self.action_name_changing()
		self.message_post(body=_("First Approval granted of Property Registration Renumbering."))

	def action_name_changing(self):
		if self.first_approval_name and self.second_approval_name:
			sale_order_records = self.env['sale.order'].search([
				('name', '=', self.original_sale_name),
				('alif_link_sale', '=', self.old_file_id.alif_link_sale.id),
				('plot_number', '=', self.old_file_id.plot_number.id),
				'|', ('active', '=', False), ('active', '=', True)
			])

			updated_count = 0
			for sale in sale_order_records:
				sale.write({'name': self.new_file_name})
				sale.message_post(body=_("This Property name has been changed form Registration Renumbering."))
				updated_count += 1

			if self.old_file_id.plot_number:
				self.old_file_id.plot_number.write({
					'name': self.new_file_name  
				})
				self.old_file_id.plot_number.message_post(body=_("This Unit name has been changed form Registration Renumbering."))
				if self.old_file_id.plot_number.product_variant_ids[0]:
					self.old_file_id.plot_number.product_variant_ids[0].write({
						'name': self.new_file_name
					})
					self.old_file_id.plot_number.product_variant_ids[0].message_post(body=_("This Product Template name has been changed from Registration Renumbering."))


			log_message = _("Sale Order name updated to: %s") % self.new_file_name
			
			if updated_count > 1:
				log_message += _(" (and %d related sale orders)") % (updated_count - 1)
			self.message_post(body=log_message)

		
		


	def action_second_approval(self):
		if self.state != 'first_approval':
			raise UserError(_("Record must have 'First Approval' before Second Approval."))
		
		# No need to check duplicate file name again since it was already done in first approval
		# and the sale orders have already been renamed
		
		self.second_approval_name = self.env.user.name
		self.state = 'approved'
		self.action_name_changing()
		self.message_post(body=_("Second Approval granted of Property Registration Renumbering."))

	def action_rejection(self):
		
		# If rejected after first approval, revert the name changes
		if self.state == 'first_approval' and self.old_file_id and self.original_sale_name:
			# Revert the main sale order
			self.old_file_id.write({'name': self.original_sale_name})
			
			# Find and revert related sale orders with the same criteria
			sale_order_records = self.env['sale.order'].search([
				('name', '=', self.new_file_name),
				('alif_link_sale', '=', self.old_file_id.alif_link_sale.id),
				('plot_number', '=', self.old_file_id.plot_number.id),
				'|', ('active', '=', False), ('active', '=', True)
			])
			
			reverted_count = 0
			for sale in sale_order_records:
				sale.write({'name': self.original_sale_name})
				reverted_count += 1
			
			# Log the revert
			log_message = _("Sale Order name reverted to: %s") % self.original_sale_name
			if reverted_count > 1:
				log_message += _(" (and %d related sale orders)") % (reverted_count - 1)
			self.message_post(body=log_message)
			
			self.original_sale_name = False
		
		self.state = 'rejected'
		self.message_post(body=_("Request was rejected and Sale Order names reverted."))

	def action_set_to_draft(self):
		
		if self.state == 'approved' and self.old_file_id and self.original_sale_name:
			# Revert the main sale order
			self.old_file_id.write({'name': self.original_sale_name})
			
			# Find and revert related sale orders with the same criteria
			sale_order_records = self.env['sale.order'].search([
				('name', '=', self.new_file_name),
				('alif_link_sale', '=', self.old_file_id.alif_link_sale.id),
				('plot_number', '=', self.old_file_id.plot_number.id),
				'|', ('active', '=', False), ('active', '=', True)
			])
			
			reverted_count = 0
			for sale in sale_order_records:
				sale.write({'name': self.original_sale_name})
				reverted_count += 1
			
			if self.old_file_id.plot_number:
				self.old_file_id.plot_number.write({
					'name': self.original_sale_name  
				})
			# Log the revert
			log_message = _("Sale Order name reverted to: %s") % self.original_sale_name
			if reverted_count > 1:
				log_message += _(" (and %d related sale orders)") % (reverted_count - 1)
			self.message_post(body=log_message)
			
			self.original_sale_name = False 
			
		elif self.state == 'approved' and not self.original_sale_name:
			self.message_post(body=_("Warning: Could not revert Sale Order name as the original name was not recorded."))
			
		if self.state not in ('rejected', 'approved', 'first_approval'):
			 raise UserError(_("Only rejected, approved, or first approval records can be set back to Draft."))
			 
		self.state = 'draft'
		self.first_approval_name = False
		self.second_approval_name = False
		self.message_post(body=_("Request set back to Draft."))

	def check_duplicate_file_name(self):
		"""Check if the new file name already exists in sale.order model"""
		for record in self:
			if record.new_file_name:
				# Check if any sale.order already has this name
				existing_sale = self.env['sale.order'].search([
					('name', '=', record.new_file_name)
				], limit=1)
				
				if existing_sale:
					raise ValidationError(
						_("File name '%s' already exists. Please choose a different file name.") % record.new_file_name
					)

	@api.constrains('new_file_name')
	def _check_new_file_name_unique(self):
		"""Constraint to validate new file name doesn't exist in sale.order"""
		for record in self:
			if record.new_file_name and record.state in ['draft', 'send_for_approval', 'first_approval']:
				record.check_duplicate_file_name()