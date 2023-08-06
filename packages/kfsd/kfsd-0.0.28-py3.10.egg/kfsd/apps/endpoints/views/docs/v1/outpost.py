from drf_spectacular.utils import OpenApiExample


class OutpostV1Doc:
    @staticmethod
    def modelviewset_list_path_examples():
        return []

    @staticmethod
    def modelviewset_list_examples():
        return []

    @staticmethod
    def modelviewset_get_path_examples():
        return []

    @staticmethod
    def modelviewset_get_examples():
        return []

    @staticmethod
    def modelviewset_create_examples():
        return [
            OpenApiExample(
                "Outpost - Create",
                value={
                    "msg_queue_info": {
                        "exchange_name": "remind_exchange",
                        "queue_name": "remind_queue",
                        "routing_key": "",
                    },
                    "msg": {
                        "action": "REORDER_CERT",
                        "type": "ONETIME",
                        "data": {
                            "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                            "remind_by": "05/31/2023, 08:01:19 AM",
                            "to_msg_queue": {
                                "exchange_name": "certs_exchange",
                                "queue_name": "certs_queue",
                                "routing_key": "certs",
                            },
                            "body": {
                                "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA"
                            },
                        },
                    },
                },
                request_only=True,
                response_only=False,
            ),
        ]

    @staticmethod
    def modelviewset_delete_path_examples():
        return []

    @staticmethod
    def modelviewset_patch_path_examples():
        return []

    @staticmethod
    def modelviewset_patch_examples():
        return []
