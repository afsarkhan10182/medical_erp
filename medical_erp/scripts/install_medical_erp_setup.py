import frappe

# Create role function
def create_role():
    if not frappe.db.exists("Role", "Shopkeeper"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Shopkeeper",
            "desk_access": 1
        })
        role.insert()
        print("✅ Created role: Shopkeeper")

# Create user and assign role function
def create_user_and_assign_role():
    email = "shop1@test.com"
    if not frappe.db.exists("User", email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Shop 1",
            "roles": [{"role": "Shopkeeper"}],
            "send_welcome_email": 0
        })
        user.insert()
        print("✅ Created user:", email)
    else:
        user = frappe.get_doc("User", email)
        if "Shopkeeper" not in [r.role for r in user.roles]:
            user.append("roles", {"role": "Shopkeeper"})
            user.save()
            print("✅ Assigned Shopkeeper role to user.")

# Create shop record function
def create_shop_record():
    if not frappe.db.exists("Shop", {"shop_name": "Shop 1"}):
        shop = frappe.get_doc({
            "doctype": "Shop",
            "shop_name": "Shop 1",
            "owner_user": "shop1@test.com"
        })
        shop.insert()
        print("✅ Created Shop: Shop 1")

# Create user permission function
def create_user_permission():
    if not frappe.db.exists({
        "doctype": "User Permission",
        "user": "shop1@test.com",
        "allow": "Shop",
        "for_value": "Shop 1"
    }):
        frappe.get_doc({
            "doctype": "User Permission",
            "user": "shop1@test.com",
            "allow": "Shop",
            "for_value": "Shop 1"
        }).insert()
        print("✅ User Permission created for shop1@test.com → Shop 1")

# Assign workspace and hide unnecessary modules function
def assign_workspace_and_hide_modules():
    user = frappe.get_doc("User", "shop1@test.com")
    user.set("home_page", "/app/workspace/Shop Dashboard")  # Change this to your workspace name
    user.save()
    print("✅ Assigned custom dashboard as default")

    blocked_modules = [
        "CRM", "HR", "Projects", "Quality", "Support", "Education", "Asset", "Non Profit", "Website"
    ]
    for module in blocked_modules:
        if not frappe.db.exists("Block Module", {"module": module, "block_module_for": "User", "user": "shop1@test.com"}):
            frappe.get_doc({
                "doctype": "Block Module",
                "module": module,
                "block_module_for": "User",
                "user": "shop1@test.com"
            }).insert()
    print("✅ Blocked unnecessary modules for shop1@test.com")

# Run setup function (this should be called last)
def run_setup():
    create_role()
    create_user_and_assign_role()
    create_shop_record()
    create_user_permission()
    assign_workspace_and_hide_modules()

# Ensure the script runs everything in order
run_setup()
