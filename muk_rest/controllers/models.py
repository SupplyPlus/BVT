###################################################################################
#
#    Copyright (c) 2017-today MuK IT GmbH.
#
#    This file is part of MuK REST for Odoo
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################

import werkzeug
import json
from odoo import http
from odoo.http import request
from odoo.models import check_method_name
from odoo.tools import misc, osutil
from odoo.http import request, Response
from odoo.addons.muk_rest import tools, core
from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.web.controllers.export import CSVExport, ExcelExport
import base64
from odoo.addons.muk_rest.tools.encoder import ResponseEncoder
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class ModelController(http.Controller):

    #----------------------------------------------------------
    # Components
    #----------------------------------------------------------

    @property
    def API_DOCS_COMPONENTS(self):
        return {
            'schemas': {
                'ReadGroupResult': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            '__domain': {
                                '$ref': '#/components/schemas/Domain',
                            }
                        },
                        'additionalProperties': True,
                    },
                    'description': 'A list of grouped record information.'
                },
                'DataFields': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'description': (
                        'A list of field names. The field names can be separated '
                        'with a "/" to access fields of a linked model.'
                    )
                },
                'ExportData': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                    },
                    'description': 'A list of the exported data.'
                },
                'ExtractData': {
                    'type': 'object',
                    'description': 'A map of field names and their corresponding values.'
                },
                'MultiWriteValues': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {
                            'anyOf': [
                                {'$ref': '#/components/schemas/RecordIDs'},
                                {'$ref': '#/components/schemas/RecordValues'},
                            ]
                        },
                        'minItems': 2,
                        'maxItems': 2,
                    },
                    'description': 'A list write commands.'
                }
            }
        }

    #----------------------------------------------------------
    # Generic Method
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route([
            '/call',
            '/call/<string:model>',
            '/call/<string:model>/<string:method>',
        ]),
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Call',
            description='Generic method call.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                },
                'method': {
                    'name': 'method',
                    'description': 'Method',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [],
                },
                'args': {
                    'name': 'args',
                    'description': 'Positional Arguments',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {}
                            },
                        },
                    },
                    'example': [],
                },
                'kwargs': {
                    'name': 'kwargs',
                    'description': 'Keyword Arguments',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object'
                            },
                        },
                    },
                    'example': {},
                },
            },
            default_responses=['200', '400', '401', '500'],
        ),
    )
    def call(self, model, method, ids=None, args=None, kwargs=None, **kw):
        check_method_name(method)
        args = tools.common.parse_value(args, [])
        kwargs = tools.common.parse_value(kwargs, {})
        records = request.env[model].browse(
            tools.common.parse_ids(ids)
        )
        return request.make_json_response(
            getattr(records, method)(*args, **kwargs)
        )

    #----------------------------------------------------------
    # Search / Read
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route([
            '/search',
            '/search/<string:model>',
            '/search/<string:model>/<string:order>',
            '/search/<string:model>/<int:limit>/<string:order>',
            '/search/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Search',
            description='Search for matching records',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'count': {
                    'name': 'count',
                    'description': 'Count',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def search(
        self,
        model,
        domain=None,
        count=False,
        limit=None,
        offset=0,
        order=None,
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        count = count and misc.str2bool(count) or None
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        model = request.env[model].with_context(prefetch_fields=False)
        result = model.search(domain, offset=offset, limit=limit, order=order, count=count)
        if not count:
            return request.make_json_response(result.ids)
        return request.make_json_response(result)

    @core.http.rest_route(
        routes=build_route([
            '/name',
            '/name/<string:model>',
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Names',
            description='Get the record names.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
                },
            },
            responses={
                '200': {
                    'description': 'List of ID and Name Tupels',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordTuples'
                            },
                            'example': [[1, 'YourCompany']]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def name(self, model, ids, **kw):
        return request.make_json_response(
            request.env[model].browse(
                tools.common.parse_ids(ids)
            ).name_get()
        )

    @core.http.rest_route(
        routes=build_route([
            '/read',
            '/read/<string:model>',
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Read',
            description='Read the given records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordFields',
                            },
                        }
                    },
                    'example': ['name'],
                },
            },
            responses={
                '200': {
                    'description': 'List of ID and name tupels',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordData'
                            },
                            'example': [{
                                'active': True,
                                'id': 14,
                                'name': 'Azure Interior'
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def read(self, model, ids, fields=None, **kw):
        return request.make_json_response(
            request.env[model].browse(
                tools.common.parse_ids(ids)
            ).read(
                tools.common.parse_value(fields)
            )
        )

    @core.http.rest_route(
        routes=build_route([
            '/search_read',
            '/search_read/<string:model>',
            '/search_read/<string:model>/<string:order>',
            '/search_read/<string:model>/<int:limit>/<string:order>',
            '/search_read/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Search Read',
            description='Search for matching records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordFields',
                            },
                        }
                    },
                    'example': ['name'],
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Records',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordData'
                            },
                            'example': [{
                                'active': True,
                                'id': 14,
                                'name': 'Azure Interior'
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def search_read(
        self,
        model,
        domain=None,
        fields=None,
        limit=None,
        offset=0,
        order=None,
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        fields = tools.common.parse_value(fields)
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        return request.make_json_response(request.env[model].search_read(
            domain, fields=fields, offset=offset, limit=limit, order=order
        ))

    @core.http.rest_route(
        routes=build_route([
            '/read_group',
            '/read_group/<string:model>',
            '/read_group/<string:model>/<string:orderby>',
            '/read_group/<string:model>/<int:limit>/<string:orderby>',
            '/read_group/<string:model>/<int:limit>/<int:offset>/<string:orderby>'
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Read Group',
            description='Search for matching records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'domain': {
                    'name': 'domain',
                    'required': True,
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordFields',
                            },
                        }
                    },
                    'example': ['name', 'parent_id'],
                },
                'groupby': {
                    'name': 'groupby',
                    'description': 'GroupBy',
                    'required': True,
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        }
                    },
                    'example': ['parent_id'],
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'orderby': {
                    'name': 'orderby',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
                'lazy': {
                    'name': 'lazy',
                    'description': 'Lazy Loading',
                    'schema': {
                        'type': 'boolean'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Records',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ReadGroupResult',
                            },
                            'example': [{
                                '__domain': [
                                    '&', ['parent_id', '=', False],
                                    '|', ['is_company', '=', True],
                                    ['parent_id', '=', False]
                                ],
                                'parent_id': False,
                                'parent_id_count': 12
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def read_group(
        self,
        model,
        domain,
        fields,
        groupby,
        offset=0,
        limit=None,
        orderby=False,
        lazy=True,
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        fields = tools.common.parse_value(fields)
        groupby = tools.common.parse_value(groupby, [])
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        lazy = misc.str2bool(lazy)
        return request.make_json_response(request.env[model].read_group(
            domain, fields, groupby=groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy
        ))

    @core.http.rest_route(
        routes=build_route([
            '/export',
            '/export/<string:model>',
            '/export/<string:model>/<string:type>',
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Export',
            description='Export the given records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 3],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/DataFields',
                            },
                        }
                    },
                    'example': ['name', 'bank_ids/acc_number'],
                },
                'type': {
                    'name': 'type',
                    'description': 'Return the Response as a CSV, Excel or Array',
                    'schema': {
                        'type': 'string',
                        'enum': ['csv', 'xlsx', 'array'],
                    },
                    'example': 'array',
                },
            },
            responses={
                '200': {
                    'description': 'Export Data',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ExportData'
                            },
                            'example': [
                                ['YourCompany', ''],
                                ['Mitchell Admin', ''],
                            ],
                        },
                        'application/octet-stream': {
                            'schema': {
                                'type': 'string',
                                'format': 'binary'
                            }
                        }

                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def export(self, model, ids, fields=None, type='array', **kw):
        records = request.env[model].browse(
            tools.common.parse_ids(ids)
        )
        field_names = tools.common.parse_value(fields)
        data  = records.export_data(field_names).get('datas', [])
        if type in ('csv', 'xlsx'):
            exporter = CSVExport() if type == 'csv' else ExcelExport()
            disposition = http.content_disposition(
                osutil.clean_filename(f'{records._table}{exporter.extension}')
            )
            content = exporter.from_data(field_names, data)
            return request.make_response(
                content,
                headers=[
                    ('Content-Length', len(content)),
                    ('Content-Type', exporter.content_type),
                    ('Content-Disposition', disposition),
                ],
            )
        return request.make_json_response(data)

    @core.http.rest_route(
        routes=build_route([
            '/extract',
            '/extract/<string:model>',
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Extract',
            description='Extract the given records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/DataFields',
                            },
                        }
                    },
                    'example': ['name', 'bank_ids/acc_number'],
                },
                'metadata': {
                    'name': 'metadata',
                    'description': 'Show Metadata',
                    'schema': {
                        'type': 'boolean'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Extract Data',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ExtractData'
                            },
                            'example': [
                              {'bank_ids': [], 'id': 1, 'name': 'YourCompany'},
                              {'bank_ids': [], 'id': 2, 'name': 'OdooBot'}
                            ],
                        },

                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def extract(self, model, ids, fields=None, metadata=False, **kw):
        records = request.env[model].browse(
            tools.common.parse_ids(ids)
        )
        return request.make_json_response(
            records.rest_extract_data(
                tools.common.parse_value(fields),
                metadata=metadata
            )
        )

    @core.http.rest_route(
        routes=build_route([
            '/search_extract',
            '/search_extract/<string:model>',
            '/search_extract/<string:model>/<string:order>',
            '/search_extract/<string:model>/<int:limit>/<string:order>',
            '/search_extract/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]),
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Search Extract',
            description='Search the given domain and extract the fields.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/DataFields',
                            },
                        }
                    },
                    'example': ['name', 'bank_ids/acc_number'],
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
                'metadata': {
                    'name': 'metadata',
                    'description': 'Show Metadata',
                    'schema': {
                        'type': 'boolean'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Extract Data',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ExtractData'
                            },
                            'example': [
                              {'bank_ids': [], 'id': 1, 'name': 'YourCompany'},
                              {'bank_ids': [], 'id': 2, 'name': 'OdooBot'}
                            ],
                        },

                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def search_extract(
        self,
        model,
        domain=None,
        fields=None,
        limit=None,
        offset=0,
        order=None,
        metadata=False,
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        records = request.env[model].search(
            domain, limit=limit, offset=offset, order=order
        )
        context = dict(records.env.context)
        context.pop('active_test', False)
        records.with_context(context)
        return request.make_json_response(
            records.rest_extract_data(
                tools.common.parse_value(fields),
                metadata=metadata
            )
        )

    #----------------------------------------------------------
    # Create / Update / Delete
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route([
            '/create',
            '/create/<string:model>',
        ]),
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Create',
            description='Creates new records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                'oneOf': [
                                    {'$ref': '#/components/schemas/RecordTuple'},
                                    {
                                        'type': 'array',
                                        'items': {
                                            '$ref': '#/components/schemas/RecordValues'
                                        }
                                    }
                                ],
                            },
                        },
                    },
                    'example': {'name': 'New Name'},
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def create(self, model, values=None, **kw):
        return request.make_json_response(
            request.env[model].create(
                tools.common.parse_value(values, {})
            ).ids
        )

    @core.http.rest_route(
        routes=build_route([
            '/write',
            '/write/<string:model>',
        ]),
        methods=['PUT'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Write',
            description='Update records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
                },
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordValues'
                            },
                        },
                    },
                    'example': {'name': 'New Name'},
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def write(self, model, ids=None, values=None, **kw):
        records = request.env[model].browse(tools.common.parse_ids(ids))
        records.write(tools.common.parse_value(values, {}))
        return request.make_json_response(records.ids)



    @core.http.rest_route(
        routes=build_route([
            '/write_multi',
            '/write_multi/<string:model>',
        ]),
        methods=['PUT'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Write',
            description='Update records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/MultiWriteValues'
                            },
                        },
                    },
                    'example': [[[1, 2], {'name': 'New Name'}]],
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def write_multi(self, model, values=None, **kw):
        values = tools.common.parse_value(values, [])
        record_ids = []
        for ids, vals in values:
            records = request.env[model].browse(
                tools.common.parse_ids(ids)
            )
            records.write(vals)
            record_ids.extend(records.ids)
        return request.make_json_response(record_ids)

    @core.http.rest_route(
        routes=build_route([
            '/create_update',
            '/create_update/<string:model>',
        ]),
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Create or Update',
            description='Creates or update a record.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': [('email', '=', 'admin@yourcompany.example.com')],
                },
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordValues'
                            },
                        },
                    },
                    'example': {'name': 'New Name'},
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
                'type': {
                    'name': 'type',
                    'description': 'Update Type',
                    'schema': {
                        'type': 'string',
                        'enum': ['limit', 'check', 'multi'],
                    }
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def create_update(
        self, model, domain, values=None, order=None, type='limit', **kw
    ):
        values = tools.common.parse_value(values, {})
        domain = tools.common.parse_domain(domain)
        limit = 1 if type == 'limit' else None
        records = request.env[model].search(
            domain, order=order, limit=limit
        )
        if type == 'check' and len(records) > 1:
            raise werkzeug.exceptions.BadRequest(
                'Multiple records were found for the given domain!'
            )
        if not records:
            records = request.env[model].create(values)
        else:
            records.write(values)
        return request.make_json_response(
            records.ids
        )

    @core.http.rest_route(
        routes=build_route([
            '/unlink',
            '/unlink/<string:model>',
        ]),
        methods=['DELETE'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Delete',
            description='Delete records.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
                },
            },
            responses={
                '200': {
                    'description': 'Result',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'boolean'
                            },
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def unlink(self, model, ids=None, **kw):
        return request.make_json_response(
            request.env[model].browse(
                tools.common.parse_ids(ids)
            ).unlink()
        )


    ############ supply plus ################

    @core.http.rest_route(
        routes=build_route('/add/product'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def add_product(self, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')
        segment_ids = data.get('segments')
        category_id = data.get('category_id')
        brand_id = data.get('brand_id')
        list_price = data.get('list_price')
        # subcategory_ids = data.get('subcategory')

        product = request.env['product.template'].sudo().create({
            "name": name,
            "categ_id": int(category_id),
            "segment_ids": segment_ids,
            'brancd_id': int(brand_id),
            'list_price': list_price,
            "company_id": 1
            # "product_tag_ids": subcategory_ids


        })

        if product:
            result = {"status": "success", "message": "Product created"}
        else:
            result = {"status": "failed", "message": "Couldn't create product"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    # read products
    @core.http.rest_route(
        routes=build_route('/get/products'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def products(self, **kw):
        products = request.env['product.template'].sudo().search([])
        product_datas = []
        segments = []
        for product in products:
            product_details = {
                "id": product.id,
                "name": product.name,
                "category": product.categ_id.id,
                "brand": product.brand_id.id,
                "segments": [p.id for p in product.segment_ids],
                "price": product.list_price,
                "subcategory_ids" : [p.id for p in product.product_tag_ids]
            }
            product_datas.append(product_details)

        result = {"status": "success", "data": product_datas}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    # segment
    @core.http.rest_route(
        routes=build_route('/segments'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def segments(self, **kw):
        segments = request.env['product.segment'].sudo().search([])
        segment_datas = []
        for segment in segments:
            segment_details = {
                "id": segment.id,
                "name": segment.name
            }
            segment_datas.append(segment_details)

        result = {"status": "success", "data": segment_datas}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    # brand
    @core.http.rest_route(
        routes=build_route('/brands'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def brands(self, **kw):
        brands = request.env['product.brand'].sudo().search([])
        brand_datas = []
        for brand in brands:
            brand_details = {
                "id": brand.id,
                "name": brand.name
            }
            brand_datas.append(brand_details)

        result = {"status": "success", "data": brand_datas}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    @core.http.rest_route(
        routes=build_route('/update/product'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True

    )
    def update_product(self, **kw):
        data = json.loads(request.httprequest.data)
        product_id = int(data.get('product_id'))
        name = data.get('name')

        product = request.env['product.template'].sudo().browse(product_id)
        category_id = product.categ_id.id
        segment_ids = product.segment_ids
        brand_id = product.brand_id.id
        list_price = product.list_price

        if data.get('category_id'):
            category_id = int(data.get('category_id'))

        if data.get('segments'):
            segment_ids = data.get('segments')

        if data.get('brand_id'):
            brand_id = int(data.get('brand_id'))

        if data.get('list_price'):
            brand_id = int(data.get('list_price'))

        if product:
            product.update({
                'name': name,
                'segment_ids': segment_ids,
                'categ_id': category_id,
                'brancd_id' :brand_id.id,
                'list_price': list_price

            })

            result = {"status": "success", "message": "Product updated"}
        else:
            result = {"status": "failed", "message": "Product not found"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)



    # journals
    @core.http.rest_route(
        routes=build_route('/journals'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def journals(self, **kw):
        journals = request.env['account.journal'].sudo().search([('type', 'in', ('bank', 'cash'))])
        journal_datas = []
        for journal in journals:
            journal_details = {
                "id": journal.id,
                "name": journal.name
            }
            journal_datas.append(journal_details)

        result = {"status": "success", "data": journal_datas}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    # driver
    @core.http.rest_route(
        routes=build_route('/drivers'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def drivers(self, **kw):
        drivers = request.env['driver'].sudo().search([])
        driver_datas = []
        for driver in drivers:
            driver_details = {
                "id": driver.id,
                "name": driver.name
            }
            driver_datas.append(driver_details)

        result = {"status": "success", "data": driver_datas}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)



    # create category api
    @core.http.rest_route(
        routes=build_route('/add/category'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def add_category(self, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')

        categ = request.env['product.category'].sudo().create({"name": name})
        result = {"status": "success", "message": "Category added"}
        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    # variants api
    @core.http.rest_route(
        routes=build_route('/get/product/variants'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def get_product_variants(self, **kw):
        data = json.loads(request.httprequest.data)
        product_template_id = data.get('product_id')

        product_ids = request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(product_template_id))])
        product_datas = []
        for product in product_ids:
            variants = []
            for val in product.product_template_variant_value_ids:
                vals = {
                    val.attribute_id.name: val.name
                }
                variants.append(vals)
            product_details = {
                "id": product.id,
                "name": product.name,
                "values": variants
            }
            product_datas.append(product_details)

        result = {"status": "success", "data": product_datas}
        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    @core.http.rest_route(
        routes=build_route('/get/invoice'),
        methods=['GET'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def get_invoice(self, **kw):
        data = json.loads(request.httprequest.data)
        sale_order_id = data.get('order_id')
        invoices = []

        order = request.env['sale.order'].sudo().browse(int(sale_order_id))
        if order and order.invoice_ids:
            for invoice in order.invoice_ids:
                pdf = \
                request.env["ir.actions.report"].sudo()._render_qweb_pdf('account.account_invoices', [invoice.id],
                                                                         data={'report_type': 'pdf'})[0]

                b64_pdf = base64.b64encode(pdf)

                invoice_details = {
                    "data": b64_pdf
                }
                invoices.append(invoice_details)

        result = {"status": "success", "data": invoices}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    @core.http.rest_route(
        routes=build_route('/create/order'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def create_order(self, **kw):
        data = json.loads(request.httprequest.data)
        partner_id = data.get('partner_id')
        order_lines = data.get('order_lines')
        order_id = data.get('order_id')
        driver_id = data.get('driver_id')
        warehouse_id = data.get('warehouse_id')
        delivery_date_time = data.get('delivery_date_time')

        driver = request.env['driver'].sudo().browse(int(driver_id))

        partner = request.env['res.partner'].sudo().browse(int(partner_id))

        company = request.env['res.company'].sudo().browse(1)

        warehouse = request.env['stock.warehouse'].sudo().browse(int(warehouse_id))

        existing_orders = request.env['sale.order'].sudo().search([('order_id', '=', order_id)])
        if existing_orders:
                result = {"status": "failed", "message": "Order ID already exists!"}
        else:
            sale_order = request.env['sale.order'].sudo().create({
                "partner_id": partner.id,
                "company_id": warehouse.company_id.id,
                "order_id": order_id,
                "driver_id": driver.id if driver else False,
                "warehouse_id": warehouse.id,
                "commitment_date": delivery_date_time
            })

            if sale_order:
                for line in order_lines:

                    request.env['sale.order.line'].sudo().create({
                        "product_id": line['product_id'],
                        "product_uom_qty": line['qty'],
                        "order_id": sale_order.id,
                        "price_unit": line['unit_price'],
                        "discount": line['discount'] if 'discount' in line else False
                    })
                sale_order.action_confirm()
                invoice_record = sale_order._create_invoices(final=True)
                invoice_record.action_post()

                result = {"status": "success", "message": "Order Created", "order_id": sale_order.id}
            else:
                result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)



    # customer creation
    @core.http.rest_route(
        routes=build_route('/create/customer'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def create_customer(self, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')
        code = data.get('country_code')
        company = request.env['res.company'].sudo().search([], limit=1)
        country = request.env['res.country'].sudo().search([('code', '=', code)], limit=1)
        datas = []
        customer = request.env['res.partner'].sudo().create({
            "company_id": company.id,
            "name": name,
            "email": email,
            "mobile": mobile,
            "country_id": country.id if country else False

        })
        if customer:
            datas.append({'id': customer.id})



        if customer:
            result = {"status": "success", "message": "Customer added", 'data': datas}
        else:
            result = {"status": "success", "message": "Something went wrong!", 'data':datas}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    # edit customer
    @core.http.rest_route(
        routes=build_route('/update/customer'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def update_customer(self, **kw):
        data = json.loads(request.httprequest.data)
        partner_id = data.get('partner_id')
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')

        customer = request.env['res.partner'].sudo().browse(int(partner_id))
        if customer:

            customer.update({
            "name": name,
            "email": email,
            "mobile": mobile
                })
            result = {"status": "success", "message": "Customer updated"}
        else:
            result = {"status": "success", "message": "Customer not found!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)



    # payment
    @core.http.rest_route(
        routes=build_route('/create/payment'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def create_payment(self, **kw):
        data = json.loads(request.httprequest.data)
        order_id = data.get('order_id')
        amount = data.get('amount')
        payment_method_id = data.get('payment_method_id')

        order = request.env['sale.order'].sudo().browse(int(order_id))
        journal = request.env['account.journal'].sudo().browse(int(payment_method_id))

        if order:

            if order.invoice_ids:
                payment = request.env['account.payment'].sudo().create({
                    "partner_id": order.partner_id.id,
                    "amount": amount,
                    "payment_type": "inbound",
                    "company_id": order.company_id.id,
                    "journal_id": journal.id if journal else order.invoice_ids[0].journal_id.id,
                    "payment_method_line_id":journal.inbound_payment_method_line_ids[0].id if journal and journal.inbound_payment_method_line_ids else 1

                })
                payment.action_post()

                move_lines = payment.line_ids.filtered(lambda line: line.account_type in ('asset_receivable', 'liability_payable') and not line.reconciled)
                for line in move_lines:
                    for inv in order.invoice_ids:
                        inv.js_assign_outstanding_line(line.id)

            result = {"status": "success", "message": "Payment created"}
        else:
            result = {"status": "success", "message": "Order not found!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    @core.http.rest_route(
        routes=build_route('/confirm/delivery'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def confirm_delivery(self, **kw):
        data = json.loads(request.httprequest.data)
        order_id = data.get('order_id')
        sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        precision_digits = request.env['decimal.precision'].precision_get('Product Unit of Measure')
        result = {}

        if sale_order and sale_order.picking_ids:
            for picking in sale_order.picking_ids:
                if picking.show_set_qty_button:
                    picking.action_set_quantities_to_reservation()
                    picking.action_assign()
                    picking._action_done()
                    result = {"status": "success", "message": "Delivery confirmed"}
                else:

                    no_quantities_done_ids = set()
                    no_reserved_quantities_ids = set()

                    if all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                           picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel'))):
                        no_quantities_done_ids.add(picking.id)
                    if all(float_is_zero(move_line.reserved_qty, precision_rounding=move_line.product_uom_id.rounding)
                           for move_line in picking.move_line_ids):
                        no_reserved_quantities_ids.add(picking.id)
                    pickings_without_quantities = picking.filtered(
                        lambda p: p.id in no_quantities_done_ids and p.id in no_reserved_quantities_ids)
                    if pickings_without_quantities:
                        result = {"status": "failed", "message": "You cannot validate a transfer if no quantities are reserved nor done. To force the transfer, switch in edit mode and encode the done quantities."}

                    else:
                        picking.action_assign()
                        picking._action_done()

                        result = {"status": "success", "message": "Delivery confirmed"}
        else:
            result = {"status": "success", "message": "Order not found!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    @core.http.rest_route(
        routes=build_route('/archive/customer'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def archive_customer(self, **kw):
        data = json.loads(request.httprequest.data)
        partner_id = data.get('partner_id')
        partner = request.env['res.partner'].sudo().browse(int(partner_id))
        if partner:
            partner.action_archive()
            result = {"status": "success", "message": "Customer Archived"}
        else:
            result = {"status": "success", "message": "Customer not found!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    # CREATE DRIVER
    @core.http.rest_route(
        routes=build_route('/create/driver'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def create_driver(self, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')

        driver = request.env['driver'].sudo().create({
            "name": name
        })

        if driver:

            result = {"status": "success", "message": "Created Successfully", "id": driver.id}
        else:
            result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    # UPDATE DRIVER
    @core.http.rest_route(
        routes=build_route('/update/driver'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def driver_upd(self, **kw):
        data = json.loads(request.httprequest.data)
        name = data.get('name')
        driver_id = data.get('driver_id')

        driver = request.env['driver'].sudo().browse(int(driver_id))

        if driver:
            driver.write({
                "name": name
            })

            result = {"status": "success", "message": "Updated Successfully"}
        else:
            result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    # UPDATE DRIVER IN ORDER
    @core.http.rest_route(
        routes=build_route('/order/update/driver'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def update_driver(self, **kw):
        data = json.loads(request.httprequest.data)
        driver_id = data.get('driver_id')
        order_id = data.get('order_id')

        driver = request.env['driver'].sudo().browse(int(driver_id))
        order = request.env['sale.order'].sudo().browse(int(order_id))
        if order and driver:

            order.update({
            "driver_id": driver.id,

                })
            result = {"status": "success", "message": "Updated Order"}
        else:
            result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


    # UPDATE ORDER STATUS
    @core.http.rest_route(
        routes=build_route('/order/status/update'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def update_order_status(self, **kw):
        data = json.loads(request.httprequest.data)
        status = data.get('status')
        order_id = data.get('order_id')
        order = request.env['sale.order'].sudo().browse(int(order_id))
        if order and status:

            order.update({
            "order_status": status,

                })
            result = {"status": "success", "message": "Updated Order Status"}
        else:
            result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @core.http.rest_route(
        routes=build_route('/cancel/order'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def cancel_order(self, **kw):
        data = json.loads(request.httprequest.data)
        order_id = data.get('order_id')
        order = request.env['sale.order'].sudo().browse(int(order_id))
        done_po = False


        if order:
            purchase_orders = order._get_purchase_orders()
            if purchase_orders:
                done_po = purchase_orders.filtered(lambda p: p.state in ('purchase', 'done'))
            if order.state != 'draft' and order.invoice_ids.filtered(
                    lambda inv: inv.state in ['draft', 'posted'] and not order.picking_ids.filtered(
                        lambda picking: picking.state == 'done')) and not done_po:

                invoices = order.invoice_ids.filtered(lambda inv: inv.state in ['draft', 'posted'])
                if invoices:
                    for invoice in invoices:
                        if invoice.state == 'draft':
                            invoice.button_cancel()

                        elif invoice.state == 'posted':
                            move_reversal = request.env['account.move.reversal'].with_context(
                                active_model="account.move",
                                active_ids=invoice.ids).create(
                                {
                                    'date': invoice.invoice_date,
                                    'refund_method': 'refund',
                                    'journal_id': invoice.journal_id.id,
                                })
                            reversal = move_reversal.reverse_moves()
                            credit_note = request.env['account.move'].browse(reversal['res_id'])
                            credit_note.action_post()
                            amount = invoice.amount_total - invoice.amount_residual
                            if invoice.payment_state in ['paid', 'partial']:
                                payments = request.env['account.payment.register'].with_context(
                                    active_model='account.move',
                                    active_ids=credit_note.ids).create(
                                    {
                                        'amount': amount,
                                        'group_payment': True,
                                    })._create_payments()
                    # purchase_order = order._get_purchase_orders()
                    # if purchase_order:
                    #     for po in purchase_order:
                    #         po.button_cancel()

                    order._action_cancel()
                    # order.order_line.purchase_line_ids.order_id
                    result = {"status": "success", "message": "Order Cancelled!"}

            elif order.state != 'draft' and order.picking_ids.filtered(lambda picking: picking.state == 'done'):
                result = {"status": "success", "message": "This order cannot be cancelled as it is delivered!"}

            elif order.state != 'draft' and done_po:
                result = {"status": "success", "message": "This order cannot be cancelled as there are completed purchase orders!"}
            else:
                purchase_order = order._get_purchase_orders()
                if purchase_order:
                    for po in purchase_order:
                        po.button_cancel()
                order._action_cancel()
                result = {"status": "success", "message": "Order Cancelled!"}
        else:
            result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @core.http.rest_route(
        routes=build_route('/return/order'),
        methods=['POST'],
        rest_access_hidden=True,
        disable_logging=True,
        ensure_db=True,
        protected=True
    )
    def return_order(self, **kw):
        data = json.loads(request.httprequest.data)
        partner_id = data.get('partner_id')
        order_lines = data.get('order_lines')
        order_id = data.get('order_id')
        driver_id = data.get('driver_id')
        warehouse_id = data.get('warehouse_id')

        driver = request.env['driver'].sudo().browse(int(driver_id))

        partner = request.env['res.partner'].sudo().browse(int(partner_id))

        company = request.env['res.company'].sudo().browse(1)

        warehouse = request.env['stock.warehouse'].sudo().browse(int(warehouse_id))

        existing_orders = request.env['sale.order'].sudo().search([('order_id', '=', order_id)])
        if existing_orders:
            result = {"status": "failed", "message": "Order ID already exists!"}
        else:
            sale_order = request.env['sale.order'].sudo().create({
                "partner_id": partner.id,
                "company_id": partner.company_id.id or company.id,
                "order_id": order_id,
                "driver_id": driver.id if driver else False,
                "warehouse_id": warehouse.id,
                "is_return": True,
                "return_type": warehouse.return_type_id.id,

            })

            if sale_order:
                for line in order_lines:
                    request.env['sale.order.line'].sudo().create({
                        "product_id": line['product_id'],
                        "product_uom_qty": line['qty'],
                        "order_id": sale_order.id,
                        "price_unit": line['unit_price'],
                        "discount": line['discount'] if 'discount' in line else False,
                        "is_return": True,
                        "location_id": warehouse.lot_stock_id.id

                    })
                sale_order.action_confirm()

                invoice_record = sale_order._create_invoices(final=True)
                invoice_record.action_post()

                result = {"status": "success", "message": "Return Order Created", "order_id": sale_order.id}
            else:
                result = {"status": "success", "message": "Something went wrong!"}

        content = json.dumps(result, sort_keys=False, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)










