RECORD = 'record'
FIELD = 'field'

THREADS_MAPPING = {
    'createdBy': RECORD,
    'createdAt': FIELD,
    'to': FIELD,
    'cc': FIELD,
    'type': FIELD,
    'source': RECORD,
    'id': FIELD,
    'bcc': FIELD,
    'action': RECORD,
    'body': FIELD,
    'state': FIELD
}

CONVERSATIONS_MAPPING = {
    'subject': FIELD,
    'status': FIELD,
    'state': FIELD,
    'type': FIELD,
    'threads': FIELD,
    'userUpdatedAt': FIELD,
    'assignee': RECORD,
    'createdAt': FIELD,
    'customFields': RECORD,
    'customerWaitingSince': RECORD,
    'number': FIELD,
    'mailboxId': FIELD,
    'closedBy': FIELD,
    'id': FIELD,
    'createdBy': RECORD,
    'closedAt': FIELD,
    'tags': RECORD,
    'bcc': FIELD,
    'preview': FIELD,
    'source': RECORD,
    'cc': FIELD,
    'folderId': FIELD,
    'primaryCustomer': RECORD
}

RATINGS_MAPPING = {
    'ratingUserId': FIELD,
    'number': FIELD,
    'threadid': FIELD,
    'ratingCustomerId': FIELD,
    'threadCreatedAt': FIELD,
    'ratingUserName': FIELD,
    'id': FIELD,
    'ratingId': FIELD,
    'type': FIELD,
    'ratingComments': FIELD,
    'ratingCreatedAt': FIELD,
    'ratingCustomerName': FIELD
}

CUSTOMERS_MAPPING = {
    'id': FIELD,
    'firstName': FIELD,
    'lastName': FIELD,
    'gender': FIELD,
    'organization': FIELD,
    'photoType': FIELD,
    'photoUrl': FIELD,
    'createdAt': FIELD,
    'updatedAt': FIELD,
    'background': FIELD,
    'emails': RECORD,
    'websites': RECORD,
    'chats': RECORD,
    'phones': RECORD,
    'social_profiles': RECORD,
    'address': RECORD
}

MAILBOXES_MAPPING = {
    'id': FIELD,
    'name': FIELD,
    'slug': FIELD,
    'email': FIELD,
    'createdAt': FIELD,
    'updatedAt': FIELD
}

FOLDERS_MAPPING = {
    'activeCount': FIELD,
    'updatedAt': FIELD,
    'totalCount': FIELD,
    'userId': FIELD,
    'mailboxId': FIELD,
    'type': FIELD,
    'name': FIELD,
    'id': FIELD
}

USERS_MAPPING = {
    'photoUrl': FIELD,
    'id': FIELD,
    'firstName': FIELD,
    'updatedAt': FIELD,
    'lastName': FIELD,
    'email': FIELD,
    'role': FIELD,
    'timezone': FIELD,
    'type': FIELD,
    'createdAt': FIELD
}
