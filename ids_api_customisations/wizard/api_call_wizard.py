from odoo import models, fields
import requests


class ApiCallWizard(models.TransientModel):
    _name = 'api.call.wizard'

    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    is_warehouse = fields.Boolean(string='Warehouse')
    product_temp_ids = fields.Many2many('product.template', string='Products')
    is_product = fields.Boolean(string='Product')
    brand_ids = fields.Many2many('product.brand', string='Brands')
    is_brand = fields.Boolean(string='Brand')
    category_ids = fields.Many2many('product.category', string='Categories')
    is_category = fields.Boolean(string='Category')
    sub_category_ids = fields.Many2many('product.tag', string='Sub Categories')
    is_sub_category = fields.Boolean(string='Sub Category')
    segment_ids = fields.Many2many('product.segment', string='Sub Segments')
    is_segment = fields.Boolean(string='Segment')
    is_vendor = fields.Boolean(string="Vendor")
    vendor_ids = fields.Many2many('res.partner',string="Vendors")

    def update_to_app_warehouse(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/warehouse.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }
        warehouses = []
        if self.warehouse_ids:
            for warehouse in self.warehouse_ids:
                warehouse_details = {
                    'id': warehouse.id,
                    'name': warehouse.name
                }
                warehouses.append(warehouse_details)
        payload = {
            "datas": warehouses

        }
        response = requests.post(url, json=payload, headers=headers)

    def update_to_app_product(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/product.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }

        products = []
        if self.product_temp_ids:
            for pro_temp in self.product_temp_ids:
                products.append(pro_temp)
        elif self.product_ids:
            for pro in self.product_ids:
                products.append(pro)
        else:
            pass

        data_list = []
        if products:
            for rec in products:
                segment = []
                if rec.segment_ids:
                    for seg in rec.segment_ids:
                        segment.append(seg.id)

                sub_category = []
                if rec.product_tag_ids:
                    for sub_cat in rec.product_tag_ids:
                        sub_category.append(sub_cat.id)

                similar_products = []
                if rec.optional_product_ids:
                    for opt_pro in rec.optional_product_ids:
                        similar_products.append(opt_pro.id)
                seller_data = []
                if rec.seller_ids:
                    for seller in rec.seller_ids:
                        seller_dict = {}
                        seller_dict.update({
                            'vendor_id':seller.partner_id.id,
                            'vendor_name':seller.partner_id.name,
                            'price':seller.price
                        })
                        seller_data.append(seller_dict)


                product_ids = self.env['product.product'].sudo().search(
                    [('product_tmpl_id', '=', rec.id)])
                product_datas = []
                for product in product_ids:
                    images = []
                    if product.product_image_ids:
                        for img in product.product_image_ids:
                            datas_related_values = img.sudo()._get_datas_related_values(img.datas, img.mimetype)
                            dir = self.env['ir.attachment']._full_path(datas_related_values['store_fname'])
                            with open(dir, "rb") as image_file:
                                data = image_file.read()
                                decode = data.decode("utf-8")
                                images.append(decode)

                    variants = []
                    for val in product.product_template_attribute_value_ids:
                        vals = {
                            val.attribute_id.name: val.product_attribute_value_id.name,
                            val.attribute_id.arabic_name: val.product_attribute_value_id.arabic_name
                        }
                        variants.append(vals)
                    quantity_details = {}
                    for stock in product.stock_quant_ids:
                        warehouse_id = stock.location_id.warehouse_id.id
                        if warehouse_id not in quantity_details:
                            quantity_details[warehouse_id] = {
                                'warehouse_id': warehouse_id,
                                'warehouse_name': stock.location_id.warehouse_id.name,
                                'qty_available': stock.quantity
                            }
                        else:
                            quantity_details[warehouse_id]['qty_available'] += stock.quantity
                    quantity_details_list = list(quantity_details.values())
                    product_details = {
                        "id": product.id,
                        "name": product.name,
                        "show_list": 1 if product.show_list else 0,
                        "status": 1,
                        "images": images,
                        "values": variants,
                        "quantity_details": quantity_details_list

                    }
                    product_datas.append(product_details)
                datas = {
                    "id": rec.id,
                    "product_sku": rec.default_code if rec.default_code else False,
                    "product_name": rec.name,
                    "arabic_product_name": rec.arabic_name,
                    "similar_product": similar_products,
                    "Segment": segment,
                    "category_id": rec.categ_id.id if rec.categ_id else False,
                    "subcategory_id": sub_category,
                    "brand_id": rec.brand_id.id if rec.brand_id else False,
                    "description": rec.description_sale if rec.description_sale else False,
                    "arabic_description": rec.arabic_description if rec.arabic_description else False,
                    "show_list": 1 if rec.show_list else 0,
                    "variants": product_datas,
                    "vendor_data":seller_data
                }
                data_list.append(datas)

        payload = {
            "datas": data_list

        }
        response = requests.post(url, json=payload, headers=headers)

    def update_to_app_brand(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/updateBrand.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }

        brands = []
        if self.brand_ids:
            for brand in self.brand_ids:
                segments = []
                if brand.segment_ids:
                    for segment in brand.segment_ids:
                        segments.append(segment.id)
                vals = {
                    'id': brand.id,
                    'name': brand.name if brand.name else False,
                    'ar_name': brand.arabic_name if brand.arabic_name else False,
                    'segments': segments,
                    'position': brand.position if brand.position else False,
                    'status': brand.status if brand.status else False,
                    'image': brand.web_image.decode()  if brand.web_image else False
                 }
                brands.append(vals)

        payload = {
            "datas": brands

        }
        response = requests.put(url, json=payload, headers=headers)

    def update_to_app_sub_category(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/updateSubcategory.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }

        sub_categories = []
        if self.sub_category_ids:
            for sub_categ in self.sub_category_ids:
                vals = {
                    'id': sub_categ.id,
                    'name': sub_categ.name if sub_categ.name else False,
                    'ar_name': sub_categ.arabic_name if sub_categ.arabic_name else False,
                    'category_id': sub_categ.category_id.id if sub_categ.category_id else False,
                    'position': sub_categ.position if sub_categ.position else False,
                    'status': sub_categ.status if sub_categ.status else False,
                    'image': sub_categ.web_image.decode()  if sub_categ.web_image else False
                }
                sub_categories.append(vals)

        payload = {
            "datas": sub_categories
        }
        response = requests.put(url, json=payload, headers=headers)

    def update_to_app_category(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/updateCategory.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }

        categories = []
        if self.category_ids:
            for categ in self.category_ids:
                vals = {
                    'id': categ.id,
                    'name': categ.name if categ.name else False,
                    'ar_name': categ.arabic_name if categ.arabic_name else False,
                    'position': categ.position if categ.position else False,
                    'status': categ.status if categ.status else False,
                    'image': categ.web_image.decode() if categ.web_image else False
                }
                categories.append(vals)

        payload = {
            "datas": categories
        }
        response = requests.put(url, json=payload, headers=headers)

    def update_to_app_segment(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/updateSegment.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }

        segments = []
        if self.segment_ids:
            for seg in self.segment_ids:
                vals = {
                    'id': seg.id,
                    'name': seg.name if seg.name else False,
                    'ar_name': seg.arabic_name if seg.arabic_name else False,
                    'position': seg.position if seg.position else False,
                    'status': seg.status if seg.status else False,
                    'image': seg.web_image.decode() if seg.web_image else False
                }
                segments.append(vals)

        payload = {
            "datas": segments
        }
        response = requests.post(url, json=payload, headers=headers)

    def update_to_app_vendor(self):
        """Updates datas to api"""

        url = 'https://supplyplus.app/odoo/api/vendor.php'

        headers = {
            'Authorization': 'Bearer wgefiesrykgfowerlisu',
            'Content-Type': 'application/json'
        }

        vendors = []
        banks = []
        if self.vendor_ids:
            for vendor in self.vendor_ids:
                bank_dict = {}
                if vendor.bank_ids:
                    for bank in vendor.bank_ids:
                        bank_dict.update({
                            'account_holder_name':bank.acc_holder_name,
                            'bank_name':bank.bank_id.name,
                            'iban':bank.bank_id.bic,
                            'branch':bank.bank_id.street
                        })
                        banks.append(bank_dict)
                vendor_name = vendor.name.split(' ')
                first_name = ''
                last_name = ''
                if len(vendor_name) > 1:
                    first_name = vendor_name[0]
                    last_name = vendor_name[1]
                else:
                    first_name = vendor.name
                    last_name = vendor.name
                vals = {
                    'id': vendor.id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email':vendor.email or False,
                    'mobile_number':vendor.mobile or vendor.phone,
                    "vat_number":vendor.vat or False,
                    'address': vendor.street or False,
                    'profile_image': vendor.image_1920.decode() if vendor.image_1920 else False,
                    'bank':banks
                }
                vendors.append(vals)

        payload = {
            "datas": vendors
        }
        response = requests.post(url, json=payload, headers=headers)
