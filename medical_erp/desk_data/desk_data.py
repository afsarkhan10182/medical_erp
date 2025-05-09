import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def get_total_sales():
    sales = frappe.get_all(
        "Sales Invoice",
        fields=["SUM(grand_total) as total"],
        filters={"docstatus": 1}
    )
    return sales[0].total or 0

@frappe.whitelist()
def get_purchase_on_credit():
    purchases = frappe.get_all(
        "Purchase Invoice",
        fields=["SUM(outstanding_amount) as total"],
        filters={"docstatus": 1, "outstanding_amount": [">", 0]}
    )
    return purchases[0].total or 0

@frappe.whitelist()
def get_sales_on_credit():
    sales = frappe.get_all(
        "Sales Invoice",
        fields=["SUM(outstanding_amount) as total"],
        filters={"docstatus": 1, "outstanding_amount": [">", 0]}
    )
    return sales[0].total or 0

@frappe.whitelist()
def get_monthly_profit():
    today = datetime.today()
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    sales = frappe.get_all(
        "Sales Invoice",
        fields=["SUM(grand_total) as total"],
        filters={
            "posting_date": [">=", start_of_month],
            "docstatus": 1
        }
    )
    purchases = frappe.get_all(
        "Purchase Invoice",
        fields=["SUM(grand_total) as total"],
        filters={
            "posting_date": [">=", start_of_month],
            "docstatus": 1
        }
    )
    total_sales = sales[0].total or 0
    total_purchases = purchases[0].total or 0
    return total_sales - total_purchases

@frappe.whitelist()
def get_near_expiry_data():
    today = datetime.today().date()
    threshold_date = today + timedelta(days=2)

    # Join Item with Batch and fetch items with expiry within next 2 days
    results = frappe.db.sql("""
        SELECT 
            i.name AS item_code,
            i.item_name,
            b.name AS batch_id,
            b.expiry_date,
            b.batch_qty,
            i.stock_uom,
            i.standard_rate AS rate
        FROM 
            `tabBatch` b
        JOIN 
            `tabItem` i ON b.item = i.name
        WHERE 
            b.expiry_date IS NOT NULL
            AND b.expiry_date <= %s
            AND i.disabled = 0
        ORDER BY 
            b.expiry_date ASC
    """, (threshold_date,), as_dict=True)

    for row in results:
        # Determine status
        row["status"] = "Expired" if row["expiry_date"] <= today else "Near Expiry"

        # Fetch the Item Tax Template linked to the Item
        item_tax = frappe.get_all(
            "Item Tax",
            filters={
                "parent": row["item_code"],
                "valid_from": ["<=", today]  # Ensure the template is valid for today
            },
            fields=["item_tax_template"],
            order_by="valid_from desc",
            limit=1
        )

        sgst_rate = 0
        cgst_rate = 0
        if item_tax and item_tax[0].item_tax_template:
            # Fetch SGST and CGST rates from the Item Tax Template Detail
            taxes = frappe.get_all(
                "Item Tax Template Detail",
                filters={"parent": item_tax[0].item_tax_template},
                fields=["tax_type", "tax_rate"]
            )

            for tax in taxes:
                if "SGST" in tax.tax_type:
                    sgst_rate = tax.tax_rate or 0
                elif "CGST" in tax.tax_type:
                    cgst_rate = tax.tax_rate or 0

        row["sgst_rate"] = sgst_rate
        row["cgst_rate"] = cgst_rate

        # Calculate base amount (batch_qty * rate)
        base_amount = (row["batch_qty"] or 0) * (row["rate"] or 0)

        # Calculate SGST and CGST amounts
        row["sgst_amount"] = (base_amount * sgst_rate) / 100
        row["cgst_amount"] = (base_amount * cgst_rate) / 100

        # Calculate total (base_amount + taxes)
        row["total"] = base_amount + row["sgst_amount"] + row["cgst_amount"]

    return results

@frappe.whitelist()
def get_stock_data():
    items = frappe.get_all(
        "Item Reorder",
        fields=[
            "parent as item_code",
            "warehouse",
            "warehouse_reorder_level as re_order_level"
        ]
    )

    results = []
    for reorder in items:
        projected_qty = frappe.db.get_value("Bin", {
            "item_code": reorder.item_code,
            "warehouse": reorder.warehouse
        }, "projected_qty") or 0

        if projected_qty < reorder.re_order_level:
            stock_uom = frappe.db.get_value("Item", reorder.item_code, "stock_uom")
            results.append({
                "item_code": reorder.item_code,
                "warehouse": reorder.warehouse,
                "stock_qty": projected_qty,
                "re_order_level": reorder.re_order_level,
                "stock_uom": stock_uom
            })

    return results

@frappe.whitelist()
def get_todays_report():
    today = datetime.today().strftime('%Y-%m-%d')

    sales = frappe.get_all(
        "Sales Invoice",
        fields=["SUM(grand_total) as total_sales"],
        filters={
            "posting_date": today,
            "docstatus": 1
        }
    )
    total_sales = sales[0].total_sales or 0

    purchases = frappe.get_all(
        "Purchase Invoice",
        fields=["SUM(grand_total) as total_purchases"],
        filters={
            "posting_date": today,
            "docstatus": 1
        }
    )
    total_purchases = purchases[0].total_purchases or 0

    gross_profit = total_sales - total_purchases
    net_profit = gross_profit

    return {
        "total_orders": len(sales),
        "total_sales": total_sales,
        "gross_profit": gross_profit,
        "net_profit": net_profit
    }