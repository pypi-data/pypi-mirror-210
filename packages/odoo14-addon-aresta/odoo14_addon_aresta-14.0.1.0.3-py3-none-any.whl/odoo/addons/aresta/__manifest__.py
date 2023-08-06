{
    "name": "Odoo customizations for Aresta",
    "version": "14.0.1.0.3",
    "depends": [
        "delivery",
        "pos_order_to_sale_order",
        "pos_sale",
        "sale",
        "website_sale",
    ],
    "author": "Coopdevs Treball SCCL",
    "category": "Project Management",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "summary": """
        Odoo customizations for Aresta.
    """,
    "data": [
        "views/sale_order.xml",
        "views/sale_report.xml",
        "report/delivery_note_mail_template.xml",
        "report/stock_report_views.xml",
        "report/stock_report_deliveryslip.xml",
        "wizards/confirm_sale_order/confirm_sale_order.xml",
        "wizards/send_delivery_note/send_delivery_note.xml",
    ],
    "installable": True,
}
