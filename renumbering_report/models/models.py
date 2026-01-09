
# from odoo import models, fields, api


# class PropertyRegistrationRenumbering(models.Model):
# 	_name = 'property.registration.renumbering'
# 	_description = 'Property File Renumbering Request'
# 	_inherit = ['mail.thread']
	
	
# 	@api.model
# 	def get_renumbering_report_data(self, docids):
# 		records = self.browse(docids)
		
# 		# Group by project
# 		grouped_by_project = {}
# 		for record in records:
# 			project = record.alif_link_sale
# 			project_key = project.id if project else 'general'
# 			project_name = project.name if project else 'General Projects'
			
# 			if project_key not in grouped_by_project:
# 				grouped_by_project[project_key] = {
# 					'project': project,
# 					'project_name': project_name,
# 					'records': []
# 				}
# 			grouped_by_project[project_key]['records'].append(record)
		
# 		sorted_groups = sorted(
# 			grouped_by_project.values(), 
# 			key=lambda x: x['project_name']
# 		)
		
# 		return sorted_groups