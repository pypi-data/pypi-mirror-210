import deepomatic.oef.protos.dataoperation_pb2 as dop

from .helpers.common import is_true
from .helpers.controls import DisplayCondition, Title, Text, ModelControl, SelectControl, SelectOption, InputControl, ToggleControl, ListControl
from .helpers.form import Form, MainForm, VIEW_TYPE_TAG
from .helpers.tags import Backend, ViewType


# Define here the models enabled in Vesta
# For CLA and TAG view types
enabled_classification_models = [
    'efficientnet_b0',
    'efficientnet_b1',
    'efficientnet_b2',
    'efficientnet_b3',
    'efficientnet_b4',
    'efficientnet_b5',
    'efficientnet_b6',
    'inception_resnet_v2',
    'inception_v1',
    'inception_v2',
    'inception_v3',
    'inception_v4',
    'resnet_101_v1',
    'resnet_152_v1',
    'resnet_50_v1',
    'mobilenet_v1',
    'mobilenet_v2',
    'vgg_16',
    # VGG 19 is disabled while we solve memory issues with inference
    # 'vgg_19',
]

# For DET view type
enabled_detection_models = [
    'efficientdet_d0.efficientnet_b0',
    'efficientdet_d1.efficientnet_b1',
    'efficientdet_d2.efficientnet_b2',
    'efficientdet_d3.efficientnet_b3',
    'efficientdet_d4.efficientnet_b4',
    'efficientdet_d5.efficientnet_b5',
    'faster_rcnn.resnet_101_v1',
    'faster_rcnn.resnet_50_v1',
    'ssd.inception_v2',
    'ssd.mobilenet_v1',
    'ssd.mobilenet_v2',
    'ssd_lite.mobilenet_v2',
    'yolo_v2.darknet_19',
    'yolo_v3.darknet_53',
    'yolo_v3_spp.darknet_53',
]


###############################################################################

form_parameters = {
    ViewType.CLASSIFICATION: (
        'image_classification.pretraining_natural_rgb.softmax.',
        enabled_classification_models,
        'efficientnet_b0'),

    ViewType.TAGGING: (
        'image_classification.pretraining_natural_rgb.sigmoid.',
        enabled_classification_models,
        'efficientnet_b0'),

    ViewType.DETECTION: (
        'image_detection.pretraining_natural_rgb.',
        enabled_detection_models,
        'efficientdet_d0.efficientnet_b0'),
}

SUBSECTION_LEFT_OFFSET = 20


###############################################################################

FORM = MainForm(form_parameters)


def num_train_steps_default_value(model_key, model, backend):
    """
    Yolo models have a large batch size (64) versus Tensorflow models (24 for SSD).
    To make training times comparable, we use a lower default number of iteration for
    Yolo.
    TODO: normalize batch sizes (64 in Yolo, 24 in TF detection) to make this comparable
    Args:
        model_key (str): the model key as in model_list.py
        model (ModelArguments): the corresponding ModelArguments instance
        backend (Backend): An instance of Backend
    Return:
        num_train_steps (int): the number of default training steps.
    """
    if backend == Backend.TENSORFLOW:
        return 20000
    elif backend == Backend.KERAS:
        return 20000
    elif backend == Backend.DARKNET:
        return 5000
    else:
        raise Exception('Unimplemented backend: {}'.format(backend))


only_for_tf_and_keras = DisplayCondition('backend', ['tensorflow', 'keras'])
only_keras = DisplayCondition('backend', ['keras'])
only_tf = DisplayCondition('backend', ['tensorflow'])

view_classif_tagging = DisplayCondition(VIEW_TYPE_TAG, [ViewType.CLASSIFICATION.value, ViewType.TAGGING.value])
view_detection = DisplayCondition(VIEW_TYPE_TAG, [ViewType.DETECTION.value])


# Training options
FORM.append(Title("Training options"))
# Architecture
FORM.append(ModelControl('model', "Choose your architecture:"))
# Number of train steps
FORM.append(
    InputControl(
        'trainer.num_train_steps',
        "The number of iterations:",
        min_value=10,
        max_value=10000000,
        increment_value=1000,
        # Callable default value: the value depends on the model
        default_value=num_train_steps_default_value
    )
)

# Optimizer options
FORM.append(
    Form()
    .append(Title("Optimizer options"))
    .append(
        # Optimizer choice
        SelectControl(
            'trainer.optimizer.optimizer',
            "Choose an optimizer:",
            [
                SelectOption('momentum_optimizer', 'Momentum Optimizer'),
                SelectOption('rms_prop_optimizer', 'RMS Prop Optimizer'),
                SelectOption('nadam_optimizer', 'NADAM Optimizer', display_ifs=[only_keras]),
                SelectOption('adam_optimizer', 'ADAM Optimizer', display_ifs=[only_for_tf_and_keras]),
                SelectOption('rectified_adam_optimizer', 'Rectified ADAM Optimizer', display_ifs=[only_keras]),
                SelectOption('yogi_optimizer', 'YOGI Optimizer', display_ifs=[only_keras]),
            ],
            display_ifs=[only_for_tf_and_keras]
        )
    )
    .append(
        # Learning rate
        InputControl(
            'trainer.initial_learning_rate',
            "Initial learning rate:",
            min_value=0,
            max_value=10,
            increment_value=0.00001
        )
    )
)

# Resize options
FORM.append(
    Form()
    .append(Title("Resizer image options"))
    .append(
        SelectControl(
            '@backbone.input.image_resizer.image_resizer_oneof',
            "Choose an image resizer type:",
            [
                SelectOption('fixed_shape_resizer', 'Fixed Shape Resizer'),
                SelectOption('keep_aspect_ratio_resizer', 'Keep Aspect Ratio Resizer', display_ifs=[only_for_tf_and_keras])
            ],
        )
    )
    .append(
        # Width/Height (only visible if Fixed Shape Resizer is selected)
        Form(
            padding_left=SUBSECTION_LEFT_OFFSET,
            display_ifs=[DisplayCondition('@backbone.input.image_resizer.image_resizer_oneof', ['fixed_shape_resizer'])]
        ).append(
            InputControl(
                '@backbone.input.image_resizer.fixed_shape_resizer.width',
                "Image width in pixels:",
                min_value=0,
                max_value=10000,
                increment_value=16
            )
        ).append(
            InputControl(
                '@backbone.input.image_resizer.fixed_shape_resizer.height',
                "Image height in pixels:",
                min_value=0,
                max_value=10000,
                increment_value=16
            )
        )
    )
    .append(
        # Image maximum (only visible if Keep Aspect Ratio Resizer is selected)
        Form(
            padding_left=SUBSECTION_LEFT_OFFSET,
            display_ifs=[DisplayCondition('@backbone.input.image_resizer.image_resizer_oneof', ['keep_aspect_ratio_resizer'])]
        ).append(
            InputControl(
                '@backbone.input.image_resizer.keep_aspect_ratio_resizer.max_dimension',
                "Image maximum dimension in pixels:",
                min_value=0,
                max_value=10000,
                increment_value=1,
            )
        )
    )
)


def class_balancing_parser(value):
    if is_true(value):
        return {'dataset': {'operations': [dop.DataOperation(loss_based_balancing=dop.LossBasedBalancing())]}}
    else:
        return {}


# Dataset options
FORM.append(Title("Dataset options"))
FORM.append(ToggleControl('balance', "Class balancing", default_value=False, parser_function=class_balancing_parser))
FORM.append(
    InputControl(
        'dataset.margin_crop',
        "Extra margin to take before cropping example (in percent of the minimum dimension):",
        min_value=0,
        max_value=1,
        increment_value=0.01,
        default_value=0,
        percent=True
    )
)


def make_form(preprocessing_step):
    return Form(
        padding_left=0,
        display_ifs=[DisplayCondition('preprocessing_step', [preprocessing_step])]
    )


FORM.append(Title("Data augmentation", display_ifs=[only_for_tf_and_keras]))
data_augmentation_list = (
    ListControl(
        '@backbone.input.data_augmentation_options',
        "List of data augmentation algorithms which will be applied:",
        Form()
        .append(
            SelectControl(
                'preprocessing_step',
                "Preprocessing type:",
                [
                    SelectOption('random_horizontal_flip', 'Horizontal Flips'),
                    SelectOption('random_vertical_flip', 'Vertical Flips'),
                    SelectOption('random_crop_image', 'Random Crops'),
                    SelectOption('random_rotation90', '90° Rotations'),
                    SelectOption('random_adjust_brightness', 'Modify Brightness'),
                    SelectOption('random_adjust_contrast', 'Modify Contrast'),
                    SelectOption('random_patch_gaussian', 'Add Gaussian Noise'),
                    SelectOption('autoaugment_image', 'Auto Augment'),
                ],
            )
        )
        .append(
            make_form('random_horizontal_flip')
            .append(Text(r"Randomly flips the image horizontally with 50% chance."))
        )
        .append(
            make_form('random_vertical_flip')
            .append(Text(r"Randomly flips the image vertically with 50% chance."))
        )
        .append(
            make_form('random_crop_image')
            .append(Text("Randomly crops the image into a smaller one."))
            .append(
                InputControl(
                    'random_crop_image.min_aspect_ratio',
                    "Minimum aspect ratio of the crop:",
                    min_value=0,
                    max_value=10,
                    increment_value=0.1,
                    default_value=0.75,
                )
            ).append(
                InputControl(
                    'random_crop_image.max_aspect_ratio',
                    "Maximum aspect ratio of the crop:",
                    min_value=0,
                    max_value=10,
                    increment_value=0.1,
                    default_value=1.33,
                )
            )
            .append(
                InputControl(
                    'random_crop_image.min_area',
                    "Minimum area IoU of the cropped image wrt. the orginal image:",
                    min_value=0.1,
                    max_value=1,
                    increment_value=0.1,
                    default_value=0.5,
                )
            )
            .append(
                InputControl(
                    'random_crop_image.max_area',
                    "Maximum area IoU of the cropped image wrt. the orginal image:",
                    min_value=0.1,
                    max_value=1,
                    increment_value=0.1,
                    default_value=1,
                )
            )
        )
        .append(
            make_form('random_rotation90')
            .append(Text(r"Randomly rotates the image by 90° counter-clockwise with 50% chance. Combine it with 'Random Horizontal Flip' and 'Random Vertical Flip' to get rotations and symetries in all directions."))
        )
        .append(
            make_form('random_adjust_brightness')
            .append(Text("Randomly changes image brightness by adding a single random number uniformly sampled from [-max_delta, max_delta] to all pixel RGB channels. Image outputs will be saturated between 0 and 1."))
            .append(
                InputControl(
                    'random_adjust_brightness.max_delta',
                    "Maximum delta:",
                    min_value=0,
                    max_value=1,
                    increment_value=0.1,
                    default_value=0.05,
                )
            )
        )
        .append(
            make_form('random_adjust_contrast')
            .append(Text("Randomly scales contrast by a value between [min_delta, max_delta]. For each RGB channel, this operation computes the mean of the image pixels in the channel and then adjusts each component x of each pixel to '(x - mean) * contrast_factor + mean' with a single 'contrast_factor' uniformly sampled from [min_delta, max_delta] for the whole image."))
            .append(
                InputControl(
                    'random_adjust_contrast.min_delta',
                    "Minimum delta:",
                    min_value=0.5,
                    max_value=1,
                    increment_value=0.1,
                    default_value=0.8,
                )
            )
            .append(
                InputControl(
                    'random_adjust_contrast.max_delta',
                    "Maximum delta:",
                    min_value=1,
                    max_value=2,
                    increment_value=0.1,
                    default_value=1.25,
                )
            )
        )
        .append(
            make_form('random_patch_gaussian')
            .append(Text("Randomly modify a patch of the image by adding gaussian noise to the image pixels normalized between 0 and 1."))
            .append(
                InputControl(
                    'random_patch_gaussian.max_gaussian_stddev',
                    "Maximum standard deviation of the noise:",
                    min_value=0,
                    max_value=2,
                    increment_value=0.1,
                    default_value=0.05,
                )
            )
        )
        .append(
            make_form('autoaugment_image')
            .append(Text("A mix of random image translations, color histogram equilizations, \"graying\" patches of the image, sharpness adjustments, image shearing, image rotating and color balance adjustments."))

            .append(
                Text(
                    "Optimized on COCO, reference: https://arxiv.org/pdf/1906.11172.pdf",
                    display_ifs=[view_detection]
                )
            )
            .append(
                Text(
                    "Optimized on ImageNet, reference: https://arxiv.org/pdf/1805.09501.pdf",
                    display_ifs=[view_classif_tagging]
                )
            )
            .append(
                SelectControl(
                    'autoaugment_image.policy_name',
                    "Choose a policy version:",
                    [
                        SelectOption('v1', 'More color & BBoxes vertical translate transformations', display_ifs=[view_detection]),
                        SelectOption('v3', 'More contrast & vertical translate transformations', display_ifs=[view_detection]),
                        SelectOption('v4', 'Original AutoAugment policy', display_ifs=[view_classif_tagging]),
                    ],
                    property_is_a_oneof=False
                )
            )
            .append(Text("Warning: you may want to disable other data augmentations to avoid interfering."))
        ),
        display_ifs=[only_for_tf_and_keras]
    )
)
FORM.append(data_augmentation_list)
