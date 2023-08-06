# Copyright 2023 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Model that wraps all segmentation models of mmdetection
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import mmcv
import numpy as np
import torch.nn
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.segmentation import PolygonType, Segmentation
from mlcvzoo_base.api.interfaces import NetBased, Trainable
from mlcvzoo_base.api.model import SegmentationModel
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from mmdet.apis import inference_detector
from mmdet.core import INSTANCE_OFFSET
from mmdet.core.mask.structures import bitmap_to_polygon
from nptyping import Int, NDArray, Shape

from mlcvzoo_mmdetection.configuration import (
    MMDetectionConfig,
    MMDetectionInferenceConfig,
)
from mlcvzoo_mmdetection.model import MMDetectionModel

logger = logging.getLogger(__name__)

ImageType = NDArray[Shape["Height, Width, Any"], Int]


class MMSegmentationModel(
    MMDetectionModel[MMDetectionInferenceConfig],
    SegmentationModel[MMDetectionConfig, Union[str, ImageType]],
    NetBased[torch.nn.Module, MMDetectionInferenceConfig],
    Trainable,
):
    """
    Class for wrapping mmdetection segmentation models
    """

    def __init__(
        self,
        from_yaml: Optional[str] = None,
        configuration: Optional[MMDetectionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        init_for_inference: bool = False,
        is_multi_gpu_instance: bool = False,
    ) -> None:
        MMDetectionModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
            init_for_inference=init_for_inference,
            is_multi_gpu_instance=is_multi_gpu_instance,
        )
        SegmentationModel.__init__(
            self,
            configuration=self.configuration,
            mapper=AnnotationClassMapper(
                class_mapping=self.configuration.class_mapping,
                reduction_mapping=self.configuration.inference_config.reduction_class_mapping,
            ),
            init_for_inference=init_for_inference,
        )
        NetBased.__init__(self, net=self.net)
        Trainable.__init__(self)

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[MMDetectionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> MMDetectionConfig:
        return cast(
            MMDetectionConfig,
            create_basis_configuration(
                configuration_class=MMDetectionConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    @property
    def num_classes(self) -> int:
        return self.mapper.num_classes

    def get_classes_id_dict(self) -> Dict[int, str]:
        return self.mapper.annotation_class_id_to_model_class_name_map

    def __decode_mmdet_result(self, model_result: Any) -> List[Segmentation]:
        """
        Decode output of an object detection model from mmdetection

        Args:
            model_result: The result that the model has predicted

        Returns:
            The model_result as list of bounding boxes in MLCVZoo format
        """

        segmentations: List[Segmentation] = []

        if isinstance(model_result, dict):
            # Have a shape of (IMAGE_HEIGHT, IMAGE_WIDTH) with each pixel
            # stating the class of the segmentation
            pan_results = model_result["pan_results"]
            # Get the classes that are contained in this panoptic segmentation
            valid_indices = np.unique(pan_results)[::-1]
            # Since the panoptic result has an INSTANCE_OFFSET, we need to make
            # sure not to get the class-id which is equal to the number of classes
            legal_indices = valid_indices != self.num_classes
            valid_indices = valid_indices[legal_indices]
            pan_class_ids = np.array(
                [class_id % INSTANCE_OFFSET for class_id in valid_indices],
                dtype=np.int64,
            )
            # Using [None] index to match the shapes:
            # pan_results (H, W) => (1, H, W)
            # valid_indices (N) => (N, 1, 1)
            # panoptic_segmentations => (N, H, W) each dimension corresponds to a boolean mask
            #                                     for the specific 'valid' class
            panoptic_segmentations = pan_results[None] == valid_indices[:, None, None]

            for panoptic_segmentation, class_id in zip(
                panoptic_segmentations, pan_class_ids
            ):
                score = 1.0

                contours, with_hole = bitmap_to_polygon(panoptic_segmentation)

                segmentations.append(
                    Segmentation(
                        class_identifier=ClassIdentifier(
                            class_id=class_id,
                            class_name=self.mapper.map_annotation_class_id_to_model_class_name(
                                class_id=class_id
                            ),
                        ),
                        score=score,
                        # For now, we only take the first contour and don't expect
                        # segmentations to be split into multiple parts
                        polygon=cast(PolygonType, contours[0]),
                        difficult=False,
                        occluded=False,
                        content="",
                        box=None,
                    )
                )
        else:
            bbox_result, segm_result = model_result
            if isinstance(segm_result, tuple):
                segm_result = segm_result[0]

            np_bounding_boxes = np.vstack(bbox_result)

            # Create numpy array containing all class ids
            class_id_list = []
            for index, box in enumerate(bbox_result):
                class_id_list.append(np.full(box.shape[0], index, dtype=np.int32))
            np_class_id_array = np.concatenate(class_id_list)

            # Get relevant indices that do match a given threshold
            np_scores = np_bounding_boxes[:, -1]
            valid_indices = (
                np_scores > self.configuration.inference_config.score_threshold
            )

            # Filter results according to the determined valid indices
            np_bounding_boxes = np_bounding_boxes[valid_indices, :]
            np_class_id_array = np_class_id_array[valid_indices]
            np_scores = np_scores[valid_indices]

            mmdet_segmentations = mmcv.concat_list(segm_result)
            if isinstance(mmdet_segmentations[0], torch.Tensor):
                mmdet_segmentations = (
                    torch.stack(mmdet_segmentations, dim=0).detach().cpu().numpy()
                )
            else:
                mmdet_segmentations = np.stack(mmdet_segmentations, axis=0)

            mmdet_segmentations = mmdet_segmentations[valid_indices, ...]

            for i, (bbox, mmdet_segmentation, class_id, score) in enumerate(
                zip(
                    np_bounding_boxes, mmdet_segmentations, np_class_id_array, np_scores
                )
            ):
                contours, with_hole = bitmap_to_polygon(mmdet_segmentation)

                bbox_int = bbox.astype(np.int32)
                # TODO: Multiple class-identifiers
                segmentations.append(
                    Segmentation(
                        class_identifier=ClassIdentifier(
                            class_id=class_id,
                            class_name=self.mapper.map_annotation_class_id_to_model_class_name(
                                class_id=class_id
                            ),
                        ),
                        score=score,
                        # For now, we only take the first contour and don't expect
                        # segmentations to be split into multiple parts
                        polygon=cast(PolygonType, contours[0]),
                        difficult=False,
                        occluded=False,
                        content="",
                        box=Box.init_format_based(
                            box_format=ObjectDetectionBBoxFormats.XYXY,
                            box_list=(bbox_int[0:4]),
                        ),
                    )
                )

        return segmentations

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[Segmentation]]:
        """
        Predicts objects for given data_item

        Args:
            data_item: Object on which a prediction is to be executed

        Returns:
            TODO
        """

        if self.net is None:
            raise ValueError(
                "MMDetectionModel is not initialized for inference! "
                "Please set the parameter 'init_for_inference=True'"
            )

        result = inference_detector(model=self.net, imgs=data_item)

        segmentations: List[Segmentation] = self.__decode_mmdet_result(
            model_result=result
        )

        return data_item, segmentations
