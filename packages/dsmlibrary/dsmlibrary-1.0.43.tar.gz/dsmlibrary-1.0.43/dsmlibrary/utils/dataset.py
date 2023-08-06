import requests
from . import check

def get_tag_ids(base_uri, tags, header):
    r = requests.get(f"{base_uri}/api/v2/tag/")
    check.check_http_status_code(response=r)
    tag_metas = {elm.get('name'):elm.get('id') for elm in r.json()}
    tag_ids = []
    for tag in tags:
        tag_id = tag_metas.get(tag, None)
        if tag_id is None:
            r = requests.post(f"{base_uri}/api/v2/tag/",
                              headers=header,
                              json={
                                  'name': tag
                              }
            )
            check.check_http_status_code(response=r)
            tag_id = r.json().get('id')
        tag_ids.append(tag_id)
    return tag_ids