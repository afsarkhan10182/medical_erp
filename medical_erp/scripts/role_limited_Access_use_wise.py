import frappe

def create_shop_user_role():
    if not frappe.db.exists("Role", "Shop User"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Shop User",
            "desk_access": 1
        })
        role.insert()
        print("✅ Created Shop User role")
    else:
        print("Shop User role already exists")

def assign_shop_user_role(user_email):
    create_shop_user_role()  # Ensure role exists
    user = frappe.get_doc("User", user_email)
    if "Shop User" not in [r.role for r in user.roles]:
        user.append("roles", {"role": "Shop User"})
        user.save()
        print(f"✅ Assigned Shop User role to {user_email}")
    else:
        print(f"Shop User role already assigned to {user_email}")

def assign_shop_permission(user_email, shop_name):
    if not frappe.db.exists("User Permission", {"user": user_email, "allow": "Shop", "for_value": shop_name}):
        frappe.get_doc({
            "doctype": "User Permission",
            "user": user_email,
            "allow": "Shop",
            "for_value": shop_name
        }).insert()
        print(f"✅ Assigned permission for {user_email} to access {shop_name}")
    else:
        print(f"Permission for {user_email} to access {shop_name} already exists")

def setup_multiple_shop_users(user_shop_list):
    create_shop_user_role()
    for user_email, shop_name in user_shop_list:
        assign_shop_user_role(user_email)
        assign_shop_permission(user_email, shop_name)

# Only execute if run directly (not when imported)
if __name__ == "__main__":
    user_shop_list = [
        ("shop1@test.com", "Shop 1"),
        ("shop2@test.com", "Shop 2"),
    ]
    setup_multiple_shop_users(user_shop_list)