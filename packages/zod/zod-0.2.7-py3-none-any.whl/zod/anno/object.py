from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
from pyquaternion import Quaternion

from zod.constants import Camera, Lidar
from zod.data_classes.box import Box2D, Box3D

OBJECT_CLASSES_DYNAMIC = (
    "Vehicle",
    "VulnerableVehicle",
    "Pedestrian",
    "Animal",
)
OBJECT_CLASSES_STATIC = (
    "PoleObject",
    "TrafficBeacon",
    "TrafficSign",
    "TrafficSignal",
    "TrafficGuide",
    "DynamicBarrier",
)
OBJECT_CLASSES = (
    *OBJECT_CLASSES_DYNAMIC,
    *OBJECT_CLASSES_STATIC,
    "Inconclusive",
)


@dataclass
class ObjectAnnotation:
    """Class to store dynamic object information."""

    # These are always available
    box2d: Box2D
    unclear: bool
    name: str
    uuid: str

    # These are not set if the object is unclear
    box3d: Optional[Box3D]  # This can be None even if the object is not unclear
    object_type: Optional[str]
    occlusion_level: Optional[str]
    artificial: Optional[str]
    with_rider: Optional[bool]
    emergency: Optional[bool]
    traffic_content_visible: Optional[bool]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ObjectAnnotation:
        """Create an ObjectAnnotation from a dictionary."""
        properties: Dict[str, Any] = data["properties"]
        unclear = (properties["class"] == "Inconclusive") or properties["unclear"]
        box2d = Box2D.from_points(points=data["geometry"]["coordinates"], frame=Camera.FRONT)
        box3d = None
        if "location_3d" in properties:
            box3d = Box3D(
                center=np.array(properties["location_3d"]["coordinates"]),
                size=np.array(
                    [
                        properties["size_3d_length"],
                        properties["size_3d_width"],
                        properties["size_3d_height"],
                    ]
                ),
                orientation=Quaternion(
                    properties["orientation_3d_qw"],
                    properties["orientation_3d_qx"],
                    properties["orientation_3d_qy"],
                    properties["orientation_3d_qz"],
                ),
                frame=Lidar.VELODYNE,
            )
        with_rider = properties.get("with_rider")
        with_rider = with_rider if with_rider is None else with_rider == "True"
        tcv = properties.get("traffic_content_visible")
        tcv = tcv if tcv is None else tcv == "True"
        return cls(
            uuid=properties["annotation_uuid"],
            box2d=box2d,
            box3d=box3d,
            unclear=unclear,
            name=properties["class"],
            object_type=properties.get("type", None),
            occlusion_level=properties.get("occlusion_ratio", None),
            artificial=properties.get("artificial", None),
            with_rider=with_rider,
            emergency=properties.get("emergency", None),
            traffic_content_visible=tcv,
        )

    def should_ignore_object(self, require_3d: bool = True) -> bool:
        """Check if the object should be ignored.

        Returns:
            True if the object should be ignored.
        """
        # Remove unclear objects
        if self.unclear:
            return True
        # Remove objects that dont have 3d box
        if self.box3d is None and require_3d:
            return True
        # If the object is artificial, reflection or an image, ignore it
        if self.artificial not in (None, "None"):
            return True

        # Class specific removals
        if self.name == "Vehicle":
            if self.object_type not in (
                "Car",
                "Bus",
                "Truck",
                "Van",
                "Trailer",
                "HeavyEquip",
            ):
                return True
        elif self.name == "VulnerableVehicle":
            if self.object_type not in ("Bicycle", "Motorcycle"):
                return True
            return not self.with_rider
        elif self.name == "Pedestrian":
            pass
        elif self.name == "TrafficSign":
            return not self.traffic_content_visible

        elif self.name == "TrafficSignal":
            return not self.traffic_content_visible

        return False


# Compatibility with old naming
AnnotatedObject = ObjectAnnotation
