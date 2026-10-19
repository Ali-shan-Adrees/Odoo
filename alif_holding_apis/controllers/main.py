# -*- coding: utf-8 -*-
from odoo import http
import ast

from odoo.http import request

import requests
import json

import base64

import re
from datetime import datetime
import pytz
import difflib
from odoo import api, models
from odoo import _, api, fields, models
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from odoo.exceptions import ValidationError, UserError
import re
import logging
_logger = logging.getLogger(__name__)

class Main(http.Controller):

	@http.route('/items_details', type='json', auth='public')
	def get_products_details(self):
		# [('raw_product','!=',1),('plot_boolean','!=',1)]
		products = request.env['product.template'].sudo().search([])
		unique_list = []
		for product in products:
			unique_list.append({
				'product_id': product.id,
				'name': product.display_name,
				'sale_price': product.list_price,
				'cost': product.standard_price,
				'barcode': product.barcode,
				'category': product.categ_id.name,
				'uom_id': product.uom_id.id,
				'product_uom_name': product.uom_id.name,
			})

		unique_list = sorted(unique_list, key=lambda r: r['name'])
		return unique_list

	@http.route('/item_wise_details', type='jsonrpc', auth='public')
	def get_item_wise_details(self):
		unique_list = []
		if product_id:
			products = request.env['product.template'].sudo().search([
				('id', '=', int(product_id))
			])

			for product in products:
				unique_list.append({
					'product_id': product.id,
					'name': product.display_name,
					'sale_price': product.lst_price,
					'cost': product.standard_price,
					'barcode': product.barcode,
					'category': product.categ_id.name,
					'uom_id': product.uom_id.id,
					'product_uom_name': product.uom_id.name,
				})

		return sorted(unique_list, key=lambda r: r['name'])


	@http.route('/get_plot_details', type='json', auth='public')
	def get_plot_details(self):
		products = request.env['product.template'].sudo().search([('plot_boolean','=',1),('purchase_ok','=',0),('raw_product','=',0),('alif_link','!=',1)
			])
		unique_list = []
		for product in products:
			unique_list.append({
				'product_id': product.id,
				'name': product.display_name,
				'sale_price': product.list_price,
				'cost': product.standard_price,
				'barcode': product.barcode,
				'category': product.categ_id.name,
				'uom_id': product.uom_id.id,
				'product_uom_name': product.uom_id.name,
				})

		unique_list = sorted(unique_list, key=lambda r: r['name'])
		return unique_list

	@http.route('/category_details', type='json', auth='public')
	def get_category_details(self):
		products_category = request.env['product.category'].sudo().search([])
		unique_list = []
		for category in products_category:
			unique_list.append({
				'id': category.id,
				'name': category.display_name,
			})

		unique_list = sorted(unique_list, key=lambda r: r['name'])
		return unique_list

	@http.route('/partners_details', type='json', auth='public')
	def get_partners_details(self):
		partners = request.env['res.partner'].sudo().search([])
		partners_list = []
		for partner in partners:
			partners_list.append({
				'partner_id': partner.id,
				'name': partner.name,
			})

		partners_list = sorted(partners_list, key=lambda r: r['name'])
		return partners_list



	@http.route('/operation_type_details', type='json', auth='public')
	def get_picking_type_id_(self):
		picking_id = request.env['stock.picking.type'].sudo().search([])
		picking_id_list = []
		for picking_id in picking_id:
			picking_id_list.append({
				'picking_id': picking_id.id,
				'name': picking_id.display_name,
			})

		picking_id_list = sorted(picking_id_list, key=lambda r: r['name'])
		return picking_id_list

	@http.route(['/create_purchase_order'], type='json', auth='public',methods=['POST'])
	def create_purchase_order(self,**kwargs):
		po_record = request.env['purchase.order']
		po_data=request.jsonrequest

		new_list_order_lines = []

		if 'order_line' in po_data: 
			if len(po_data['order_line']) != 0: 
				for x in po_data['order_line']:
					product = request.env['product.product'].sudo().search([('id','=',int(x['product_id']))])
					if product:
						x['product_uom'] = product.uom_id.id
					new_list_order_lines.append((0,0,x))
				po_data['order_line'] = new_list_order_lines
		try:    
			po_created = po_record.sudo().create(po_data)
			return {'success':True,'po':po_created.id}
		except:
			return {'success':False,'po':False}


	@http.route('/get_vendors', type='json', auth='public')
	def get_vendors(self):
		suppliers = request.env['res.partner'].sudo().search([('supplier', '=', True)])
		supplier_list = []
		for supplier in suppliers:
			if supplier:
				supplier_list.append({
				'supplier_id': supplier.id,
				'name': supplier.name,
			})

		supplier_list = sorted(supplier_list, key=lambda r: r['name'])
		return supplier_list

	@http.route('/get_customers_unit_reg', type='json', auth='public')
	def get_customers_unit_reg(self):
		orders = request.env['sale.order'].sudo().search([('active', '=', True)])
		customer_list = []
		uni_customer_list = []
		for order in orders:
			if order.partner_id:
				if order.partner_id not in uni_customer_list:
					customer_list.append({
						'parent_id': order.partner_id.id,
						'name': order.partner_id.name,
					})
					uni_customer_list.append(order.partner_id)

		customer_list = sorted(customer_list, key=lambda r: r['name'])
		return customer_list

	@http.route('/get_customers', type='json', auth='public')
	def get_customers(self):
		orders = request.env['res.partner'].sudo().search([('active', '=', True)])
		customer_list = []
		uni_customer_list = []
		for order in orders:
			if order:
				if order not in uni_customer_list:
					customer_list.append({
						'customer_id': order.id,
						'name': order.name,
					})
					uni_customer_list.append(order)

		customer_list = sorted(customer_list, key=lambda r: r['name'])
		return customer_list    


	@http.route('/get_dealers', type='json', auth='public')
	def get_dealer(self):
		property_dealers = request.env['res.partner'].sudo().search([('property_dealer', '=', True)])
		property_dealer_list = []
		for property_dealer in property_dealers:
				property_dealer_list.append({
				'property_dealer': property_dealer.id,
				'name': property_dealer.name,
			})

		property_dealer_list = sorted(property_dealer_list, key=lambda r: r['name'])
		return property_dealer_list 


	@http.route('/get_grin_details', type='json', auth='public')
	def get_grin_details(self):
		# Search for stock pickings with the specified type
		picking_ids = request.env['stock.picking'].sudo().search([('picking_type_code', '=', 'incoming')])

		picking_data = []
		for picking in picking_ids:
			pack_operation_data = []
			for pack_operation in picking.pack_operation_product_ids:
				pack_operation_data.append({
					'product_id': pack_operation.product_id.id,
					'product_name': pack_operation.product_id.name,
					'quantity': pack_operation.product_qty,
					'qty_done': pack_operation.qty_done,
					'from_loc': pack_operation.from_loc,
					'to_loc': pack_operation.to_loc,
					'product_qty': pack_operation.product_qty,
					'qty_available': pack_operation.qty_available,
				})
		

			# Collect purchase_line_ids for each move line
			purchase_line_ids = [move.purchase_line_id.id for move in picking.move_lines if move.purchase_line_id]

			# Collecting all necessary picking data
			picking_data.append({
				'picking_name': picking.name,
				'picking_id': picking.id,
				'name': picking.partner_id.name,
				'min_date': picking.min_date,
				'origin': picking.origin,
				'state': picking.state,
				'id': picking.id,
				'purchase_line_ids': purchase_line_ids,  # A list of purchase_line_ids
				'picking_type_code': picking.picking_type_code,
				'alif_link_stock_picking_id': picking.alif_link_stock_picking.id,
				'alif_link_stock_picking_name': picking.alif_link_stock_picking.name,
				'location_dest_id': picking.location_dest_id.id,
				'location_dest_name': picking.location_dest_id.name,
				'location_id': picking.location_id.id,
				'location_name': picking.location_id.name,
				'pack_operation_product_ids': pack_operation_data,
			})

		return picking_data



	@http.route('/get_single_grin_details', type='json', auth='public')
	def get_single_grin_details(self):
		json_data = request.jsonrequest
		grin_id = json_data.get('grin_id')
		picking = request.env['stock.picking'].sudo().search([('id', '=', grin_id), ('picking_type_code', '=', 'incoming')])

		if not grin_id:
			return {'error': 'GRIN ID is required'}

		if not picking:
			return {'error': 'GRIN not found'}

		pack_operation_data = []
		for pack_operation in picking.pack_operation_product_ids:
			pack_operation_data.append({
				'product_id': pack_operation.product_id.id,
				'product_name': pack_operation.product_id.name,
				'quantity': pack_operation.product_qty,
				'qty_done': pack_operation.qty_done,
				'from_loc': pack_operation.from_loc,
				'to_loc': pack_operation.to_loc,
				'product_qty': pack_operation.product_qty,
				'qty_available': pack_operation.qty_available,
			})

		picking_data = {
			'picking_id': picking.id,
			'picking_name': picking.name,
			'name': picking.partner_id.name,
			'min_date': picking.min_date,
			'origin': picking.origin,
			'state': picking.state,
			'purchase_line_id': picking.move_lines.purchase_line_id.id,
			'picking_type_code': picking.picking_type_code,
			'alif_link_stock_picking_id': picking.alif_link_stock_picking.id,
			'alif_link_stock_picking_name': picking.alif_link_stock_picking.name,
			'location_dest_id': picking.location_dest_id.id,
			'location_dest_name': picking.location_dest_id.name,
			'location_id': picking.location_id.id,
			'location_name': picking.location_id.name,
			'pack_operation_product_ids': pack_operation_data,
		}

		return picking_data
	



	@http.route('/delete_grin', type='json', auth='public', methods=['POST'])
	def delete_grin(self, **kwargs):
		picking_id = kwargs.get('picking_id')

		if not picking_id:
			return {'success': False, 'message': 'Picking ID is required'}

		try:
			picking_record = request.env['stock.picking'].sudo().browse(picking_id)

			if not picking_record.exists():
				return {'success': False, 'message': 'Picking record not found'}

			pack_operations = picking_record.pack_operation_product_ids
			if pack_operations:
				pack_operations.sudo().unlink()

			picking_record.sudo().unlink()

			return {'success': True, 'message': 'Picking record deleted successfully'}
		except Exception as e:
			return {'success': False, 'message': str(e)}


	@http.route('/create_grin', type='json', auth='public', methods=['POST'])
	def create_grin(self, **kwargs):
		picking_record = request.env['stock.picking']
		picking_data = request.jsonrequest

		picking_dict = {
			'partner_id': picking_data.get('partner_id'),
			'origin': picking_data.get('origin'),
			'location_id': picking_data.get('location_id'),
			'location_dest_id': picking_data.get('location_dest_id'),
			'picking_type_id': picking_data.get('picking_type_id'),
			'scheduled_date': picking_data.get('scheduled_date'),
			
		}

		try:
			picking_created = picking_record.sudo().create(picking_dict)
			
			pack_operation_data = []
			for pack_operation in picking_created.pack_operation_product_ids:
				pack_operation_data.append({
					'product_id': pack_operation.product_id.id,
					'product_name': pack_operation.product_id.name,
					'quantity': pack_operation.product_qty,
					'qty_done': pack_operation.qty_done,
					'purchase_line_id': pack_operation.move_lines.purchase_line_id.id,
					'from_loc': pack_operation.from_loc,
					'to_loc': pack_operation.to_loc,
					'product_qty': pack_operation.product_qty,
					'qty_available': pack_operation.qty_available,
				})

	
			picking_details = {
				'picking_id': picking_created.id,
				'picking_name': picking_created.name,

				# 'name': picking_created.partner_id.name,
				# 'min_date': picking_created.min_date,
				# 'origin': picking_created.origin,
				# 'state': picking_created.state,
				# 'picking_type_code': picking_created.picking_type_code,
				# 'alif_link_stock_picking_id': picking_created.alif_link_stock_picking.id,
				# 'alif_link_stock_picking_name': picking_created.alif_link_stock_picking.name,
				# 'location_dest_id': picking_created.location_dest_id.id,
				# 'location_dest_name': picking_created.location_dest_id.name,
				# 'location_id': picking_created.location_id.id,
				# 'location_name': picking_created.location_id.name,
				# 'pack_operation_product_ids': pack_operation_data,
			}

			return {'success': True, 'grin_details': picking_details}
		except Exception as e:
			return {'success': False, 'message': str(e)}

	@http.route('/get_products_fixed_asset', type='json', auth='public')
	def get_products_fixed_asset(self):
		products = request.env['product.template'].sudo().search([('plot_boolean','=',1),('raw_product','=',0),('assets_product','=',1)])
		unique_list = []
		for product in products:
			unique_list.append({
				'product_id': product.id,
				'name': product.display_name,
				'sale_price': product.list_price,
				'cost': product.standard_price,
				'barcode': product.barcode,
				'category': product.categ_id.name,
				'uom_id': product.uom_id.id,
				'uom': product.uom_id.name,
				'asset_type' :product.asset_type,
				'assets_product' :product.assets_product,
				'plot_no': product.plot_no,
				'block' : product.block,
				'sector' : product.sector,
				'city' : product.city,
				'society_name' : product.scheme_name,
				'asset_type': product.asset_type,
				'vehicle_no': product.vehicle_no,
				'meter_reading': product.meter_reading,
				'engine_no': product.engine_no,
				'make': product.make,
				'model': product.model,

				'weight': product.weight,
				'rate': product.rate,
				'metal_number': product.metal_number,
				'metal_type':  product.metal_type,
				'metal_description': product.metal_description,
				'crypto_type': product.crypto_type,
				'crypto_number': product.crypto_number,
				'pair': product.pair,
				'crypto_foreign_currency': product.crypto_foreign_currency,
				'crypto_foreign_currency_rate,': product.crypto_foreign_currency_rate,
				'foreign_currency_rate': product.foreign_currency_rate,
				'foreign_currency_name': product.foreign_currency_name,
				'forex_qty': product.forex_qty,
				'forex_description': product.forex_description,
				'picture1': product.picture1,
				'picture2': product.picture2,
				'picture3': product.picture3,
				'picture4': product.picture4,
				
				'fur_name': product.fur_name,
				'fur_number': product.fur_number,
				'furniture_others_type': product.furniture_others_type,
				'used_new': product.used_new,
				'furniture_others_qty': product.furniture_others_qty,
				'fur_description': product.fur_description
			})

		unique_list = sorted(unique_list, key=lambda r: r['name'])
		return unique_list

	@http.route('/get_customer_receipt_invoices', type='json', auth='public')
	def get_customer_receipt_invoices(self, **kwargs):
		json_data = request.jsonrequest
		
		customer_id = json_data.get('customer_id')

		if customer_id != 0:
			invoices = request.env['account.invoice'].sudo().search([('partner_id', '=', customer_id)])
			
			response_data = []
			for invoice in invoices:
				response_data.append({
					"number": invoice.number or "",  
					"date": invoice.date_invoice or "",  
					"amount_total": invoice.amount_total or 0.0  
				})

			return {
				"success": True,
				"invoices": response_data
			}
		else:
			return {
				"success": False,
				"message": "Invalid customer ID (zero value)"
			}

	@http.route('/get_customer_receipt', type='json', auth='public')
	def get_customer_receipt(self, **kwargs):
		json_data = request.jsonrequest
		print(json_data)        
		customer_id = json_data.get('customer_id')
		number = json_data.get('number')    
		print(customer_id)
		print(number)
		if customer_id and number:
			payments = request.env['invoice.payment.tree'].sudo().search([
				('invoice_id.partner_id', '=', int(customer_id)),('invoice_id.number', '=', number),
				])
			response_data = []
			for receipt in payments:
				response_data.append({
					"customer_name": receipt.invoice_id.partner_id.name,
					"invoice_number": receipt.invoice_id.number,
					"status": receipt.invoice_id.state,
					"invoice_amount_total": receipt.invoice_id.amount_total,
					"invoice_id": receipt.invoice_id.id,
					"receipt_reference" : receipt.payment_id.reference,
					"receipt_date": receipt.date,
					"amount": receipt.amount,
					"receipt_number": receipt.payment_id.number,
					"receipt_id": receipt.payment_id.id,
				})
			return {
				"success": True,
				"recipts": response_data
			}               
		else:
			return {
				"success": False,
				"message": "No receipts found for customer {} and invoice number {}".format(customer_id, number)
			}

	@http.route('/get_customer_info', type='json', auth='public')
	def get_customer_info(self, **kwargs):
		json_data = request.jsonrequest
	
		customer_id = json_data.get('customer_id')
		
		customers = request.env['res.partner'].sudo().search([('id', '=', customer_id)])
		customer_data = []
		for customer in customers:
			associated_units = ', '.join(unit.name for unit in customer.associated_unit_ids)
			
			customer_data.append({
				'name': customer.name,
				'create_date': customer.create_date,
				'customer_id': customer.id,
				'website': customer.website,
				'associated_unit_ids': associated_units,
				'guardian': customer.guardian,
				'occupation': customer.function,
				'whatsapp_number': customer.whatsapp_number,
				'date_of_birth': customer.birthdate,
				'phone': customer.phone,
				'mobile': customer.mobile,
				'overseas_mobile': customer.overseas_mobile,
				'fax': customer.fax,
				'alif_link_res_partner': customer.alif_link_res_partner,
				'alif_dealer': customer.alif_dealer,
				'status': customer.status,
				'cnic': customer.cnic,
				'cnic_img': customer.cnic_img,
				'cnic_img_back': customer.cnic_img_back,
				'email_check': customer.email_check,
				'whatsapp_check': customer.whatsapp_check,
				'email': customer.email,
				'gi_code': customer.gi_code,
				'partner_code': customer.partner_code,
				'billing_code': customer.billing_code,
				'customer_short_code': customer.customer_short_code,
				'company_id': customer.company_id.name,
				'country': customer.country,
				'street': customer.street,
			})
	
		customer_data = sorted(customer_data, key=lambda r: r['name'])
		return customer_data

	@http.route('/get_vendor_info', type='json', auth='public')
	def get_vendor_info(self, **kwargs):
		json_data = request.jsonrequest
		vendor_id = json_data.get('vendor_id')
		
		vendors = request.env['res.partner'].sudo().search([('id', '=', vendor_id)])
		vendor_data = []
		for vendor in vendors:
			associated_units = ', '.join(unit.name for unit in vendor.associated_unit_ids)
			
			vendor_data.append({
				'name': vendor.name,
				'create_date': vendor.create_date,
				'vendor_id': vendor.id,
				'website': vendor.website,
				'associated_unit_ids': associated_units,
				'guardian': vendor.guardian,
				'occupation': vendor.function,
				'whatsapp_number': vendor.whatsapp_number,
				'date_of_birth': vendor.birthdate,
				'phone': vendor.phone,
				'mobile': vendor.mobile,
				'overseas_mobile': vendor.overseas_mobile,
				'fax': vendor.fax,
				'alif_link_res_partner': vendor.alif_link_res_partner,
				'alif_dealer': vendor.alif_dealer,
				'status': vendor.status,
				'cnic': vendor.cnic,
				'cnic_img': vendor.cnic_img,
				'cnic_img_back': vendor.cnic_img_back,
				'email_check': vendor.email_check,
				'whatsapp_check': vendor.whatsapp_check,
				'email': vendor.email,
				'gi_code': vendor.gi_code,
				'partner_code': vendor.partner_code,
				'billing_code': vendor.billing_code,
				'customer_short_code': vendor.customer_short_code,
				'company_id': vendor.company_id.name,
				'country': vendor.country,
				'street': vendor.street,
			})
		vendor_data = sorted(vendor_data, key=lambda r: r['name'])
		return vendor_data


	@http.route('/get_purchase_orders', type='json', auth='public')
	def get_purchase_orders(self, **kwargs):
		json_data = request.jsonrequest
		
		# date_from_str = json_data.get('date_from')
		# date_to_str = json_data.get('date_to')

		# date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
		# date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()

		purchase_orders = request.env['purchase.order'].sudo().search([])

		response_data = []
		for purchase_order in purchase_orders:
			order_date_str = purchase_order.date_order
			
			if order_date_str:
				order_date = datetime.strptime(order_date_str, '%Y-%m-%d %H:%M:%S').date()

				# if date_from <= order_date <= date_to:
				order_lines_data = []
				for order_line in purchase_order.order_line:
					order_line_data = {
						"product_id": order_line.product_id.name,
						"product_qty": order_line.product_qty,
						"price_unit": order_line.price_unit,
						"date_planned": order_line.date_planned
					}
					order_lines_data.append(order_line_data)

				response_data.append({
					"vendor": purchase_order.partner_id.name,
					"date_order": order_date_str,
					"po_number": purchase_order.name,
					"project": purchase_order.alif_link_purchase_order.name,
					"vendor_reference": purchase_order.partner_ref,
					"purpose": purchase_order.purpose,
					"order_lines": order_lines_data
				})
		
		return {
			"success": True,
			"Purchase Orders": response_data
		}


	@http.route('/get_purchase_order_info', type='json', auth='public')
	def get_purchase_order_info(self, **kwargs):
		json_data = request.jsonrequest
		
		po_number = json_data.get('po_number')
		
		if po_number:
			purchase_orders = request.env['purchase.order'].sudo().search([('name', '=', po_number)])
			if not purchase_orders:
				return {"error": "Purchase Order not found"}
			
			response_data = []
			for purchase_order in purchase_orders:
				order_lines_data = []
				for order_line in purchase_order.order_line:
					order_line_data = {
						"product_nane": order_line.product_id.name,
						"product_id": order_line.product_id.id,
						
						"product_qty": order_line.product_qty,
						"price_unit": order_line.price_unit,
						"date_planned": datetime.strptime(order_line.date_planned, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') if order_line.date_planned else None
					}
					order_lines_data.append(order_line_data)
				
				response_data.append({
					"vendor": purchase_order.partner_id.name,
					"date_order": purchase_order.date_order,
					"po_number": purchase_order.name,
					"vision_activity" : purchase_order.vision_activity,
					"nature_of_bill" : purchase_order.new_bill_nature,
					"type_of_bill" : purchase_order.type_of_bill,
					"vision_po_number" : purchase_order.vision_po_number,
					"project": purchase_order.alif_link_purchase_order.name,
					"project_id": purchase_order.alif_link_purchase_order.id,
					
					"vendor_reference": purchase_order.partner_ref,
					"purpose": purchase_order.purpose,
					"order_lines": order_lines_data
				})
			
			return response_data
		else:
			return {"error": "Invalid or missing PO number"}

	@http.route('/delete_purchase_order', type='json', auth='public')
	def delete_purchase_order(self, **kwargs):
		po_record = request.env['purchase.order']
		
		po_data = request.jsonrequest
		
		po_number = po_data.get('po_number')
		try:
			if 'po_number' in po_data and po_number:
				po_to_delete = po_record.sudo().search([('name', '=', po_number), ('state', 'in', ['draft', 'cancel'])])
				if po_to_delete:
					po_to_delete.state = 'cancel'
					po_to_delete.sudo().unlink()
					return {'success': True, 'message': 'Purchase Order deleted successfully'}
				else:
					return {'success': False, 'message': 'Purchase Order not found or cannot be deleted (not in Draft or Cancel state)'}
		except: 
			return {'success': False, 'message': 'To delete purchase order stage must be Cancel or Draft'}
		else:
			return {'success': False, 'message': 'Parameter po_number is missing or invalid'}


	@http.route('/get_initialized_purchase_orders', type='json', auth='public')
	def get_initialized_purchase_orders(self, **kwargs):
		json_data = request.jsonrequest
		purchase_orders = request.env['purchase.order'].sudo().search([('approve_state' ,'=','waiting')])
		response_data = []
		for purchase_order in purchase_orders:
			order_lines_data = []
			for order_line in purchase_order.order_line:
				order_line_data = {
					"product_id": order_line.product_id.name,
					"product_qty": order_line.product_qty,
					"price_unit": order_line.price_unit,
					"date_planned": order_line.date_planned
				}
				order_lines_data.append(order_line_data)
			response_data.append({
				"vendor": purchase_order.partner_id.name,
				"po_number": purchase_order.name,
				"approve_state" : purchase_order.approve_state,
				"project": purchase_order.alif_link_purchase_order.name,
				"vendor_reference": purchase_order.partner_ref,
				"purpose": purchase_order.purpose,
				"order_lines": order_lines_data
			})
		
		return {
			"success": True,
			"Purchase Orders": response_data
		}

	@http.route('/update_purchase_order_status', type='json', auth='public')
	def update_purchase_order_status(self, **kwargs):
		json_data = request.jsonrequest
		
		po_number = json_data.get('po_number')
		
		if po_number:
			purchase_orders = request.env['purchase.order'].sudo().search([('name', '=', po_number)])   
			response_data = []
			for purchase_order in purchase_orders:
				if purchase_order.approve_state == 'waiting':
					purchase_order.approve_state = 'approved'
				elif purchase_order.approve_state == 'approved':
					purchase_order.approve_state = 'waiting'
				order_lines_data = []               
				for order_line in purchase_order.order_line:
					

					order_line_data = {
						"product_id": order_line.product_id.name,
						"product_qty": order_line.product_qty,
						"price_unit": order_line.price_unit,
						"date_planned": order_line.date_planned,
					}
					order_lines_data.append(order_line_data)

				response_data.append({
					"approve_state" : purchase_order.approve_state,
					"vendor": purchase_order.partner_id.name,
					"date_order": purchase_order.date_order,
					"po_number": purchase_order.name,
					"project": purchase_order.alif_link_purchase_order.name,
					"vendor_reference": purchase_order.partner_ref,
					"purpose": purchase_order.purpose,
					"order_lines": order_lines_data
				})
			
			return response_data
		else:
			return {"error": "Invalid or missing PO number"}    


	@http.route('/get_customer_wise_project', type='json', auth='public')
	def get_customer_wise_project(self, **kwargs):
		json_data = request.jsonrequest
		partner_id = json_data.get('partner_id')

		customers = request.env['sale.order'].sudo().search([('partner_id', '=',partner_id),('active', '=', True)])

		seen_projects = set()
		customer_data = []
		
		for customer in customers:
			project_name = customer.alif_link_sale.name
			project_id = customer.alif_link_sale.id
			if project_id not in seen_projects:
				customer_data.append({
					"project": project_name,
					"project_id": project_id,
				})
				seen_projects.add(project_id)
		
		_logger.info(customer_data)
		_logger.info(customers)
		_logger.info("--------------")
		
		return customer_data
	 

	@http.route('/get_project_wise_units', type='json', auth='public')
	def get_project_wise_units(self, **kwargs):
		json_data = request.jsonrequest

		partner_id = json_data.get('partner_id')
		project_id = json_data.get('project_id')

		project = request.env['sale.order'].sudo().search([('partner_id', '=', partner_id), ('alif_link_sale.id', '=', project_id), ('active', '=', True)])

		if not project:
			return {"error": "Project not found"}
		units = []
		for plot in project:
			units.append({
				"unit_name": plot.plot_number.name,
				"unit_id ": plot.plot_number.id
			})
		return units


	@http.route('/get_open_installments', type='json', auth='public')
	def get_open_installments(self, **kwargs):
		json_data = request.jsonrequest

		partner_id = json_data.get('partner_id')
		project_id = json_data.get('project_id')
		plot_number_id = json_data.get('plot_number_id')
		project = request.env['sale.order'].sudo().search([
			('partner_id', '=', partner_id),
			('alif_link_sale.id', '=', project_id),
			('plot_number.id', '=', plot_number_id),
			('active', '=', True)
		], limit=1)

		if not project:
			return {"error": "Project not found"}

		lines_data = []
		for pipt_ids in project.pipt_ids:
			if pipt_ids.invoice_status == "open":
				line_data = {
					"invoice_status": pipt_ids.invoice_status,
					"amount_due": pipt_ids.due_amount,
					"installment_no": pipt_ids.name,
					"invoice_number" : pipt_ids.invoice_link.number,
					"invoice_id" : pipt_ids.invoice_link.id
					
				}
				lines_data.append(line_data)

		print(lines_data)            
		return {"open_invoices": lines_data}



	@http.route('/get_installments_details', type='json', auth='public')
	def get_installments_details(self, **kwargs):
		json_data = request.jsonrequest

		invoice_id = json_data.get('invoice_id')

		if not invoice_id:
			return {"error": "Invoice ID is required"}

		sale_order = request.env['sale.order'].sudo().search([
			('pipt_ids.invoice_link.id', '=', int(invoice_id))
		])

		if not sale_order:
			return {"error": "Installment not found for the provided invoice ID"}

		installment_line = sale_order.pipt_ids.filtered(lambda p: p.invoice_link.id == invoice_id)

		if not installment_line:
			return {"error": "Installment not found for the provided invoice ID"}

		installment_details = {
			"invoice_status": installment_line.invoice_status,
			"amount_due": installment_line.due_amount,
			"installment_no": installment_line.name,
			"invoice_number": installment_line.invoice_link.number,
			"amount" :  installment_line.amount,
			"due_date" :  installment_line.due_date,
			"approve_state " : installment_line.approve_state
		}

		return  installment_details



	@http.route('/update_product_asset_type_wise', type='json', auth='public', methods=['POST'])
	def update_product_asset_type_wise(self, **kwargs):
		json_data = request.jsonrequest

		product_id = json_data.get('product_id')
		print(product_id)
		if not product_id:
			return {'error': 'Product ID is required'}

		product = request.env['product.template'].sudo().search([('id', '=', product_id)], limit=1)
		if not product:
			return {'error': 'Product not found'}

		update_data = {}
		for field in [
			'name', 'asset_type', 'plot_no' , 'block', 'sector','scheme_name', 'city','vehicle_no', 'meter_reading', 'engine_no', 'make', 'model',
			'weight', 'rate', 'metal_number', 'metal_type', 'metal_description', 'crypto_type',
			'crypto_number', 'pair', 'crypto_forign_currency', 'crypto_forign_currency_rate',
			'forign_currency_rate', 'forign_currency_name', 'forex_qty', 'forex_description',
			'picture1','picture2','picture3','picture4', 'fur_number', 'fur_name','furniture_others_type', 'used_new', 'furniture_others_qty', 'fur_description'
		]:
			if field in json_data:
				update_data[field] = json_data[field]

		product.sudo().write(update_data)
		
		return {'success': True, 'product_id': product.id, 'product_name': product.name}



	@http.route('/update_purchase_order', type='json', auth='public')
	def update_purchase_order(self, **kwargs):
		po_record = request.env['purchase.order']
		po_data = request.jsonrequest

		po_number = po_data.get('po_number')

		if not po_number:
			return {'success': False, 'error': 'PO number not provided'}

		po_to_update = po_record.sudo().search([('name', '=', po_number)], limit=1)

		if not po_to_update:
			return {'success': False, 'error': 'Purchase Order not found'}

		new_list_order_lines = []
		if 'order_line' in po_data:
			if len(po_data['order_line']) != 0:
				for line in po_data['order_line']:
					product = request.env['product.product'].sudo().search([('id', '=', int(line['product_id']))])
					if product:
						line['product_uom'] = product.uom_id.id
					new_list_order_lines.append((0, 0, line))
		
		update_data = po_data.copy()
		if new_list_order_lines:
			update_data['order_line'] = [(5, 0, 0)] + new_list_order_lines 

		update_data.pop('po_number', None)

		try:
			po_to_update.sudo().write(update_data)
			return {'success': True, 'po': po_to_update.id}
		except:
			return {'success': False,}

		return {'success': False, 'error': 'Unexpected error occurred'}


	@http.route('/get_chart_of_accounts', type='json', auth='public')
	def get_chart_of_accounts(self):
		accounts = request.env['account.account'].sudo().search([])

		account_list = []
		for account in accounts:
			account_list.append({
				'account_id': account.id,
				'name': account.name,
				'code': account.code,
			})

		account_list = sorted(account_list, key=lambda r: r['name'])
		
		return account_list

		
		return {'success': False,}     

	@http.route(['/create_journal_entry'], type='json', auth='public', methods=['POST'])
	def create_journal_entry(self, **kwargs):
		journal_entry_record = request.env['account.move']
		journal_entry_data = request.jsonrequest

		new_line_ids = []
		if 'line_ids' in journal_entry_data:
			if len(journal_entry_data['line_ids']) != 0:
				for line in journal_entry_data['line_ids']:
					try:
						account = request.env['account.account'].sudo().search([('id', '=', int(line['account_id']))])
						if not account:
							_logger.error("Account with ID %s does not exist", line['account_id'])
							return {'success': False, 'error': 'Account with ID {} does not exist'.format(line['account_id'])}
						line['account_id'] = account.id
						new_line_ids.append((0, 0, line))
					except:
						return {'success': False,}
				journal_entry_data['line_ids'] = new_line_ids

		try:
			journal_entry_created = journal_entry_record.sudo().create(journal_entry_data)
			return {'success': True, 'journal_entry': journal_entry_created.id}

		except:
			return {'success': False,}
		return {'success': False,}



	
	@http.route(['/create_product_asset_type_wise'], type='json', auth='public', methods=['POST'])
	def create_product_asset_type_wise(self, **kwargs):
		product_record = request.env['product.template']
		product_data = request.jsonrequest
		
		product_data['assets_product'] = True

		product_created = product_record.sudo().create(product_data)
		
		return {'success': True, 'product_id': product_created.id, 'product_name': product_created.name}

	

	@http.route('/get_unit_info', type='json', auth='public')
	def get_unit_info(self, **kwargs):
		json_data = request.jsonrequest
		
		unit_id = json_data.get('unit_id')
		
		units = request.env['product.template'].sudo().search([('id', '=', unit_id)])
		unit_data = []
		for unit in units:
			sale_order = request.env['sale.order'].sudo().search([
				('plot_number', '=', unit.id),
				('stages', '=', 'validate'),
				('active', '=', True)
			], limit=1)
			print(sale_order)
			lines_data=[]
			for pipt_ids in sale_order.pipt_ids:
				if pipt_ids.invoice_status == "open":
					line_data = {
						"invoice_status": pipt_ids.invoice_status,
						"amount_due": pipt_ids.due_amount,
						"installment_no": pipt_ids.name
					}
					lines_data.append(line_data)
				else:
					print("No installment is in Open state ")
			unit_data.append({
				'name': unit.name,
				'create_date': unit.create_date,
				'dealer': unit.user_id.name,
				'project': unit.alif_link.name,
				'category': unit.categ_id.name,
				'block': unit.block,
				'sale_price': unit.list_price,
				'size': unit.plot_sq_ft,
				'floor': unit.floor,
				'sector' : unit.sector,
				'city' : unit.city,
				'plot_rate_marla' : unit.plot_rate_marla,
				'scheme_name' :unit.scheme_name,
				'plot_no' : unit.plot_no,
				'complete_address' : unit.complete_address,
				'type' : unit.type_of_plot,
				"ownership" : "100%",
				"installment_lines" : lines_data

			})
		unit_data = sorted(unit_data, key=lambda r: r['name'])
		return unit_data    

	@http.route('/get_bank_cash_accounts', type='json', auth='public')
	def get_bank_cash_accounts(self):
		accounts = request.env['account.account'].sudo().search([('bank', '=', True)])

		account_list = []
		for account in accounts:
			account_list.append({
				'account_id': account.id,
				'name': account.name,
				'code': account.code,
			})

		account_list = sorted(account_list, key=lambda r: r['name'])
		
		return account_list

		
		return {'success': False,}      

	@http.route('/create_vendor', type='json', auth='public', methods=['POST'])
	def create_vendor(self, **kwargs):
		json_data = request.jsonrequest

		try:
			associated_units = json_data['associated_units']
		except:
			associated_units = False

		try:
			function = json_data['function']
		except:
			function = False

		new_vendor = request.env['res.partner'].sudo().create({
			'name': json_data['name'],
			'website': json_data['website'],
			'guardian': json_data['guardian'],
			'whatsapp_number': json_data['whatsapp_number'],
			'birthdate': json_data['date_of_birth'],
			'phone': json_data['phone'],
			'mobile': json_data['mobile'],
			'email': json_data['email'],
			'supplier': True,
			'is_vendor':True,
			'associated_unit_ids': [(6,0,associated_units)] if associated_units else False,
			'function': function if function else '',
			'overseas_mobile': json_data['overseas_mobile'],
			'fax': json_data['fax'],
			'alif_link_res_partner': json_data.get('alif_link_res_partner',False) or False,
			'alif_dealer': json_data['alif_dealer'],
			'status': json_data['status'],
			'cnic': json_data['cnic'],
			'cnic_img': json_data['cnic_img'],
			'cnic_img_back': json_data['cnic_img_back'],
			'email_check': json_data['email_check'],
			'whatsapp_check': json_data['whatsapp_check'],
			'gi_code': json_data['gi_code'],
			'partner_code': json_data['partner_code'],
			'billing_code': json_data['billing_code'],
			'customer_short_code': json_data['customer_short_code'],
			'company_id': json_data['company_id'],
			'country': json_data['country'],
			'street': json_data['street'],
			'property_account_receivable_id': json_data.get('property_account_receivable_id'),
			'property_account_payable_id': json_data.get('property_account_payable_id')
		})

		return {
			'supplier_id': new_vendor.id,
			'name': new_vendor.name,
			'supplier': new_vendor.supplier,
			'message': 'Vendor created successfully.'
		}

	@http.route('/create_customer', type='json', auth='public', methods=['POST'])
	def create_customer(self, **kwargs):
		json_data = request.jsonrequest

		try:
			associated_units = json_data['associated_units']
		except:
			associated_units = False

		try:
			function = json_data['function']
		except:
			function = False

		new_customer = request.env['res.partner'].sudo().create({
			'name': json_data['name'],
			'website': json_data['website'],
			'guardian': json_data['guardian'],
			'whatsapp_number': json_data['whatsapp_number'],
			'birthdate': json_data['date_of_birth'],
			'phone': json_data['phone'],
			'mobile': json_data['mobile'],
			'email': json_data['email'],
			'supplier': False,
			'is_customer':True,
			'associated_unit_ids': [(6,0,associated_units)] if associated_units else False,
			'function': function if function else '',
			'overseas_mobile': json_data['overseas_mobile'],
			'fax': json_data['fax'],
			'alif_link_res_partner': json_data.get('alif_link_res_partner',False) or False,
			'alif_dealer': json_data['alif_dealer'],
			'status': json_data['status'],
			'cnic': json_data['cnic'],
			'cnic_img': json_data['cnic_img'],
			'cnic_img_back': json_data['cnic_img_back'],
			'email_check': json_data['email_check'],
			'whatsapp_check': json_data['whatsapp_check'],
			'gi_code': json_data['gi_code'],
			'partner_code': json_data['partner_code'],
			'billing_code': json_data['billing_code'],
			'customer_short_code': json_data['customer_short_code'],
			'company_id': json_data['company_id'],
			'country': json_data['country'],
			'street': json_data['street'],
			'property_account_receivable_id': json_data.get('property_account_receivable_id'),
			'property_account_payable_id': json_data.get('property_account_payable_id')

		})

		return {
			'customer_id': new_customer.id,
			'name': new_customer.name,
			'customer': new_customer.customer,
			'property_account_receivable_id': new_customer.property_account_receivable_id.id if new_customer.property_account_receivable_id else None,
			'property_account_receivable_id': new_customer.property_account_payable_id.id if new_customer.property_account_payable_id else None,
			'message': 'Customer created successfully.'
		}   



	@http.route('/update_customer', type='json', auth='public', methods=['POST'])
	def update_customer(self, **kwargs):
		json_data = request.jsonrequest

		# Extract customer ID
		try:
			customer_id = int(json_data.get('id'))
		except (TypeError, ValueError):
			return {'error': 'Invalid or missing customer ID.'}

		# Fetch the existing customer
		customer = request.env['res.partner'].sudo().browse(customer_id)
		if not customer.exists():
			return {'error': 'Customer not found.'}

		try:
			associated_units = json_data['associated_units']
		except:
			associated_units = False

		try:
			function = json_data['function']
		except:
			function = False

		# Prepare write values
		vals = {
			'name': json_data.get('name'),
			'website': json_data.get('website'),
			'guardian': json_data.get('guardian'),
			'whatsapp_number': json_data.get('whatsapp_number'),
			'birthdate': json_data.get('date_of_birth'),
			'phone': json_data.get('phone'),
			'mobile': json_data.get('mobile'),
			'email': json_data.get('email'),
			'supplier': False,
			'is_customer': True,
			'function': function if function else '',
			'overseas_mobile': json_data.get('overseas_mobile'),
			'fax': json_data.get('fax'),
			'alif_link_res_partner': json_data.get('alif_link_res_partner', False),
			'alif_dealer': json_data.get('alif_dealer'),
			'status': json_data.get('status'),
			'cnic': json_data.get('cnic'),
			'cnic_img': json_data.get('cnic_img'),
			'cnic_img_back': json_data.get('cnic_img_back'),
			'email_check': json_data.get('email_check'),
			'whatsapp_check': json_data.get('whatsapp_check'),
			'gi_code': json_data.get('gi_code'),
			'partner_code': json_data.get('partner_code'),
			'billing_code': json_data.get('billing_code'),
			'customer_short_code': json_data.get('customer_short_code'),
			'company_id': json_data.get('company_id'),
			'country': json_data.get('country'),
			'street': json_data.get('street'),
			'property_account_receivable_id': json_data.get('property_account_receivable_id'),
			'property_account_payable_id': json_data.get('property_account_payable_id'),
		}

		# Handle m2m field: associated_unit_ids
		if associated_units:
			vals['associated_unit_ids'] = [(6, 0, associated_units)]
		else:
			vals['associated_unit_ids'] = [(5, 0, 0)]  # Clear relation if empty

		# Remove keys with None values to avoid overwriting with null
		vals = {k: v for k, v in vals.items() if v is not None}

		# Update the customer
		customer.write(vals)

		return {
			'customer_id': customer.id,
			'name': customer.name,
			'message': 'Customer updated successfully.',
			'property_account_receivable_id': customer.property_account_receivable_id.id if customer.property_account_receivable_id else None,
			'property_account_payable_id': customer.property_account_payable_id.id if customer.property_account_payable_id else None,
		}



	@http.route('/update_vendor', type='json', auth='public', methods=['POST'])
	def update_vendor(self, **kwargs):
		json_data = request.jsonrequest

		try:
			vendor_id = int(json_data.get('id'))
		except (TypeError, ValueError):
			return {'error': 'Invalid or missing vendor ID.'}

		vendor = request.env['res.partner'].sudo().browse(vendor_id)
		if not vendor.exists() or not vendor.supplier:
			return {'error': 'Vendor not found or is not a supplier.'}

		try:
			associated_units = json_data['associated_units']
		except:
			associated_units = False

		try:
			function = json_data['function']
		except:
			function = False

		vals = {
			'name': json_data.get('name'),
			'website': json_data.get('website'),
			'guardian': json_data.get('guardian'),
			'whatsapp_number': json_data.get('whatsapp_number'),
			'birthdate': json_data.get('date_of_birth'),
			'phone': json_data.get('phone'),
			'mobile': json_data.get('mobile'),
			'email': json_data.get('email'),
			'supplier': True,  
			'is_vendor': True,
			'function': function if function else '',
			'overseas_mobile': json_data.get('overseas_mobile'),
			'fax': json_data.get('fax'),
			'alif_link_res_partner': json_data.get('alif_link_res_partner', False),
			'alif_dealer': json_data.get('alif_dealer'),
			'status': json_data.get('status'),
			'cnic': json_data.get('cnic'),
			'cnic_img': json_data.get('cnic_img'),
			'cnic_img_back': json_data.get('cnic_img_back'),
			'email_check': json_data.get('email_check'),
			'whatsapp_check': json_data.get('whatsapp_check'),
			'gi_code': json_data.get('gi_code'),
			'partner_code': json_data.get('partner_code'),
			'billing_code': json_data.get('billing_code'),
			'customer_short_code': json_data.get('customer_short_code'),
			'company_id': json_data.get('company_id'),
			'country': json_data.get('country'),
			'street': json_data.get('street'),
			'property_account_receivable_id': json_data.get('property_account_receivable_id'),
			'property_account_payable_id': json_data.get('property_account_payable_id'),
		}

		# Handle m2m field: associated_unit_ids
		if associated_units:
			vals['associated_unit_ids'] = [(6, 0, associated_units)]
		else:
			vals['associated_unit_ids'] = [(5, 0, 0)]  # Clear relation if empty

		# Remove keys with None values to avoid overwriting with null
		vals = {k: v for k, v in vals.items() if v is not None}

		# Update the vendor
		vendor.write(vals)

		return {
			'vendor_id': vendor.id,
			'name': vendor.name,
			'supplier': vendor.supplier,
			'message': 'Vendor updated successfully.',
			'property_account_receivable_id': vendor.property_account_receivable_id.id if vendor.property_account_receivable_id else None,
			'property_account_payable_id': vendor.property_account_payable_id.id if vendor.property_account_payable_id else None,
		}


	@http.route('/get_invoices', type='json', auth='public')
	def get_invoices(self, **kwargs):
		json_data = request.jsonrequest
		project_id = json_data.get('project_id')
		
		invoice_list = []
		invoices = request.env['account.invoice'].sudo().search([('alif_link_account_invoice', '=', project_id)])
			
		for invoice in invoices:
			invoice_list.append({
				'invoice_id': invoice.id,
				'number': invoice.number,
				'date_due': invoice.date_due,
				'invoice_date': invoice.date_invoice,
				'amount_total': invoice.amount_total,
				'unit_reg_link': invoice.plot_file_link.name,
			})

		return {'success': True, 'invoices': invoice_list}

	@http.route('/get_payment_methods', type='json', auth='public')
	def get_payment_methods(self):
		_logger.info("get_payment_methods route called")
		payment_methods = request.env['account.journal'].sudo().search([])
		method_list = []

		for method in payment_methods:
			method_list.append({
				'id': method.id,
				'name': method.name,
				'code': method.code or '',
				'type': method.type or '',
			})

		return method_list

	@http.route('/create_vendor_payment', type='json', auth='public', methods=['POST'])
	def create_vendor_receipt(self, **kwargs):
		payment_record = request.env['customer.payment.bcube']
		payment_data = request.jsonrequest

		name = payment_data.get('name')
		date = payment_data.get('date')
		cheque_no = payment_data.get('cheque_no')
		invoice_id = payment_data.get('invoice_id')
		account_id = payment_data.get('account_id')
		amount = payment_data.get('amount')
		journal_id = payment_data.get('journal_id')
		partner_id = payment_data.get('partner_id')
		date_tracking = payment_data.get('date_tracking')
		
		cheque = payment_data.get('cheque')
		journal_entry_id = payment_data.get('journal_entry_id')
		discount = payment_data.get('discount')
		advance_payment = payment_data.get('advance_payment')
		contract_ids = payment_data.get('contract_ids')
		contract_ids_list = []
		contract_ids_list.append('taxes')
		alif_link = payment_data.get('alif_link')
		reference = payment_data.get('reference')
		document = payment_data.get('document')
		payment_vals = {

			'name': name,
			'date': date,
			'amount': amount,
			"advance_payment" : advance_payment,
			'alif_link': alif_link,
			'discount' : discount,
			'invoice_id' : invoice_id,          
			'journal_id' : journal_id,
			'document' : document,
			'date_tracking' :date_tracking,
			'journal_entry_id' : journal_entry_id,
			'reference': reference,
			'account_id' : account_id,
			'partner_id': partner_id,
			'cheque': cheque,
			'cheque_no': cheque_no,
			# 'contract_ids': [(6, 0, contract_ids_list)] if contract_ids_list else False, 
		}
		payment_created = payment_record.sudo().create(payment_vals)
		payment_created.get_inv()
		payment_created.get_account()
		print("Payment Values:", payment_vals)

		for line in payment_created.customer_tree:
			if line.invoice_id.id == int(invoice_id):
				line.reconciled_amount_new = amount
				print(amount)
				print(line.reconciled_amount_new)

		payment_created.received_by_sale()

		return {'success': True, 'payment': payment_created.number}


	@http.route(['/create_customer_receipt'], type='json', auth='public', methods=['POST'])
	def create_customer_receipt(self, **kwargs):
		receipt_record = request.env['customer.payment.bcube']
		receipt_data = request.jsonrequest

		date = receipt_data.get('date')
		alif_link = receipt_data.get('alif_link')
		name = receipt_data.get('name')
		plot_number = receipt_data.get('plot_number')
		reference = receipt_data.get('reference')
		journal_entry_id = receipt_data.get('journal_entry_id')
		account_id = receipt_data.get('account_id')
		partner_id = receipt_data.get('partner_id')
		document = receipt_data.get('document')
		document_desc = receipt_data.get('document_desc')
		brs_desc = receipt_data.get('brs_desc')
		discount_only = receipt_data.get('discount_only')
		sale_order = receipt_data.get('sale_order')
		# date_tracking = receipt_data.get('date_tracking')
		journal_id = receipt_data.get('journal_id')
		cnic = receipt_data.get('cnic')
		payment_type = receipt_data.get('payment_type')
		receipts = receipt_data.get('receipts')
		other_receipts = receipt_data.get('other_receipts')
		amount = receipt_data.get('amount')
		invoice_id = receipt_data.get('invoice_id')

		receipt_vals = {
			'date': date,
			'alif_link': alif_link,
			'name': name,
			'plot_number': plot_number,
			'reference': reference,
			'account_id': account_id,
			'partner_id': partner_id,
			'document': document,
			'document_desc': document_desc,
			'brs_desc': brs_desc,
			'discount_only': discount_only,
			'sale_order': sale_order,
			'journal_id': journal_id,
			'cnic': cnic,
			'payment_type': payment_type,
			'receipts': receipts,
			'other_receipts': other_receipts,
			'amount': amount,
			'invoice_id': invoice_id,
		}

		receipt_created = receipt_record.sudo().create(receipt_vals)

		receipt_created.get_inv()
		receipt_created.get_account()

		for line in receipt_created.customer_tree:
			if line.invoice_id.id == int(invoice_id):
				line.reconciled_amount_new = amount
				print(amount)
				print(line.reconciled_amount_new)

		receipt_created.received_by_sale()

		return {'success': True, 'receipt': receipt_created.number} 

	@http.route('/get_locations', type='json', auth='public')
	def get_locations(self):
		locations = request.env['stock.location'].sudo().search([])
		locations_list = []
		for location in locations:
				locations_list.append({
				'location_id': location.location_id.id,
				'location_name': location.location_id.name,
				'full_name': location.name,
				'location_type': location.location_type,
				
			})

		locations_list = sorted(locations_list, key=lambda r: r['full_name'])
		return locations_list 




	@http.route('/update_contact_addresses', type='json', auth='public', methods=['POST'])
	def update_contact_addresses(self, **kwargs):
		json_data = request.jsonrequest
		contact_id = json_data.get('contact_id')

		if not contact_id:
			return {'error': 'Contact ID (contact_id) is required'}

		contact = request.env['res.partner'].sudo().browse(contact_id)
		if not contact.exists():
			return {'error': 'Contact not found'}

		update_values = {key: json_data[key] for key in json_data if key not in ['contact_id']}
		contact.sudo().write(update_values)

		return {
			'contact_id': contact.id,
			'name': contact.name,
			'email': contact.email,
			'phone': contact.phone,
			'mobile': contact.mobile,
			'message': 'Contact updated successfully'
		}
	
	
	@http.route('/delete_contact_addresses', type='json', auth='public', methods=['DELETE'])
	def delete_contact_addresses(self, **kwargs):
		json_data = request.jsonrequest
		contact_id = json_data.get('contact_id')

		if not contact_id:
			return {'error': 'Contact ID (contact_id) is required'}

		contact = request.env['res.partner'].sudo().browse(contact_id)
		if not contact.exists():
			return {'error': 'Contact not found'}

		contact.sudo().unlink()

		return {'message': 'Contact deleted successfully'}


	@http.route('/get_contact_addresses', type='json', auth='public', methods=['GET'])
	def get_contact_addresses(self, **kwargs):
		json_data = request.jsonrequest
		parent_id = json_data.get('parent_id')

		if not parent_id:
			return {'error': 'Customer ID (parent_id) is required'}

		parent = request.env['res.partner'].sudo().browse(parent_id)
		if not parent.exists():
			return {'error': 'Customer not found'}

		contacts = parent.child_ids.filtered(lambda c: c.type == 'contact')
		if not contacts:
			return {'error': 'No contacts found for this customer'}

		contact_list = [{
			'contact_id': contact.id,
			'name': contact.name,
			'email': contact.email,
			'phone': contact.phone,
			'mobile': contact.mobile,
			'function': contact.function
		} for contact in contacts]

		return {'contacts': contact_list}

	@http.route('/get_nominees', type='json', auth='public', methods=['GET'])
	def get_nominees(self, **kwargs):
		json_data = request.jsonrequest
		parent_id = json_data.get('parent_id')

		if not parent_id:
			return {'error': 'Parent ID is required'}

		nominees = request.env['nominee.info'].sudo().search([('tree_link', '=', parent_id)])

		if not nominees:
			return {'error': 'No nominees found'}

		nominee_list = []
		for nominee in nominees:
			nominee_list.append({
				'nominee_id': nominee.id,
				'name': nominee.name,
				'guardian': nominee.guardian,
				'cnic': nominee.cnic,
				'relation': nominee.relation,
				'phone': nominee.phone,
				'email': nominee.email,
			})

		return {'nominees': nominee_list}

	@http.route('/update_nominee', type='json', auth='public', methods=['POST'])
	def update_nominee(self, **kwargs):
		json_data = request.jsonrequest
		nominee_id = json_data.get('nominee_id')

		if not nominee_id:
			return {'error': 'Nominee ID is required'}

		nominee = request.env['nominee.info'].sudo().browse(nominee_id)
		if not nominee.exists():
			return {'error': 'Nominee not found'}

		nominee.sudo().write({
			'name': json_data.get('name', nominee.name),
			'guardian': json_data.get('guardian', nominee.guardian),
			'cnic': json_data.get('cnic', nominee.cnic),
			'passport': json_data.get('passport', nominee.passport),
			'relation': json_data.get('relation', nominee.relation),
			'contact_no': json_data.get('contact_no', nominee.contact_no),
			'phone': json_data.get('phone', nominee.phone),
			'cell': json_data.get('cell', nominee.cell),
			'email': json_data.get('email', nominee.email),
			'img': json_data.get('img', nominee.img)
		})

		return {
			'nominee_id': nominee.id,
			'name': nominee.name,
			'guardian': nominee.guardian,
			'cnic': nominee.cnic,
			'relation': nominee.relation,
			'phone': nominee.phone,
			'email': nominee.email,
			'message': 'Nominee updated successfully'
		}

	@http.route('/delete_nominee', type='json', auth='public', methods=['DELETE'])
	def delete_nominee(self, **kwargs):
		json_data = request.jsonrequest
		nominee_id = json_data.get('nominee_id')

		if not nominee_id:
			return {'error': 'Nominee ID is required'}

		nominee = request.env['nominee.info'].sudo().browse(nominee_id)
		
		if not nominee.exists():
			return {'error': 'Nominee not found'}

		nominee.sudo().unlink()

		return {
			'nominee_id': nominee_id,
			'message': 'Nominee deleted successfully'
		}

	@http.route('/create_nominee', type='json', auth='public', methods=['POST'])
	def create_nominee(self, **kwargs):
		json_data = request.jsonrequest
		parent_id = json_data.get('parent_id')

		if not parent_id:
			return {'error': 'Customer ID (parent_id) is required'}

		customer = request.env['res.partner'].sudo().browse(parent_id)
		if not customer.exists():
			return {'error': 'Customer not found'}

		# Create nominee and link it to the customer
		new_nominee = request.env['nominee.info'].sudo().create({
			'name': json_data.get('name') or "Default Name",  
			'guardian': json_data.get('guardian') or "Unknown",
			'cnic': json_data.get('cnic') or "00000-0000000-0",
			'passport': json_data.get('passport') or "N/A",
			'relation': json_data.get('relation') or "Other",
			'contact_no': json_data.get('contact_no') or "",
			'phone': json_data.get('phone') or "",
			'cell': json_data.get('cell') or "",
			'email': json_data.get('email') or "",
			'img': json_data.get('img') or False,
			'tree_link': customer.id  # ✅ Properly link nominee to customer
		})

		if not new_nominee:
			return {'error': 'Failed to create nominee'}

		_logger.info("Nominee Created: ID=%s, Name=%s, Parent=%s", new_nominee.id, new_nominee.name, new_nominee.tree_link)

		return {
			'nominee_id': new_nominee.id,
			'name': new_nominee.name,
			'guardian': new_nominee.guardian,
			'cnic': new_nominee.cnic,
			'relation': new_nominee.relation,
			'phone': new_nominee.phone,
			'email': new_nominee.email,
			'parent_id': parent_id,
			'message': 'Nominee created successfully and linked to the customer'
		}




	@http.route('/create_assets_class', type='json', auth='public', methods=['POST'])
	def create_assets_class(self):
		data = request.jsonrequest  
		name = data.get('name')
		status = data.get('status')
		class_id = data.get('class_id')

		if not name or not status:
			return {"error": "Both 'name' and 'status' are required"}

		valid_statuses = ['active', 'inactive']
		if status not in valid_statuses:
			return {"error": "Invalid status. Allowed values: 'active', 'inactive'"}

		new_record = request.env['assets.class'].sudo().create({
			'name': name,
			'status': status,
			'class_id' : class_id
		})

		return {
			"message": "Record created successfully",
			"class_id": class_id,
			"name": new_record.name,
			"status": new_record.status
		}


	@http.route('/update_assets_class', type='json', auth='public', methods=['POST'], csrf=False)
	def update_assets_class(self):
		data = request.jsonrequest

		class_id = data.get('class_id') 
		name = data.get('name') 
		status = data.get('status')  

		asset_class = request.env['assets.class'].sudo().search([('class_id', '=', class_id)], limit=1)

		if not asset_class:
			return {"error": "Asset class not found"}

		update_vals = {}
		if class_id:
			update_vals['class_id'] = class_id
		if name:
			update_vals['name'] = name
		if status:
			update_vals['status'] = status

		asset_class.sudo().write(update_vals)

		return {
			"message": "Record updated successfully",
			"class_id": class_id,
			"name": asset_class.name,
			"status": asset_class.status
		}

	@http.route('/delete_assets_class', type='json', auth='public', methods=['DELETE'])
	def delete_assets_class(self, **kwargs):
		record_id = kwargs.get('class_id')

		record = request.env['assets.class'].sudo().search([('class_id', '=', record_id)])

		record.sudo().unlink()
		return {"result": {"message": "Record deleted successfully"}}


	@http.route('/create_category_coding', type='json', auth='public', methods=['POST'], csrf=False)
	def create_category_coding(self, **kwargs):
		data = request.jsonrequest  
		category_name = data.get('name')  
		category_id = data.get('category_id')  
		status = data.get('status')
		asset_class_id = data.get('asset_class_id')  # use this instead of `desc`

		if not category_name or not status or not asset_class_id  or not category_id:
			return {"error": "Fields 'name', 'status', and 'asset_class_id'  and   'category_id'  are required"}

		valid_statuses = ['active', 'inactive']
		if status not in valid_statuses:
			return {"error": "Invalid status. Allowed values: 'active', 'inactive'"}

		assets_class = request.env['assets.class'].sudo().search([('id', '=', int(asset_class_id))], limit=1)
		if not assets_class:
			return {"error": "No assets.class found with ID {}".format(asset_class_id)}

		new_record = request.env['category.coding'].sudo().create({
			'name': category_name,
			'category_id' : category_id,
			'status': status,
			'asset_class_id': assets_class.id
		})

		return {
			"message": "Record created successfully",
			"category_id": category_id,
			"name": new_record.name,
			"status": new_record.status,
			"asset_class_id": new_record.asset_class_id.id
		}

	
	@http.route('/update_category_coding', type='json', auth='public', methods=['POST'], csrf=False)
	def update_category_coding(self, **kwargs):
		data = request.jsonrequest
		category_id = data.get('category_id')
		name = data.get('name') 
		asset_class_id = data.get('asset_class_id')
		status = data.get('status')

		if not category_id:
			return {"error": "Field 'category_id' is required to update record"}

		record = request.env['category.coding'].sudo().search([('category_id', '=', int(category_id))], limit=1)
		if not record:
			return {"error": "Record with ID {} not found".format(category_id)}

		update_vals = {}
		if name:
			update_vals['name'] = name
		if category_id:
			update_vals['category_id'] = category_id	
		if asset_class_id:
			update_vals['asset_class_id'] = int(asset_class_id)
		if status:
			if status not in ['active', 'inactive']:
				return {"error": "Invalid status. Allowed values: 'active', 'inactive'"}
			update_vals['status'] = status

		record.write(update_vals)

		return {"message": "Record updated successfully", "category_id": record.id}


	@http.route('/delete_category_coding', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_category_coding(self, **kwargs):
		record_id = kwargs.get('category_id')

		record = request.env['category.coding'].sudo().search([('category_id', '=', record_id)])

		record.sudo().unlink()
		return {"result": {"message": "Record deleted successfully"}}

	
	@http.route('/create_characteristics_coding', type='json', auth='public', methods=['POST'], csrf=False)
	def create_characteristics_coding(self, **kwargs):
		data = request.jsonrequest

		asset_class_id = data.get('asset_class_id')
		characteristics = data.get('characteristics')
		memo = data.get('memo')

		if not asset_class_id or not characteristics:
			return {'error': 'Missing required fields: asset_class_id or characteristics'}

		valid_types = ['int', 'text', 'file']
		for line in characteristics:
			if line.get('type') not in valid_types:
				return {'error': 'Invalid type value: %s. Allowed values: %s' % (line.get('type'), valid_types)}

		existing_record = request.env['characteristics.coding'].sudo().search([
			('name', '=', int(asset_class_id))
		], limit=1)
		if existing_record:
			return {'error': 'A characteristics.coding record with asset_class_id %s already exists' % asset_class_id}

		create_data = {
			'name': int(asset_class_id),
			'characteristic_ids': [(0, 0, {
				'name': line.get('name'),
				'type': line.get('type'),
				'length': line.get('length', 0)
			}) for line in characteristics]
		}

		if memo:
			create_data['memo'] = memo

		record = request.env['characteristics.coding'].sudo().create(create_data)

		return {
			'success': True,
			'id': record.id,
			'message': 'Characteristics coding for asset_class_id %s created successfully' % asset_class_id
		}


	@http.route('/update_characteristics_coding', type='json', auth='public', methods=['POST'], csrf=False)
	def update_characteristics_coding(self, **kwargs):
		data = request.jsonrequest

		asset_class_id = data.get('asset_class_id')
		characteristics = data.get('characteristics')
		memo = data.get('memo')

		if not asset_class_id or not characteristics:
			return {'error': 'Missing asset_class_id or characteristics'}

		record = request.env['characteristics.coding'].sudo().search([('name', '=', int(asset_class_id))], limit=1)
		if not record:
			return {'error': 'No characteristics.coding found with asset_class_id %s' % asset_class_id}

		valid_types = dict(request.env['characteristics.coding.lines']._fields['type'].selection).keys()
		for line in characteristics:
			if line.get('type') not in valid_types:
				return {'error': 'Invalid type value: %s. Allowed values: %s' % (line.get('type'), valid_types)}

		write_data = {
			'name': int(asset_class_id),
			'characteristic_ids': [(5, 0, 0)] + [
				(0, 0, {
					'name': line.get('name'),
					'type': line.get('type'),
					'length': line.get('length', 0)
				}) for line in characteristics
			]
		}

		if memo:
			write_data['memo'] = memo

		record.sudo().write(write_data)

		return {
			'success': True,
			'message': 'Characteristics coding for asset_class_id %s updated successfully' % asset_class_id
		}

	
	@http.route('/delete_characteristics_coding', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_characteristics_coding(self, **kwargs):
		data = request.jsonrequest
		asset_class_id = data.get('asset_class_id')

		if not asset_class_id:
			return {'error': 'asset_class_id is required'}

		record = request.env['characteristics.coding'].sudo().search([('name', '=', int(asset_class_id))], limit=1)
		if not record:
			return {'error': 'No characteristics.coding found with asset_class_id %s' % asset_class_id}

		record.sudo().unlink()

		return {
			'success': True,
			'message': 'Characteristics coding for asset_class_id %s deleted successfully' % asset_class_id
		}

		
	@http.route('/get_assets_class', type='json', auth='public')
	def get_assets_class(self):
		asset_classes = request.env['assets.class'].sudo().search([])

		result = []
		for ac in asset_classes:
			result.append({
				'class_id': class_id,
				'name': ac.name,
				'status': ac.status,
			})

		result = sorted(result, key=lambda r: r['name'])

		return {'asset_classes': result}

	@http.route('/get_category_coding', type='json', auth='public')
	def get_category_coding(self):
		category_coding = request.env['category.coding'].sudo().search([])
		result = []
		for cc in category_coding:
			result.append({
				'category_id':  category_id,
				'name': cc.name,
				'status': cc.status,
				'asset_class_id': cc.asset_class_id.name if cc.asset_class_id else False
			})

		result = sorted(result, key=lambda r: r['name'])

		return {'category_coding': result}


	@http.route('/get_characteristics_coding', type='json', auth='public', methods=['POST'], csrf=False)
	def get_characteristics_coding(self, **kwargs):
		records = request.env['characteristics.coding'].sudo().search([])

		result = []
		for rec in records:
			result.append({
				'id': rec.id,
				'asset_class_id': rec.name.id if rec.name else False,
				'asset_class_name': rec.name.name if rec.name else '',
				'characteristics': [
					{
						'id': line.id,
						'name': line.name,
						'type': line.type,
						'length': line.length,
					} for line in rec.characteristic_ids
				]
			})

		return {
			'success': True,
			'data': result
		}

	@http.route('/create_barter_recipt', type='json', auth='public', methods=['POST'], csrf=False)
	def create_barter_recipt(self, **vals):
		asset_characteristics = vals.pop('asset_characteristics', [])
		installment_lines = vals.pop('installments_lines', [])

		barter_recipt = request.env['barter.recipt'].sudo().create({
			'asset_class': vals.get('asset_class'),
			'category_coding': vals.get('category_coding'),
			'purchase_date': vals.get('purchase_date'),
			'customer_name': vals.get('customer_name'),
			'description_type': vals.get('description_type'),
			'description_rate': vals.get('description_rate'),
			'description_period': vals.get('description_period'),
			'residual_scrap_value': vals.get('residual_scrap_value'),
			'cost_replace': vals.get('cost_replace'),
			'dismantling_cost': vals.get('dismantling_cost'),
			'payment_type': vals.get('payment_type'),
			'barter_amount': vals.get('barter_amount'),
			'remaining_value': vals.get('remaining_value'),
			'bank_cash': vals.get('bank_cash'),
			'cheque_no': vals.get('cheque_no'),
			'assets_purchase': vals.get('assets_purchase'),
		})

		for line in asset_characteristics:
			request.env['barter.lines'].sudo().create({
				'barter_line_id': barter_recipt.id,
				'name': line.get('name'),     
				'value': line.get('value'),   
			})

		for line in installment_lines:
			request.env['installment.line'].sudo().create({
				'barter_recipt_id': barter_recipt.id,
				'installment_amount': line.get('installment_amount'),
				'installment_no': line.get('installment_no'),
				'project': line.get('project'),
				'unit_no': line.get('unit_no'),
				'ownership': line.get('ownership'),
				'amount': line.get('amount'),
			})

		return {
			'status': 'success',
			'record_id': barter_recipt.id,
			'message': 'Barter receipt created successfully with barter lines and installments.'
		}

	@http.route('/get_barter_recipt', type='json', auth='public', methods=['GET'], csrf=False)
	def get_barter_recipt(self, **kwargs):
		records = request.env['barter.recipt'].sudo().search([])
		result = []
		for record in records:
			result.append({
				'record_id': record.id,
				'asset_class': record.asset_class.id if record.asset_class else None,
				'category_coding': record.category_coding.id,
				'purchase_date': record.purchase_date,
				'customer_name': record.customer_name.id if record.customer_name else None,
				'description_type': record.description_type,
				'description_rate': record.description_rate,
				'description_period': record.description_period,
				'residual_scrap_value': record.residual_scrap_value,
				'cost_replace': record.cost_replace,
				'dismantling_cost': record.dismantling_cost,
				'payment_type': record.payment_type,
				'barter_amount': record.barter_amount,
				'remaining_value': record.remaining_value,
				'bank_cash': record.bank_cash,
				'cheque_no': record.cheque_no,
				'assets_purchase': record.assets_purchase,
				'asset_characteristics': [{
					'name': line.name,
					'value': line.value
				} for line in record.asset_characteristics],
				'installment_lines': [{
					'installment_amount': line.installment_amount,
					'installment_no': line.installment_no,
					'project': line.project.id,
					'unit_no': line.unit_no.id,
					'ownership': line.ownership,
					'amount': line.amount
				} for line in record.installments_lines],
			})

		return {
			'status': 'success',
			'total_records': len(result),
			'data': result
		}


	@http.route('/delete_barter_recipt', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_barter_recipt(self, **kwargs):
		json_data = request.jsonrequest
	
		barter_recipt_id = json_data.get('barter_recipt_id')
		record = request.env['barter.recipt'].sudo().browse(barter_recipt_id)

		record.sudo().unlink()
		return {
			'status': 'success',
			'message': 'Barter receipt deleted successfully'
		}	

	@http.route('/update_barter_recipt', type='json', auth='public', methods=['POST'], csrf=False)
	def update_barter_recipt(self, **kwargs):
		json_data = request.jsonrequest

		barter_recipt_id = json_data.get('barter_recipt_id')

		barter_recipt_id = int(barter_recipt_id)
		

		record = request.env['barter.recipt'].sudo().browse(barter_recipt_id)
		

		asset_characteristics = json_data.pop('asset_characteristics', [])
		installment_lines = json_data.pop('installments_lines', [])

		update_vals = {
			'asset_class': json_data.get('asset_class'),
			'category_coding': json_data.get('category_coding'),
			'purchase_date': json_data.get('purchase_date'),
			'customer_name': json_data.get('customer_name'),
			'description_type': json_data.get('description_type'),
			'description_rate': json_data.get('description_rate'),
			'description_period': json_data.get('description_period'),
			'residual_scrap_value': json_data.get('residual_scrap_value'),
			'cost_replace': json_data.get('cost_replace'),
			'dismantling_cost': json_data.get('dismantling_cost'),
			'payment_type': json_data.get('payment_type'),
			'barter_amount': json_data.get('barter_amount'),
			'remaining_value': json_data.get('remaining_value'),
			'bank_cash': json_data.get('bank_cash'),
			'cheque_no': json_data.get('cheque_no'),
			'assets_purchase': json_data.get('assets_purchase'),
		}

		update_vals = {k: v for k, v in update_vals.items() if v is not None}

		record.sudo().write(update_vals)

		record.asset_characteristics.unlink()
		for line in asset_characteristics:
			request.env['barter.lines'].sudo().create({
				'barter_line_id': record.id,
				'name': line.get('name'),
				'value': line.get('value'),
			})

		record.installments_lines.unlink()
		for line in installment_lines:
			request.env['installment.line'].sudo().create({
				'barter_recipt_id': record.id,
				'installment_amount': line.get('installment_amount'),
				'installment_no': line.get('installment_no'),
				'project': line.get('project'),
				'unit_no': line.get('unit_no'),
				'ownership': line.get('ownership'),
				'amount': line.get('amount'),
			})

		return {
			'status': 'success',
			'record_id': record.id,
			'message': 'Barter receipt updated successfully'
		}

 
	@http.route('/create_asset_purchase', type='json', auth='public', methods=['POST'], csrf=False)
	def create_asset_purchase(self, **kwargs):
	  
		json_data = request.jsonrequest

		asset_characteristics = json_data.pop('asset_characteristics', [])

		asset_purchase_vals = {
			'asset_class': json_data.get('asset_class'),
			'category_coding': json_data.get('category_coding'),
			'purchase_date': json_data.get('purchase_date'),
			'vendor_name': json_data.get('vendor_name'),
			'description_type': json_data.get('description_type'),
			'description_rate': json_data.get('description_rate'),
			'description_period': json_data.get('description_period'),
			'residual_scrap_value': json_data.get('residual_scrap_value'),
			'cost_replace': json_data.get('cost_replace'),
			'dismantling_cost': json_data.get('dismantling_cost'),
			'payment_type': json_data.get('payment_type'),
			'cheque_no': json_data.get('cheque_no'),
			'bank_cash': json_data.get('bank_cash'),
			'paid_amount': json_data.get('paid_amount'),
			'asset_period': json_data.get('asset_period'),
		}

		asset_purchase_vals = {k: v for k, v in asset_purchase_vals.items() if v is not None}

		asset_purchase_created = request.env['asset.purchase'].sudo().create(asset_purchase_vals)

		for line in asset_characteristics:
			request.env['purchase.lines'].sudo().create({
				'purchase_line_id': asset_purchase_created.id,
				'name': line.get('name'),    
				'value': line.get('value'),  
			})

		return {
			'success': True,
			'asset_purchase_id': asset_purchase_created.id,
			'message': 'Asset Purchase record created successfully.'
		}


	@http.route('/update_asset_purchase', type='json', auth='public', methods=['POST'], csrf=False)
	def update_asset_purchase(self, **kwargs):
		json_data = request.jsonrequest

		asset_purchase_id = json_data.get('asset_purchase_id')
		if not asset_purchase_id:
			return {
				'success': False,
				'message': 'Missing required field: asset_purchase_id'
			}
		asset_purchase = request.env['asset.purchase'].sudo().browse(asset_purchase_id)

		asset_characteristics = json_data.pop('asset_characteristics', [])

		update_vals = {
			'asset_class': json_data.get('asset_class'),
			'category_coding': json_data.get('category_coding'),
			'purchase_date': json_data.get('purchase_date'),
			'vendor_name': json_data.get('vendor_name'),
			'description_type': json_data.get('description_type'),
			'description_rate': json_data.get('description_rate'),
			'description_period': json_data.get('description_period'),
			'residual_scrap_value': json_data.get('residual_scrap_value'),
			'cost_replace': json_data.get('cost_replace'),
			'dismantling_cost': json_data.get('dismantling_cost'),
			'payment_type': json_data.get('payment_type'),
			'cheque_no': json_data.get('cheque_no'),
			'bank_cash': json_data.get('bank_cash'),
			'paid_amount': json_data.get('paid_amount'),
			'asset_period': json_data.get('asset_period'),
		}

		update_vals = {k: v for k, v in update_vals.items() if v is not None}

		asset_purchase.write(update_vals)

		asset_purchase.asset_characteristics.unlink()
		for line in asset_characteristics:
			request.env['purchase.lines'].sudo().create({
				'purchase_line_id': asset_purchase.id,
				'name': line.get('name'),
				'value': line.get('value'),
			})

		return {
			'success': True,
			'asset_purchase_id': asset_purchase.id,
			'message': 'Asset Purchase record updated successfully.'
		}

	@http.route('/get_asset_purchases', type='json', auth='public', methods=['GET'], csrf=False)
	def get_asset_purchases(self, **kwargs):
		records = request.env['asset.purchase'].sudo().search([])
		
		result = []
		for record in records:
			result.append({
				'asset_purchase_id': record.id,
				'asset_class': record.asset_class.id if record.asset_class else None,
				'category_coding': record.category_coding.id if record.category_coding else None,
				'purchase_date': record.purchase_date,
				'vendor_name': record.vendor_name.id if record.vendor_name else None,
				'description_type': record.description_type,
				'description_rate': record.description_rate,
				'residual_scrap_value': record.residual_scrap_value,
				'cost_replace': record.cost_replace,
				'dismantling_cost': record.dismantling_cost,
				'payment_type': record.payment_type,
				'cheque_no': record.cheque_no,
				'bank_cash': record.bank_cash,
				'paid_amount': record.paid_amount,
				'asset_period': record.asset_period,
				'asset_characteristics': [{
					'name': line.name,
					'value': line.value
				} for line in record.asset_characteristics],
			})

		return {
			'success': True,
			'total_records': len(result),
			'data': result
		}


	@http.route('/delete_asset_purchase', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_asset_purchase(self, **kwargs):
		asset_purchase_data = request.jsonrequest or {}
		record_id = asset_purchase_data.get('asset_purchase_id')

		record = request.env['asset.purchase'].sudo().search([('id', '=', record_id)])
		
		if not record:
			return {"result": {"message": "Record not found"}}

		record.sudo().unlink()
		return {"result": {"message": "Record deleted successfully"}}

# @http.route('/delete_asset_purchase', type='json', auth='public', methods=['DELETE'], csrf=False)
# def delete_asset_purchase(self, **kwargs):
#     json_data = request.jsonrequest or {}
#     record_id = json_data.get('asset_purchase_id')
	
#     if not record_id:
#         return {
#             'success': False,
#             'message': 'Missing required field: asset_purchase_id'
#         }
		
#     try:
#         record_id = int(record_id)
#     except (ValueError, TypeError):
#         return {
#             'success': False,
#             'message': 'Invalid ID format: must be an integer'
#         }

#     record = request.env['asset.purchase'].sudo().browse(record_id)
	
#     # Check if record exists
#     if not record.exists():
#         return {
#             'success': False,
#             'message': f'Record with ID {record_id} not found'
#         }

#     record.unlink()
	
#     return {
#         'success': True,
#         'message': 'Record deleted successfully'
#     }
		
   


	@http.route('/create_asset_insurance', type='json', auth='public', methods=['POST'], csrf=False)
	def create_asset_insurance(self, **kwargs):
		insurance_model = request.env['asset.insurance']
		json_data = request.jsonrequest

		asset_class = json_data.get('asset_class')
		insurance_date = json_data.get('insurance_date')
		insurance_company = json_data.get('insurance_company')
		insurance_value = json_data.get('insurance_value')
		insurance_start_date = json_data.get('insurance_start_date')
		insurance_end_date = json_data.get('insurance_end_date')

		insurance_vals = {
			'asset_class': asset_class,
			'insurance_date': insurance_date,
			'insurance_company': insurance_company,
			'insurance_value': insurance_value,
			'insurance_start_date': insurance_start_date,
			'insurance_end_date': insurance_end_date,
		}

		insurance_record = insurance_model.sudo().create(insurance_vals)

		return {
			'success': True,
			'id': insurance_record.id,
			'asset_class': asset_class,

			'message': 'Asset Insurance record created successfully.',
		}

	@http.route('/update_asset_insurance', type='json', auth='public', methods=['POST'], csrf=False)
	def update_asset_insurance(self, **kwargs):
		json_data = request.jsonrequest

		insurance_id = json_data.get('insurance_id')
		
		record = request.env['asset.insurance'].sudo().browse(insurance_id)

		update_vals = {}

		asset_class = json_data.get('asset_class')
		insurance_date = json_data.get('insurance_date')
		insurance_company = json_data.get('insurance_company')
		insurance_value = json_data.get('insurance_value')
		insurance_start_date = json_data.get('insurance_start_date')
		insurance_end_date = json_data.get('insurance_end_date')

		if asset_class is not None:
			update_vals['asset_class'] = asset_class

		if insurance_date is not None:
			update_vals['insurance_date'] = insurance_date

		if insurance_company is not None:
			update_vals['insurance_company'] = insurance_company

		if insurance_value is not None:
			update_vals['insurance_value'] = insurance_value

		if insurance_start_date is not None:
			update_vals['insurance_start_date'] = insurance_start_date

		if insurance_end_date is not None:
			update_vals['insurance_end_date'] = insurance_end_date

		record.write(update_vals)

		return {
			'success': True,
			'insurance_id': record.id,
			'asset_class_id': record.asset_class.id,
			'insurance_company_id': record.insurance_company.id,
			'message': 'Asset Insurance record updated successfully.'
		}

	@http.route('/get_asset_insurance', type='json', auth='public', methods=['GET'], csrf=False)
	def get_asset_insurance(self):
		records = request.env['asset.insurance'].sudo().search([])

		result = []
		for record in records:
			result.append({
				'id': record.id,
				'asset_class': {
					'id': record.asset_class.id,
					'name': record.asset_class.name
				} if record.asset_class else None,
				'insurance_company': {
					'id': record.insurance_company.id,
					'name': record.insurance_company.name
				} if record.insurance_company else None,
				'insurance_date': record.insurance_date,
				'insurance_value': record.insurance_value,
				'insurance_start_date': record.insurance_start_date,
				'insurance_end_date': record.insurance_end_date,
			})

		return {
			'status': 'success',
			'total_records': len(result),
			'data': result
		}

	@http.route('/delete_asset_insurance', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_asset_insurance(self, **kwargs):
		json_data = request.jsonrequest
		insurance_id = json_data.get('insurance_id')

		record = request.env['asset.insurance'].sudo().browse(insurance_id)

		if not record.exists():
			return {
				'status': 'error',
				'message': 'Record with provided ID  does not exist.'
			}

		record.unlink()

		return {
			'status': 'success',
			'message': 'Asset Insurance record deleted successfully.'
		}


	@http.route('/create_asset_issuance', type='json', auth='public', methods=['POST'], csrf=False)
	def create_asset_issuance(self, **kwargs):
		json_data = request.jsonrequest

		asset_class = json_data.get('asset_class')
		issuance_date = json_data.get('issuance_date')
		issued_to_project = json_data.get('issued_to_project') 
		project = json_data.get('project')
		project_location = json_data.get('project_location')

		issuance_vals = {
			'asset_class': asset_class,
			'issuance_date': issuance_date,
			'issued_to_project': issued_to_project,
			'project': project,
			'project_location': project_location,
		}

		issuance_record = request.env['asset.issuance'].sudo().create(issuance_vals)

		return {
			'success': True,
			'issuance_id': issuance_record.id,
			'message': 'Asset Issuance record created successfully.',
		}	


	@http.route('/update_asset_issuance', type='json', auth='public', methods=['POST'], csrf=False)
	def update_asset_issuance(self, **kwargs):
		json_data = request.jsonrequest

		issuance_id = json_data.get('issuance_id')
		record = request.env['asset.issuance'].sudo().browse(issuance_id)

		if not record.exists():
			return {
				'success': False,
				'message': 'Record with Provided ID  does not exist.'
			}

		update_vals = {}

		asset_class = json_data.get('asset_class')
		issuance_date = json_data.get('issuance_date')
		issued_to_project = json_data.get('issued_to_project')  
		project = json_data.get('project')
		project_location = json_data.get('project_location')

		# Build update_vals conditionally
		if asset_class is not None:
			update_vals['asset_class'] = asset_class

		if issuance_date is not None:
			update_vals['issuance_date'] = issuance_date

		if issued_to_project in ['yes', 'no']:
			update_vals['issued_to_project'] = issued_to_project

		if project is not None:
			update_vals['project'] = project

		if project_location is not None:
			update_vals['project_location'] = project_location

		record.write(update_vals)

		return {
			'success': True,
			'issuance_id': record.id,
			'asset_class_id': record.asset_class.id,
			'project_id': record.project.id,
			'project_location_id': record.project_location.id,
			'issued_to_project': record.issued_to_project,
			'message': 'Asset Issuance record updated successfully.'
		}	


	@http.route('/get_asset_issuance', type='json', auth='public', methods=['GET'], csrf=False)
	def get_asset_issuance(self, **kwargs):
		records = request.env['asset.issuance'].sudo().search([])

		result = []
		for record in records:
			result.append({
				'issuance_id': record.id,
				'asset_class': {
					'id': record.asset_class.id,
					'name': record.asset_class.name
				} if record.asset_class else None,
				'issuance_date': record.issuance_date,
				'issued_to_project': {
					'value': record.issued_to_project,
					'label': dict(record._fields['issued_to_project'].selection).get(record.issued_to_project)
				},
				'project': {
					'id': record.project.id,
					'name': record.project.name
				} if record.project else None,
				'project_location': {
					'id': record.project_location.id,
					'name': record.project_location.name
				} if record.project_location else None,
			})

		return {
			'status': 'success',
			'total_records': len(result),
			'data': result
		}	


	@http.route('/delete_asset_issuance', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_asset_issuance(self, **kwargs):
		json_data = request.jsonrequest

		issuance_id = json_data.get('issuance_id')

		record = request.env['asset.issuance'].sudo().browse(issuance_id)

		if not record.exists():
			return {
				'success': False,
				'message': 'Record with this ID  does not exist.'
			}

		record.unlink()

		return {
			'success': True,
			'deleted_id': issuance_id,
			'message': 'Asset Issuance record deleted successfully.'
		}	


	@http.route('/create_asset_transfer', type='json', auth='public', methods=['POST'], csrf=False)
	def create_asset_transfer(self, **kwargs):
		
		transfer_model = request.env['asset.transfer']
		json_data = request.jsonrequest

		asset_class = json_data.get('asset_class')
		transfer_date = json_data.get('transfer_date')
		from_user = json_data.get('from_user')
		to_user = json_data.get('to_user')
		project = json_data.get('project')
		project_location = json_data.get('project_location')

		transfer_vals = {
			'asset_class': asset_class,
			'transfer_date': transfer_date,
			'from_user': from_user,
			'to_user': to_user,
			'project': project,
			'project_location': project_location,
		}

		transfer_record = transfer_model.sudo().create(transfer_vals)

		return {
			'success': True,
			'id': transfer_record.id,
			'asset_class': asset_class,
			'message': 'Asset Transfer record created successfully.',
		}		

	@http.route('/update_asset_transfer', type='json', auth='public', methods=['POST'], csrf=False)
	def update_asset_transfer(self, record_id, **kwargs):
		transfer_model = request.env['asset.transfer']
		record = transfer_model.sudo().browse(record_id)

		json_data = request.jsonrequest

		asset_class = json_data.get('asset_class')
		transfer_date = json_data.get('transfer_date')
		from_user = json_data.get('from_user')
		to_user = json_data.get('to_user')
		project = json_data.get('project')
		project_location = json_data.get('project_location')

		transfer_vals = {
			'asset_class': asset_class,
			'transfer_date': transfer_date,
			'from_user': from_user,
			'to_user': to_user,
			'project': project,
			'project_location': project_location,
		}

		record.sudo().write(transfer_vals)

		return {
			'success': True,
			'id': record.id,
			'asset_class': asset_class,
			'message': 'Asset Transfer record updated successfully.',
		}	


	@http.route('/update_asset_transfer', type='json', auth='public', methods=['POST'], csrf=False)
	def update_asset_transfer(self, **kwargs):
		transfer_model = request.env['asset.transfer']
		json_data = request.jsonrequest

		transfer_id = json_data.get('transfer_id')
		if not transfer_id:
			return {
				'success': False,
				'message': 'Missing required field: transfer_id'
			}

		record = transfer_model.sudo().browse(transfer_id)
		if not record.exists():
			return {
				'success': False,
				'message': 'Record with provided ID  not found.'
			}

		update_vals = {}

		asset_class = json_data.get('asset_class')
		transfer_date = json_data.get('transfer_date')
		from_user = json_data.get('from_user')
		to_user = json_data.get('to_user')
		project = json_data.get('project')
		project_location = json_data.get('project_location')

		if asset_class is not None:
			update_vals['asset_class'] = asset_class

		if transfer_date is not None:
			update_vals['transfer_date'] = transfer_date

		if from_user is not None:
			update_vals['from_user'] = from_user

		if to_user is not None:
			update_vals['to_user'] = to_user

		if project is not None:
			update_vals['project'] = project

		if project_location is not None:
			update_vals['project_location'] = project_location

		record.sudo().write(update_vals)

		return {
			'success': True,
			'transfer_id': record.id,
			'message': 'Asset Transfer record updated successfully.',
		}	


	@http.route('/get_asset_transfer', type='json', auth='public', methods=['GET'], csrf=False)
	def get_asset_transfer(self, **kwargs):
		records = request.env['asset.transfer'].sudo().search([])
		result = []
		for record in records:
			result.append({
				'transfer_id': record.id,
				'asset_class': {
					'id': record.asset_class.id,
					'name': record.asset_class.name
				} if record.asset_class else None,
				'transfer_date': record.transfer_date,
				'from_user': {
					'id': record.from_user.id,
					'name': record.from_user.name
				} if record.from_user else None,
				'to_user': {
					'id': record.to_user.id,
					'name': record.to_user.name
				} if record.to_user else None,
				'project': {
					'id': record.project.id,
					'name': record.project.name
				} if record.project else None,
				'project_location': {
					'id': record.project_location.id,
					'name': record.project_location.name
				} if record.project_location else None,
			})

		return {
			'status': 'success',
			'total_records': len(result),
			'data': result
		}


	@http.route('/delete_asset_transfer', type='json', auth='public', methods=['DELETE'], csrf=False)
	def delete_asset_transfer(self, **kwargs):
		json_data = request.jsonrequest

		transfer_id = json_data.get('transfer_id')

		record = request.env['asset.transfer'].sudo().browse(transfer_id)

		# if not record.exists():
		# 	return {
		# 		'success': False,
		# 		'message': 'Record with provided ID  does not exist.'
		# 	}

		record.unlink()

		return {
			'success': True,
			'deleted_id': transfer_id,
			'message': 'Asset Transfer record deleted successfully.'
		}	



	@http.route('/get_project_info', type='json', auth='public')
	def get_project_info(self, **kwargs):
		json_data = request.jsonrequest
		
		project_id = json_data.get('project_id')
		
		projects = request.env['alif.project'].sudo().search([('id', '=', project_id)])
		project_data = []
		for project in projects:
			project_data.append({
				'name': project.name,
				'create_date': project.create_date,
				'project_id': project.id,
				'create_date': project.create_date,
				'land_securing_date': project.date,
				'block': project.block,
				'first_sale_date': project.first_sale_date,
				'first_payment_date': project.first_payment_date,
				'sector' : project.sector,
				'city' : project.city,
				'phone' : project.phone,
				'scheme_name' :project.address,
				'mobile' : project.mobile,
				'deliver_to' : project.ecube_delivery.name,
				'credit' : project.account_credit.name,
				'issue_to' : project.issue_to_production.name,
				'scrap_location': project.scrap_location.name,
				'project_location': project.project_location.name,
			})
		project_data = sorted(project_data, key=lambda r: r['name'])
		return project_data


	@http.route('/project_details', type='json', auth='public')
	def get_project_details(self):
		projects = request.env['alif.project'].sudo().search([])
		projects_list = []
		for project in projects:
			projects_list.append({
				'create_date': project.create_date,
				'project_id': project.id,
				'name': project.name,
				'create_date': project.create_date,
				'location_id': project.project_location.id,
				'location_name': project.project_location.name,
			})

		projects_list = sorted(projects_list, key=lambda r: r['name'])
		return projects_list

	@http.route('/create_project', type='json', auth='public', methods=['POST'], csrf=False)
	def create_project(self):
		data = request.jsonrequest
		name = data.get('name')
		location_id = data.get('location_id')
		project_vals = {
			'name': name,
			'project_location': location_id,  
			'phone': data.get('phone'),
			'mobile': data.get('mobile'),
			'sector': data.get('sector'),
			'create_date': data.get('create_date'),
			'land_securing_date': data.get('land_securing_date'),
			'block': data.get('block'),
			'first_sale_date': data.get('first_sale_date'),
			'first_payment_date': data.get('first_payment_date'),
			'city': data.get('city'),
			'scheme_name': data.get('scheme_name'),
			'deliver_to': data.get('deliver_to'),
			'credit': data.get('credit'),
			'issue_to': data.get('issue_to'),
			'scrap_location': data.get('scrap_location'),
			'project_location': data.get('project_location'),
			
		}
		project_vals = {k: v for k, v in project_vals.items() if v is not None}
		project = request.env['alif.project'].sudo().create(project_vals)
		return {
			'status': 'success',
			'message': 'Project created successfully.',
			'project_id': project.id,
			'name': project.name
		}


	@http.route('/update_project', type='json', auth='public', methods=['POST'], csrf=False)
	def update_project(self):
		data = request.jsonrequest
		project_id = data.get('project_id')
		
		project = request.env['alif.project'].sudo().search([('id', '=', project_id)], limit=1)
		
		update_vals = {
			'name': data.get('name'),
			'phone': data.get('phone'),
			'mobile': data.get('mobile'),
			'sector': data.get('sector'),
			'create_date': data.get('create_date'),
			'land_securing_date': data.get('land_securing_date'),
			'block': data.get('block'),
			'first_sale_date': data.get('first_sale_date'),
			'first_payment_date': data.get('first_payment_date'),
			'city': data.get('city'),
			'scheme_name': data.get('scheme_name'),
			'deliver_to': data.get('deliver_to'),
			'credit': data.get('credit'),
			'issue_to': data.get('issue_to'),
			'scrap_location': data.get('scrap_location'),
			'project_location': data.get('project_location'),
		}
		update_vals = {k: v for k, v in update_vals.items() if v is not None}
		project.write(update_vals)
		return {
			'status': 'success',
			'message': 'Project updated successfully.',
			'project_id': project.id,
			'updated_fields': list(update_vals.keys())
		}