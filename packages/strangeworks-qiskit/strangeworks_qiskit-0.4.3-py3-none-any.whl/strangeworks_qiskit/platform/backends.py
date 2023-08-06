"""backends.py"""
import json
from typing import Any, Dict, List, Optional

from strangeworks.core.client.platform import API, Operation
from strangeworks_core.types.backend import Backend
from strangeworks_core.utils import str_to_datetime


get_backends_query = Operation(
    query="""
    query backends(
        $product_slugs: [String!]
        $backend_type_slugs: [String!]
        $statuses: [BackendStatus!]
        $backend_tags: [String!]
    ) {
        backends(
            productSlugs: $product_slugs
            backendTypeSlugs: $backend_type_slugs
            backendStatuses: $statuses
            backendTags: $backend_tags
        ) {
            name
            slug
            remoteBackendId
            status
            backendRegistrations {
                data
                backendType {
                    slug
                    displayName
                }
            }
            product {
                slug
                productType
            }
        }
    }
"""
)


class Registration:
    """Backend Registration object.

    Includes the configuration data and type slug.
    """

    def __init__(
        self,
        backendType: Dict[str, Any],
        data: Optional[str] = None,
        dateCreated: Optional[str] = None,
        dateUpdated: Optional[str] = None,
        **kwargs,
    ):
        """Initialize Backend Registration.

        Parameters
        ----------
        backendType: Dict[str, Any]
            Backend type information. Contains the type slug.
        data: Optional[str]
            Backend configuration data.
        dateCreate: Optional[str]
            Date when the registration was created.
        dateUpdated: Optional[str]
            Date when the registration was last updated.
        """
        self.data = json.loads(data) if data else None
        self.type_slug = backendType.get("slug")
        self.date_created = str_to_datetime(dateCreated) if dateCreated else None
        self.date_updated = str_to_datetime(dateUpdated) if dateUpdated else None

    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]) -> "Registration":
        """Create a Backend Registration object from a dictionary.

        Parameters
        ----------
        cls
            The class object.
        dict_obj: Dict[str, Any]
            Dictionary object with registation info.

        Return
        ------
        :Registration
            A Registration object.
        """
        return cls(**dict_obj)

    def is_qiskit(self) -> bool:
        return self.type_slug == "sw-qiskit"


class QiskitBackend(Backend):
    """Backend Class representing a Qiskit Backend."""

    def __init__(
        self,
        backendRegistrations: List[Dict[str, Any]],
        **kwargs,
    ):
        """Initialize a Qiskit Backend object.

        Parameters
        ----------
        backendRegistration: List[Dict[str, Any]]
            List of registration objects with information about the backend.
        """
        super().__init__(**kwargs)
        self.registrations: List[Registration] = [
            Registration.from_dict(reg_dict) for reg_dict in backendRegistrations
        ]

    @classmethod
    def from_dict(cls, dict_obj: Dict[str, Any]) -> "QiskitBackend":
        """Create a QiskitBackend from a Dictionary."""
        return cls(**dict_obj)

    def get_registration(self) -> Dict[str, Any]:
        """Get Qiskit-related backend info."""
        return next(reg for reg in self.registrations if reg.is_qiskit())


def get(
    api: API,
    statuses: Optional[List[str]] = None,
    product_slugs: Optional[List[str]] = None,
) -> Optional[List[QiskitBackend]]:
    """Get backends from Strangeworks."""
    raw_results = api.execute(
        get_backends_query,
        statuses=statuses,
        product_slugs=product_slugs,
        backend_type_slugs=["sw-qiskit"],
    ).get("backends")
    return list(map(lambda x: QiskitBackend.from_dict(x), raw_results))


_get_status_query = Operation(
    query="""
    query backend_status($backend_slug: String!) {
        backend(slug: $backend_slug) {
            status
            remoteStatus
            name
        }
    }
"""
)


def get_status(api: API, backend_slug: str) -> Dict[str, Any]:
    """Get status for backend identified by its slug."""
    sw_status = api.execute(op=_get_status_query, backend_slug=backend_slug).get(
        "backend"
    )
    return {
        "backend_name": sw_status.get("name"),
        "backend_version": "0.0.0",
        "operational": True,
        "pending_jobs": 0,
        "status_msg": sw_status.get("remoteStatus"),
    }
