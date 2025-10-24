"""
Hardcoded form schema for Rawad close cash submissions.
New 12-section structure with dynamic lists and auto-calculations.
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
                    "label": "Cashier Name",
                    "type": "text",
                    "required": False
                },
                {
                    "key": "date",
                    "label": "Date",
                    "type": "date",
                    "required": False
                },
                {
                    "key": "shift_time",
                    "label": "Shift Time",
                    "type": "select",
                    "options": ["Morning", "Day", "Evening", "Night"],
                    "required": False
                }
            ]
        },
        {
            "title": "Recharge Cards",
            "fields": [
                {
                    "key": "recharge_placeholder",
                    "label": "This section is reserved for future use",
                    "type": "text",
                    "required": False,
                    "readonly": True
                }
            ]
        },
        {
            "title": "Special Credit",
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
                    "key": "delivery_shabeb_co",
                    "label": "Delivery Shabeb co.",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "delivery_employee",
                    "label": "Delivery Employee",
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
                    "key": "special_credit_total",
                    "label": "Special Credit Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Lebanese Cash Bills",
            "fields": [
                {
                    "key": "lebanese_5000_qty",
                    "label": "5,000 LBP (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "lebanese_10000_qty",
                    "label": "10,000 LBP (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "lebanese_20000_qty",
                    "label": "20,000 LBP (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "lebanese_50000_qty",
                    "label": "50,000 LBP (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "lebanese_100000_qty",
                    "label": "100,000 LBP (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "lebanese_cash_total",
                    "label": "Lebanese Cash Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Dollar Cash Bills",
            "fields": [
                {
                    "key": "dollar_1_qty",
                    "label": "$1 (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_5_qty",
                    "label": "$5 (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_10_qty",
                    "label": "$10 (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_20_qty",
                    "label": "$20 (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_50_qty",
                    "label": "$50 (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_100_qty",
                    "label": "$100 (Quantity)",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_rate",
                    "label": "Dollar Rate",
                    "type": "number",
                    "required": False
                },
                {
                    "key": "dollar_cash_total_usd",
                    "label": "Dollar Cash Total (USD)",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                },
                {
                    "key": "dollar_cash_total_lbp",
                    "label": "Dollar Cash Total (LBP)",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Cash Purchase",
            "type": "dynamic_list",
            "fields": [
                {
                    "key": "cash_purchase",
                    "label": "Cash Purchase Entries",
                    "type": "dynamic_list",
                    "list_fields": [
                        {"key": "amount", "label": "Amount", "type": "number"},
                        {"key": "currency", "label": "Currency", "type": "select", "options": ["lebanese", "dollar"]},
                        {"key": "name", "label": "Name", "type": "text"}
                    ]
                },
                {
                    "key": "cash_purchase_total",
                    "label": "Cash Purchase Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Credit Invoices",
            "type": "dynamic_list",
            "fields": [
                {
                    "key": "credit_invoices",
                    "label": "Credit Invoice Entries",
                    "type": "dynamic_list",
                    "list_fields": [
                        {"key": "amount", "label": "Amount", "type": "number"},
                        {"key": "currency", "label": "Currency", "type": "select", "options": ["lebanese", "dollar"]},
                        {"key": "name", "label": "Name", "type": "text"}
                    ]
                },
                {
                    "key": "credit_invoices_total",
                    "label": "Credit Invoices Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Employee On the House",
            "type": "dynamic_list",
            "fields": [
                {
                    "key": "employee_on_house",
                    "label": "Employee On the House Entries",
                    "type": "dynamic_list",
                    "list_fields": [
                        {"key": "amount", "label": "Amount", "type": "number"},
                        {"key": "currency", "label": "Currency", "type": "select", "options": ["lebanese", "dollar"]},
                        {"key": "name", "label": "Name", "type": "text"}
                    ]
                },
                {
                    "key": "employee_on_house_total",
                    "label": "Employee On the House Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Customer On the House",
            "type": "dynamic_list",
            "fields": [
                {
                    "key": "customer_on_house",
                    "label": "Customer On the House Entries",
                    "type": "dynamic_list",
                    "list_fields": [
                        {"key": "amount", "label": "Amount", "type": "number"},
                        {"key": "currency", "label": "Currency", "type": "select", "options": ["lebanese", "dollar"]},
                        {"key": "name", "label": "Name", "type": "text"}
                    ]
                },
                {
                    "key": "customer_on_house_total",
                    "label": "Customer On the House Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Bar On the House",
            "type": "dynamic_list",
            "fields": [
                {
                    "key": "bar_on_house",
                    "label": "Bar On the House Entries",
                    "type": "dynamic_list",
                    "list_fields": [
                        {"key": "amount", "label": "Amount", "type": "number"},
                        {"key": "currency", "label": "Currency", "type": "select", "options": ["lebanese", "dollar"]},
                        {"key": "name", "label": "Name", "type": "text"}
                    ]
                },
                {
                    "key": "bar_on_house_total",
                    "label": "Bar On the House Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Store",
            "type": "dynamic_list",
            "fields": [
                {
                    "key": "store",
                    "label": "Store Entries",
                    "type": "dynamic_list",
                    "list_fields": [
                        {"key": "amount", "label": "Amount", "type": "number"},
                        {"key": "currency", "label": "Currency", "type": "select", "options": ["lebanese", "dollar"]},
                        {"key": "name", "label": "Name", "type": "text"}
                    ]
                },
                {
                    "key": "store_total",
                    "label": "Store Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        },
        {
            "title": "Summary Results",
            "fields": [
                {
                    "key": "cash_in_hand_dollar",
                    "label": "Cash in Hand (Dollar)",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                },
                {
                    "key": "cash_in_hand_lebanese",
                    "label": "Cash in Hand (Lebanese)",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                },
                {
                    "key": "cash_out_of_hand",
                    "label": "Cash Out of Hand",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                },
                {
                    "key": "grand_total",
                    "label": "Grand Total",
                    "type": "number",
                    "required": False,
                    "readonly": True,
                    "calculated": True
                }
            ]
        }
    ]
}