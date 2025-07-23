import pandas as pd


def get_foreign_key_instance(model, pk_value, field_name, fk_issues_list, row_num, required=False):
    """
    Helper to retrieve a foreign key instance and log issues if not found.
    Returns: (instance, success_flag)
    """
    if pd.isna(pk_value) or str(pk_value).strip() == '':
        if required:
            fk_issues_list.append(f"Missing required FK '{field_name}' in row {row_num}")
        return None, False
    try:
        instance_id = int(pk_value)
        instance = model.objects.filter(pk=instance_id).first()
        if not instance:
            fk_issues_list.append(f"{field_name} with ID '{instance_id}' not found (row {row_num})")
            return None, False
        return instance, True
    
    except (ValueError, TypeError):
        fk_issues_list.append(f"Invalid ID for {field_name}: '{pk_value}' (row {row_num})")
        return None, False
