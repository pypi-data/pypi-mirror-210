from rules import add_perm, always_allow

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models import ExemptionRequest

add_perm("fritak", always_allow)

# Apply for exemption
apply_exemptionrequest_predicate = has_person & has_global_perm(
    "fritak.add_exemptionrequest"
)
add_perm("fritak.apply_exemptionrequest_rule", apply_exemptionrequest_predicate)

# View index
view_index_predicate = has_person & apply_exemptionrequest_predicate
add_perm("fritak.view_index_rule", view_index_predicate)

# View details
view_details_predicate = has_person & (
    has_global_perm("fritak.view_exemptionrequest")
    | has_object_perm("fritak.view_exemptionrequest")
)
add_perm("fritak.view_details_rule", view_details_predicate)

# Delete exemptionrequest
delete_exemptionrequest_predicate = has_person & (
    has_global_perm("fritak.delete_exemptionrequest")
    | has_object_perm("fritak.delete_exemptionrequest")
)
add_perm("fritak.delete_exemptionrequest_rule", delete_exemptionrequest_predicate)

# Edit exemptionrequest
edit_exemptionrequest_predicate = has_person & (
    has_global_perm("fritak.change_exemptionrequest")
    | has_object_perm("fritak.change_exemptionrequest")
)
add_perm("fritak.edit_exemptionrequest_rule", edit_exemptionrequest_predicate)

# View archive
view_archive_predicate = has_person & (
    has_global_perm("fritak.view_exemptionrequest")
    | has_any_object("fritak.view_exemptionrequest", ExemptionRequest)
)
add_perm("fritak.view_archive_rule", view_archive_predicate)

# First check exemption request
check1_exemptionrequest_predicate = has_person & (
    has_global_perm("fritak.check1_exemptionrequest")
)
add_perm("fritak.check1_exemptionrequest_rule", check1_exemptionrequest_predicate)

# Second check exemption
check2_exemptionrequest_predicate = has_person & (
    has_global_perm("fritak.check2_exemptionrequest")
)
add_perm("fritak.check2_exemptionrequest_rule", check2_exemptionrequest_predicate)

# View menu
view_menu_predicate = has_person & (
    apply_exemptionrequest_predicate
    | check1_exemptionrequest_predicate
    | check2_exemptionrequest_predicate
    | view_archive_predicate
)
add_perm("fritak.view_menu_rule", view_menu_predicate)
