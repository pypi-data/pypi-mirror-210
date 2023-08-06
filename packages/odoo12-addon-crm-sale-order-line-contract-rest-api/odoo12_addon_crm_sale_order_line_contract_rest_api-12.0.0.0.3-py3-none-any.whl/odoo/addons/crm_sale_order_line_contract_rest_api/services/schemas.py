def boolean_validator(field, value, error):
    if value and value not in ["true", "false"]:
        error(field, "Must be a boolean value: true or false")


S_CRM_LEAD_CREATE = {
    "order_lines": {
        "type": "list",
        "empty": True,
        "schema": {
            "type": "dict",
            "schema": {
                "product_id": {"type": "integer", "required": True},
                "price_unit": {"type": "float", "required": False},
                "attach_to_existing_contract": {
                    "type": "boolean",
                    "required": False
                },
                "contract_id": {
                    "type": "integer",
                    "required": False
                },
                "contract_date_start_type": {
                    "type": "string",
                    "required": False
                },
                "termination_interval": {
                    "type": "integer",
                    "required": False
                },
                "termination_rule_type": {
                    "type": "string",
                    "required": False
                }
            }
        }
    }
}
