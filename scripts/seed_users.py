from datetime import date

print("=== SEED User Accounts IP FarmBook ===")

print("\n[0] Membersihkan user lama...")
logins_to_delete = ['management', 'pembibitan', 'produksi', 'processing', 'finance']
old_users = env['res.users'].search([('login', 'in', logins_to_delete)])
old_users.mapped('employee_id').unlink()
old_users.unlink()
env.cr.commit()

g_management = env.ref('ip_farmbook.group_ipfarm_management')
g_seedling   = env.ref('ip_farmbook.group_ipfarm_seedling')
g_production = env.ref('ip_farmbook.group_ipfarm_production')
g_processing = env.ref('ip_farmbook.group_ipfarm_processing')
g_finance    = env.ref('ip_farmbook.group_ipfarm_finance')

print("\n[1] Membuat user...")

users_data = [
    {'name': 'Manajer Farm',    'login': 'management', 'group': g_management},
    {'name': 'Budi Santoso',    'login': 'pembibitan', 'group': g_seedling},
    {'name': 'Sari Dewi',       'login': 'produksi',   'group': g_production},
    {'name': 'Raka Pratama',    'login': 'processing', 'group': g_processing},
    {'name': 'Finance Officer', 'login': 'finance',    'group': g_finance},
]

for d in users_data:
    user = env['res.users'].create({
        'name': d['name'],
        'login': d['login'],
        'password': 'ipfarm123',
        'groups_id': [(4, d['group'].id)],
    })
    env['hr.employee'].create({'name': d['name'], 'user_id': user.id})
    print(f"    {d['login']:15} → {d['group'].name}")

env.cr.commit()

print("\n" + "=" * 45)
print(f"  {'Login':<15} {'Password':<12} Role")
print(f"  {'-'*42}")
print(f"  {'admin':<15} {'admin':<12} Administrator")
for d in users_data:
    print(f"  {d['login']:<15} {'ipfarm123':<12} {d['group'].name}")
print("=" * 45)
