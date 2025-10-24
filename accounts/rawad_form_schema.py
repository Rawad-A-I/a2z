"""
Hardcoded form schema for Rawad close cash submissions.
Based on the structure extracted from Rawad.xlsx.
"""

RAWAD_FORM_SCHEMA = {
    "sections": [
        {
            "title": "General",
            "fields": [
                {
                    "key": "black_market_daily_rate",
                    "label": "Black Market Daily Rate",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "cashier_name",
                    "label": "Cashier name",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "date",
                    "label": "Date",
                    "type": "date",
                    "required": False
                }
            ]
        },
        {
            "title": "Shift Time",
            "fields": [
                {
                    "key": "mtc_3_79",
                    "label": "MTC 3.79$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "mtc_4_5",
                    "label": "MTC 4.5$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "mtc_7_58",
                    "label": "MTC 7.58$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "mtc_15_15",
                    "label": "MTC 15.15$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "alfa_3_03",
                    "label": "Alfa 3.03$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "alfa_4_5",
                    "label": "Alfa 4.5$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "alfa_7_58",
                    "label": "Alfa 7.58$",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "alfa_15_15",
                    "label": "Alfa 15.15$",
                    "type": "text",
                    "required": False
                }
            ]
        },
        {
            "title": "Total in Account $",
            "fields": [
                {
                    "key": "rayan_invoices_credit",
                    "label": "Rayan Invoices Credit",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "employee_invoice_credit",
                    "label": "Employee Invoice Credit",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "delivery_chabeb_co",
                    "label": "Delivery Chabeb co.",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "delivery_employee",
                    "label": "Delivery Employee.",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "waste_goods",
                    "label": "Waste Goods",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "total_l_l",
                    "label": "Total L.L.",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "cash_in_hand_l_l",
                    "label": "Cash in Hand $/L.L.",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "cash_in_hand_lbp",
                    "label": "Cash in Hand LBP",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "cash_out_from_draw",
                    "label": "Cash out from draw",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "total_shift_sales",
                    "label": "Total shift sales",
                    "type": "number",
                    "required": False
                }
            ]
        },
        {
            "title": "Coffee Machine",
            "fields": [
                {
                    "key": "item",
                    "label": "ITEM",
                    "type": "text",
                    "required": False
                }
            ]
        }
    ]
}
