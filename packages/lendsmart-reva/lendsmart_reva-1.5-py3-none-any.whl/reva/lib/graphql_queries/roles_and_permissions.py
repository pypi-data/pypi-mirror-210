"""
    Holds the query to update roles and permissions
"""


def update_roles_query(roles_data_list: dict):
    """
    Update roles query
    """
    return {
        "query": """
     	mutation MyMutation($data: [roles_insert_input!]!) {
	  insert_roles(objects: $data, on_conflict: {constraint: roles_pkey, update_columns: [object_meta,name,namespace_id,type_meta,description]}) {
	    returning {
	      id
	    }
	  }
	}""",
        "variables": {"data": roles_data_list},
    }

def update_permissions_query(permissions_data_list: dict):
    """
    Update permissions query
    """
    return {
        "query": """
     	mutation MyMutation($data: [permissions_insert_input!]!) {
	  insert_permissions(objects: $data, on_conflict: {constraint: permissions_pkey, update_columns: [description,metadata,name,role_id,updated_at]}) {
	    returning {
	      id
	    }
	  }
	}""",
        "variables": {"data": permissions_data_list},
    }
